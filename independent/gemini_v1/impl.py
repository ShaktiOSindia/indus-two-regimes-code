"""Independent implementation of the frozen measurement specification (Roadmap C1).
Written independently by Gemini CLI from SPEC_decision2_DRAFT.md, PREREG_chronology.md,
and area_values_ending_dash.txt.
"""
import collections
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # deposit root
INPUT_CSV = os.path.join(BASE_DIR, "data", "input.csv")  # deposit: the reader places the pinned file here
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "output.json")
EXPECTED_SHA = "c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98"
MARKS = {'+', '[', ']'}


def verify_input_sha(path):
    with open(path, "rb") as f:
        data = f.read()
    h = hashlib.sha256(data).hexdigest()
    if h != EXPECTED_SHA:
        sys.exit(f"Input file SHA-256 mismatch! Got {h}, expected {EXPECTED_SHA}")
    return data


def is_missing(val):
    if not val:
        return True
    c = val.replace('-', '').replace('?', '').replace(' ', '')
    return c == ''


def calc_p5_p95(draws):
    s = sorted(draws)
    n = len(s)
    p5 = s[math.floor(0.05 * (n - 1))]
    p95 = s[math.floor(0.95 * (n - 1))]
    return p5, p95


def serialize_key(key):
    right_mark, lines_ro, left_mark = key
    return right_mark + "|" + "/".join("-".join(line) for line in lines_ro) + "|" + left_mark


def parse_row(row, row_idx):
    s = row['text'].strip()
    left_mark = s[0] if s and s[0] in MARKS else ""
    s_core = s[1:] if left_mark else s
    right_mark = s_core[-1] if s_core and s_core[-1] in MARKS else ""
    core = s_core[:-1] if right_mark else s_core

    if '+' in core:
        sys.exit(f"Core contains '+': row {row['id']}")

    lines_raw = core.split('/')
    is_malformed = False
    stored_lines = []
    all_tokens = []
    for l_str in lines_raw:
        toks = l_str.split('-')
        for t in toks:
            if len(t) != 3 or not t.isdigit():
                is_malformed = True
                break
        if is_malformed:
            break
        stored_lines.append(toks)
        all_tokens.extend(toks)

    if is_malformed:
        return None

    # Legible tokens: any other token != '000' and != '999'
    legible_tokens = [t for t in all_tokens if t not in ('000', '999')]

    # Reading order (R1): lines reversed, tokens in each line reversed
    # Reading start = stored right end; reading end = stored left end
    lines_ro = tuple(tuple(t for t in reversed(l) if t != '999') for l in reversed(stored_lines))
    # Key = (stored right mark, tuple of lines in reading order with 999 removed and 000 kept, stored left mark)
    key = (right_mark, lines_ro, left_mark)
    ser = right_mark + "|" + "/".join("-".join(line) for line in lines_ro) + "|" + left_mark

    # Runs for pairs, triples, entropy (Section 4)
    # A run is a maximal sequence of legible signs within one line, in reading order; 000, 999 and line break end it.
    runs = []
    is_bus = (row['dir.'].strip() == 'BUS')
    has_slash = ('/' in row['text'])
    bus_no_slash = is_bus and not has_slash

    if not bus_no_slash:
        for l in reversed(stored_lines):
            curr_run = []
            for t in reversed(l):
                if t in ('000', '999'):
                    if curr_run:
                        runs.append(tuple(curr_run))
                        curr_run = []
                else:
                    curr_run.append(t)
            if curr_run:
                runs.append(tuple(curr_run))

    # Find-spots (Section 6)
    site = row['site'].strip()
    area = row['area-section'].strip()
    if is_missing(area) or (area.endswith('-') and 'trench' not in area.lower()):
        findspot_d2a = ("row", row_idx)
    else:
        findspot_d2a = (site, area)

    if findspot_d2a[0] == "row":
        findspot_d2b = findspot_d2a
    else:
        rg = "" if is_missing(row['room-grid'].strip()) else row['room-grid'].strip()
        dp = "" if is_missing(row['depth'].strip()) else row['depth'].strip()
        findspot_d2b = (site, area, rg, dp)

    # First and last token in reading order (Section 5)
    # Single-line texts only: no '/' in code and dir. not BUS
    single_line = (not has_slash) and (not is_bus)
    reading_initial_tok = None
    reading_final_tok = None
    if single_line and stored_lines:
        # stored line has tokens in stored order (left to right)
        # reading start = stored right end = stored_lines[0][-1]
        # reading end = stored left end = stored_lines[0][0]
        reading_initial_tok = stored_lines[0][-1]
        reading_final_tok = stored_lines[0][0]

    return {
        "id": row['id'].strip(),
        "row_index": row_idx,
        "type": row['type'].strip(),
        "site": site,
        "complete": row['complete'].strip(),
        "dir": row['dir.'].strip(),
        "raw_text": row['text'].strip(),
        "left_mark": left_mark,
        "right_mark": right_mark,
        "stored_lines": stored_lines,
        "all_tokens": all_tokens,
        "legible_tokens": legible_tokens,
        "legible_len": len(legible_tokens),
        "key": key,
        "serialization": ser,
        "runs": runs,
        "findspot_d2a": findspot_d2a,
        "findspot_d2b": findspot_d2b,
        "single_line": single_line,
        "reading_initial_tok": reading_initial_tok,
        "reading_final_tok": reading_final_tok,
        "object_id": row['id'].strip().rsplit('.', 1)[0],
        "phase": row['phase'].strip(),
        "area_section": area,
        "bus_no_slash": bus_no_slash
    }


def deduplicate(texts, variant):
    if variant == "D0":
        return texts
    seen = {}
    for r in texts:
        if variant == "D1":
            k = (r['site'], r['type'], r['raw_text'])
        elif variant == "D2a":
            k = (r['site'], r['type'], r['raw_text'], r['findspot_d2a'])
        elif variant == "D2b":
            k = (r['site'], r['type'], r['raw_text'], r['findspot_d2b'])
        else:
            raise ValueError(f"Unknown variant: {variant}")
        if k not in seen:
            seen[k] = r
    # Row index order preserved
    return sorted(seen.values(), key=lambda r: r['row_index'])


def top10_and_repeat_share(texts):
    n = len(texts)
    if n == 0:
        return 0.0, [], 0.0
    counts = collections.Counter(r['key'] for r in texts)
    ser_map = {r['key']: r['serialization'] for r in texts}
    ordered = sorted(counts.keys(), key=lambda k: (-counts[k], ser_map[k]))
    top10_keys = ordered[:min(10, len(ordered))]
    cov10 = 100.0 * sum(counts[k] for k in top10_keys) / n
    top10_ser = [ser_map[k] for k in top10_keys]
    repeat_share = 100.0 * sum(c for c in counts.values() if c >= 2) / n
    return cov10, top10_ser, repeat_share


def compute_h3(texts):
    # Runs over eligible texts
    trigrams = collections.Counter()
    contexts = collections.Counter()
    for r in texts:
        for run in r['runs']:
            if len(run) >= 3:
                for i in range(len(run) - 2):
                    t = (run[i], run[i+1], run[i+2])
                    x = (run[i], run[i+1])
                    trigrams[t] += 1
                    contexts[x] += 1
    N = sum(trigrams.values())
    if N == 0:
        return {"plugin": None, "mm": None, "n_tri": 0, "k_tri": 0, "k_ctx": 0, "ktri_over_n": 0.0}
    k_tri = len(trigrams)
    k_ctx = len(contexts)
    h3_plug = -sum((c / N) * math.log2(c / contexts[(t[0], t[1])]) for t, c in trigrams.items())
    mm_h3 = h3_plug + (k_tri - k_ctx) / (2.0 * N * math.log(2))
    ktri_over_n = 100.0 * k_tri / N
    return {
        "plugin": h3_plug,
        "mm": mm_h3,
        "n_tri": N,
        "k_tri": k_tri,
        "k_ctx": k_ctx,
        "ktri_over_n": ktri_over_n
    }


def main():
    raw_bytes = verify_input_sha(INPUT_CSV)
    reader = list(csv.DictReader(raw_bytes.decode('utf-8-sig').splitlines()))
    rows_total = len(reader)

    malformed_ids = []
    analyzable_rows = []
    no_legible_sign_rows = []
    bus_without_slash_rows = []

    for i, r in enumerate(reader):
        res = parse_row(r, i)
        if res is None:
            malformed_ids.append(r['id'].strip())
        else:
            if res['bus_no_slash']:
                bus_without_slash_rows.append(res['id'])
            if res['legible_len'] == 0:
                no_legible_sign_rows.append(res['id'])
            else:
                analyzable_rows.append(res)

    analyzable_by_type = dict(collections.Counter(r['type'] for r in analyzable_rows))

    # Helper filters
    def get_population(cls, pop):
        res = [r for r in analyzable_rows if r['type'] == cls]
        if pop == "complete":
            res = [r for r in res if r['complete'] == 'Y']
        return res

    def get_multisign(cls, pop):
        return [r for r in get_population(cls, pop) if r['legible_len'] >= 2]

    multisign = {}
    for c in ("TAB:I", "SEAL:S"):
        for pop in ("complete", "all"):
            multisign[f"multisign.{c}.{pop}"] = len(get_multisign(c, pop))

    output = {}

    # Part A. Counts
    output["rows_total"] = rows_total
    output["malformed_ids"] = malformed_ids
    output["analyzable_rows"] = len(analyzable_rows)
    output["no_legible_sign_rows"] = len(no_legible_sign_rows)
    output["analyzable_by_type"] = analyzable_by_type
    output["bus_without_slash_rows"] = len(bus_without_slash_rows)
    output.update(multisign)

    # Part B. Whole-text measures
    variants = ("D0", "D1", "D2a", "D2b")
    for c in ("TAB:I", "SEAL:S"):
        for pop in ("complete", "all"):
            pop_texts = get_multisign(c, pop)
            for v in variants:
                v_texts = deduplicate(pop_texts, v)
                cov10, top10_ser, rep_share = top10_and_repeat_share(v_texts)
                output[f"n.{c}.{pop}.{v}"] = len(v_texts)
                output[f"cov10.{c}.{pop}.{v}"] = cov10
                output[f"top10keys.{c}.{pop}.{v}"] = top10_ser
                output[f"repeat_share.{c}.{pop}.{v}"] = rep_share

            # Object rows (section 3), D0 only
            # (a) share of objects carrying at least one of the class's top-10 keys
            # top-10 keys learned on the side-level population (D0)
            d0_top10_set = set(output[f"top10keys.{c}.{pop}.D0"])
            objects_map = collections.defaultdict(list)
            for r in pop_texts:
                objects_map[r['object_id']].append(r)
            total_objs = len(objects_map)
            objs_with_top10 = sum(1 for sides in objects_map.values() if any(s['serialization'] in d0_top10_set for s in sides))
            obj_share_top10 = 100.0 * objs_with_top10 / total_objs if total_objs > 0 else 0.0
            output[f"object_top10_share.{c}.{pop}"] = obj_share_top10

            # (b) whole-object identity
            obj_keys = [tuple(sorted(s['serialization'] for s in sides)) for sides in objects_map.values()]
            obj_counts = collections.Counter(obj_keys)
            ordered_obj_keys = sorted(obj_counts.keys(), key=lambda k: (-obj_counts[k], k))
            top10_obj_keys = ordered_obj_keys[:min(10, len(ordered_obj_keys))]
            obj_cov10 = 100.0 * sum(obj_counts[k] for k in top10_obj_keys) / total_objs if total_objs > 0 else 0.0
            obj_repeat_share = 100.0 * sum(c for c in obj_counts.values() if c >= 2) / total_objs if total_objs > 0 else 0.0
            output[f"object_identity.{c}.{pop}"] = {
                "n_objects": total_objs,
                "cov10": obj_cov10,
                "repeat_share": obj_repeat_share,
                "top10keys": ["+".join(k) for k in top10_obj_keys]
            }

    # Part C. Draw-based measures (section 7), D0 only
    for pop in ("complete", "all"):
        tab_texts = get_multisign("TAB:I", pop)
        sea_texts = get_multisign("SEAL:S", pop)

        # Matched-N cov10
        rng_mn_cov = random.Random(42)
        n_smaller = min(len(tab_texts), len(sea_texts))
        larger = sea_texts if len(sea_texts) > len(tab_texts) else tab_texts
        smaller = tab_texts if len(sea_texts) > len(tab_texts) else sea_texts
        tab_is_smaller = (len(tab_texts) <= len(sea_texts))

        cov_diffs = []
        for _ in range(200):
            sub = rng_mn_cov.sample(larger, n_smaller)
            cov_sub, _, _ = top10_and_repeat_share(sub)
            cov_small, _, _ = top10_and_repeat_share(smaller)
            cov_tab = cov_small if tab_is_smaller else cov_sub
            cov_sea = cov_sub if tab_is_smaller else cov_small
            cov_diffs.append(cov_tab - cov_sea)
        p5, p95 = calc_p5_p95(cov_diffs)
        output[f"matched_n.cov10.{pop}"] = {
            "n": n_smaller,
            "mean": sum(cov_diffs) / len(cov_diffs),
            "p5": p5,
            "p95": p95
        }

        # Matched-N repeat_share
        rng_mn_rep = random.Random(42)
        rep_diffs = []
        for _ in range(200):
            sub = rng_mn_rep.sample(larger, n_smaller)
            _, _, rep_sub = top10_and_repeat_share(sub)
            _, _, rep_small = top10_and_repeat_share(smaller)
            rep_tab = rep_small if tab_is_smaller else rep_sub
            rep_sea = rep_sub if tab_is_smaller else rep_small
            rep_diffs.append(rep_tab - rep_sea)
        p5, p95 = calc_p5_p95(rep_diffs)
        output[f"matched_n.repeat_share.{pop}"] = {
            "n": n_smaller,
            "mean": sum(rep_diffs) / len(rep_diffs),
            "p5": p5,
            "p95": p95
        }

        # Find-spot resampling sensitivity interval (clusters = D2a find-spots)
        def get_clusters(texts):
            c_map = collections.defaultdict(list)
            for r in texts:
                c_map[r['findspot_d2a']].append(r)
            # Ordered by first row index, cluster rows in row-index order
            ordered_clusters = sorted(c_map.values(), key=lambda cl: min(r['row_index'] for r in cl))
            return [sorted(cl, key=lambda r: r['row_index']) for cl in ordered_clusters]

        clusters_tab = get_clusters(tab_texts)
        clusters_seal = get_clusters(sea_texts)

        # findspot_interval.cov10
        rng_fs_cov = random.Random(42)
        valid_cov = []
        discarded_cov = 0
        while len(valid_cov) < 200:
            c_tab = rng_fs_cov.choices(clusters_tab, k=len(clusters_tab))
            c_seal = rng_fs_cov.choices(clusters_seal, k=len(clusters_seal))
            r_tab = [r for cl in c_tab for r in cl]
            r_seal = [r for cl in c_seal for r in cl]
            if len(r_tab) < 2 or len(r_seal) < 2:
                discarded_cov += 1
                continue
            n_res = min(len(r_tab), len(r_seal))
            # Subsampling larger class (TAB:I first)
            if len(r_tab) > n_res:
                r_tab = rng_fs_cov.sample(r_tab, n_res)
            if len(r_seal) > n_res:
                r_seal = rng_fs_cov.sample(r_seal, n_res)
            cov_t, _, _ = top10_and_repeat_share(r_tab)
            cov_s, _, _ = top10_and_repeat_share(r_seal)
            valid_cov.append(cov_t - cov_s)
        p5, p95 = calc_p5_p95(valid_cov)
        output[f"findspot_interval.cov10.{pop}"] = {
            "p5": p5,
            "p95": p95,
            "draws_discarded": discarded_cov
        }

        # findspot_interval.repeat_share
        rng_fs_rep = random.Random(42)
        valid_rep = []
        discarded_rep = 0
        while len(valid_rep) < 200:
            c_tab = rng_fs_rep.choices(clusters_tab, k=len(clusters_tab))
            c_seal = rng_fs_rep.choices(clusters_seal, k=len(clusters_seal))
            r_tab = [r for cl in c_tab for r in cl]
            r_seal = [r for cl in c_seal for r in cl]
            if len(r_tab) < 2 or len(r_seal) < 2:
                discarded_rep += 1
                continue
            n_res = min(len(r_tab), len(r_seal))
            if len(r_tab) > n_res:
                r_tab = rng_fs_rep.sample(r_tab, n_res)
            if len(r_seal) > n_res:
                r_seal = rng_fs_rep.sample(r_seal, n_res)
            _, _, rep_t = top10_and_repeat_share(r_tab)
            _, _, rep_s = top10_and_repeat_share(r_seal)
            valid_rep.append(rep_t - rep_s)
        p5, p95 = calc_p5_p95(valid_rep)
        output[f"findspot_interval.repeat_share.{pop}"] = {
            "p5": p5,
            "p95": p95,
            "draws_discarded": discarded_rep
        }

        # H3 per class
        h3_res = {}
        for c in ("TAB:I", "SEAL:S"):
            c_texts = get_population(c, pop)
            h3_res[c] = compute_h3(c_texts)
            output[f"h3.{c}.{pop}"] = h3_res[c]

        # Entropy comparison at matched trigram tokens
        n_tab_tri = h3_res["TAB:I"]["n_tri"]
        n_sea_tri = h3_res["SEAL:S"]["n_tri"]
        if n_tab_tri <= n_sea_tri:
            fixed_class = "TAB:I"
            other_class = "SEAL:S"
            T = n_tab_tri
            fixed_h3_plug = h3_res["TAB:I"]["plugin"]
            fixed_h3_mm = h3_res["TAB:I"]["mm"]
            other_texts = get_population(other_class, pop)
        else:
            fixed_class = "SEAL:S"
            other_class = "TAB:I"
            T = n_sea_tri
            fixed_h3_plug = h3_res["SEAL:S"]["plugin"]
            fixed_h3_mm = h3_res["SEAL:S"]["mm"]
            other_texts = get_population(other_class, pop)

        rng_em = random.Random(42)
        plug_diffs = []
        mm_diffs = []
        achieved_tokens = []
        for _ in range(200):
            shuffled = list(other_texts)
            rng_em.shuffle(shuffled)
            cum_tokens = 0
            taken = []
            for r in shuffled:
                # count trigrams in r
                r_tri = sum(max(0, len(run) - 2) for run in r['runs'])
                taken.append(r)
                cum_tokens += r_tri
                if cum_tokens >= T:
                    break
            h3_taken = compute_h3(taken)
            achieved_tokens.append(cum_tokens)
            if fixed_class == "TAB:I":
                # difference = SEAL:S - TAB:I
                plug_diffs.append(h3_taken["plugin"] - fixed_h3_plug)
                mm_diffs.append(h3_taken["mm"] - fixed_h3_mm)
            else:
                plug_diffs.append(fixed_h3_plug - h3_taken["plugin"])
                mm_diffs.append(fixed_h3_mm - h3_taken["mm"])

        p5_plug, p95_plug = calc_p5_p95(plug_diffs)
        p5_mm, p95_mm = calc_p5_p95(mm_diffs)
        output[f"entropy_matched.{pop}"] = {
            "fixed_class": fixed_class,
            "T": T,
            "plugin_diff_mean": sum(plug_diffs) / len(plug_diffs),
            "plugin_diff_p5": p5_plug,
            "plugin_diff_p95": p95_plug,
            "mm_diff_mean": sum(mm_diffs) / len(mm_diffs),
            "mm_diff_p5": p5_mm,
            "mm_diff_p95": p95_mm,
            "mean_achieved_tokens": sum(achieved_tokens) / len(achieved_tokens)
        }

        # Predictive hold-out for G3, G1, G2
        for g in ("G3", "G1", "G2"):
            rng_ho = random.Random(42)
            for c in ("TAB:I", "SEAL:S"):
                c_texts = get_multisign(c, pop)
                if g == "G3":
                    groups_dict = collections.defaultdict(list)
                    for r in c_texts:
                        groups_dict[r['findspot_d2a']].append(r)
                    canonical_groups = sorted(groups_dict.values(), key=lambda gr: min(r['row_index'] for r in gr))
                elif g == "G1":
                    canonical_groups = [[r] for r in c_texts]
                elif g == "G2":
                    groups_dict = collections.defaultdict(list)
                    for r in c_texts:
                        groups_dict[r['object_id']].append(r)
                    canonical_groups = sorted(groups_dict.values(), key=lambda gr: min(r['row_index'] for r in gr))

                in_list, out_list, ret_list = [], [], []
                for _ in range(200):
                    copy_gr = list(canonical_groups)
                    rng_ho.shuffle(copy_gr)
                    fold1, fold2 = [], []
                    half_len = len(c_texts) / 2
                    for gr in copy_gr:
                        if len(fold1) < half_len:
                            fold1.extend(gr)
                        else:
                            fold2.extend(gr)

                    cov1_in, top10_fold1, _ = top10_and_repeat_share(fold1)
                    top10_set = set(top10_fold1)
                    cov_out = 100.0 * sum(1 for r in fold2 if r['serialization'] in top10_set) / len(fold2) if fold2 else 0.0
                    retained = 100.0 * cov_out / cov1_in if cov1_in > 0 else 0.0

                    in_list.append(cov1_in)
                    out_list.append(cov_out)
                    ret_list.append(retained)

                out_p5, out_p95 = calc_p5_p95(out_list)
                ret_p5, ret_p95 = calc_p5_p95(ret_list)
                output[f"holdout.{g}.{c}.{pop}"] = {
                    "in_mean": sum(in_list) / len(in_list),
                    "out_mean": sum(out_list) / len(out_list),
                    "out_p5": out_p5,
                    "out_p95": out_p95,
                    "retained_mean": sum(ret_list) / len(ret_list),
                    "retained_p5": ret_p5,
                    "retained_p95": ret_p95
                }

        # Synthetic negative control
        # Sign frequencies: all legible signs of all analyzable rows of all classes
        freq = collections.Counter(t for r in analyzable_rows for t in r['legible_tokens'])
        vocab = sorted(freq.keys())
        weights = [freq[v] for v in vocab]
        len_t = [r['legible_len'] for r in tab_texts]
        len_s = [r['legible_len'] for r in sea_texts]
        obs_gap = output[f"cov10.TAB:I.{pop}.D0"] - output[f"cov10.SEAL:S.{pop}.D0"]

        rng_sn = random.Random(42)
        syn_gaps = []
        for _ in range(200):
            # For TAB:I then SEAL:S
            syn_tab = [("", (tuple(rng_sn.choices(vocab, weights=weights, k=L)),), "") for L in len_t]
            syn_sea = [("", (tuple(rng_sn.choices(vocab, weights=weights, k=L)),), "") for L in len_s]

            def syn_cov(keys):
                counts = collections.Counter(keys)
                ordered = sorted(counts.keys(), key=lambda k: (-counts[k], serialize_key(k)))
                top10 = ordered[:min(10, len(ordered))]
                return 100.0 * sum(counts[k] for k in top10) / len(keys)

            gap = syn_cov(syn_tab) - syn_cov(syn_sea)
            syn_gaps.append(gap)

        output[f"synthetic_negative.{pop}"] = {
            "observed_gap": obs_gap,
            "mean_gap": sum(syn_gaps) / len(syn_gaps),
            "max_abs_gap": max(abs(g) for g in syn_gaps)
        }

    # Part D. First and last signs (section 5), D0, every {c} and {pop}
    for c in ("TAB:I", "SEAL:S"):
        for pop in ("complete", "all"):
            pop_texts = get_population(c, pop)
            eligible = [r for r in pop_texts if r['single_line'] and r['left_mark'] == '+' and r['reading_final_tok'] not in ('000', '999')]
            hits = sum(1 for r in eligible if r['reading_final_tok'] == '740')
            n_el = len(eligible)
            rate = 100.0 * hits / n_el if n_el > 0 else None
            output[f"final740.{c}.{pop}"] = {
                "eligible": n_el,
                "hits": hits,
                "rate": rate
            }

    # Part E. Published-work protocols (section 8)
    # EBUDS-like
    ebuds_cands = [r for r in analyzable_rows if r['complete'] == 'Y' and r['single_line'] and (1 <= r['legible_len'] <= 14)]
    ebuds_seen = {}
    for r in ebuds_cands:
        if r['key'] not in ebuds_seen:
            ebuds_seen[r['key']] = r
    ebuds_like_n = len(ebuds_seen)
    full_n = len(analyzable_rows)
    sensitivity_rl_lr_n = sum(1 for r in analyzable_rows if r['dir'] in ('R/L', 'L/R'))
    output["table2_n"] = {
        "ebuds_like": ebuds_like_n,
        "full": full_n,
        "sensitivity_rl_lr": sensitivity_rl_lr_n
    }

    # Yadav 2013
    yadav_pool = [r for r in analyzable_rows if r['legible_len'] >= 2]
    yadav_counts = collections.Counter(r['key'] for r in yadav_pool)
    ser_map_all = {r['key']: r['serialization'] for r in yadav_pool}
    yadav_top4_keys = sorted(yadav_counts.keys(), key=lambda k: (-yadav_counts[k], ser_map_all[k]))[:4]
    yadav_top4_ser = [ser_map_all[k] for k in yadav_top4_keys]
    yadav_top4_set = set(yadav_top4_keys)

    har_tab = [r for r in analyzable_rows if r['type'] == 'TAB:I' and r['site'] == 'Harappa' and r['legible_len'] >= 2]
    yadav_num = sum(1 for r in har_tab if r['key'] in yadav_top4_set)
    yadav_den = len(har_tab)
    output["yadav2013"] = {
        "keys": yadav_top4_ser,
        "numerator": yadav_num,
        "denominator": yadav_den,
        "share": 100.0 * yadav_num / yadav_den if yadav_den > 0 else 0.0
    }

    # Specification grid (144 cells)
    grid_cells = []
    gaps = []
    neg_cells = []
    for keep_000 in (True, False):
        for min_len in (2, 3):
            for sites in (None, ('Harappa',), ('Harappa', 'Mohenjo-daro')):
                for pop in ('all', 'complete'):
                    for tab_cls in (('TAB:I',), ('TAB:I', 'TAB:B')):
                        for top_n in (5, 10, 20):
                            def filt(cls_tuple):
                                res = []
                                for r in analyzable_rows:
                                    if r['type'] not in cls_tuple:
                                        continue
                                    if pop == 'complete' and r['complete'] != 'Y':
                                        continue
                                    if sites is not None and r['site'] not in sites:
                                        continue
                                    if r['legible_len'] < min_len:
                                        continue
                                    res.append(r)
                                return res

                            t_texts = filt(tab_cls)
                            s_texts = filt(('SEAL:S',))

                            if len(t_texts) >= 30 and len(s_texts) >= 30:
                                def grid_cov(texts, n):
                                    # Identity key under keep_000 setting
                                    def custom_key(r):
                                        lines_ro = tuple(tuple(t for t in reversed(l) if t != '999' and (keep_000 or t != '000')) for l in reversed(r['stored_lines']))
                                        ser = r['right_mark'] + "|" + "/".join("-".join(line) for line in lines_ro) + "|" + r['left_mark']
                                        return (r['right_mark'], lines_ro, r['left_mark']), ser

                                    counts = collections.Counter(custom_key(r)[0] for r in texts)
                                    ser_map = {custom_key(r)[0]: custom_key(r)[1] for r in texts}
                                    ordered = sorted(counts.keys(), key=lambda k: (-counts[k], ser_map[k]))
                                    top = ordered[:min(n, len(ordered))]
                                    return 100.0 * sum(counts[k] for k in top) / len(texts)

                                gap = grid_cov(t_texts, top_n) - grid_cov(s_texts, top_n)
                                cell_obj = {
                                    "gate_000": "keep" if keep_000 else "remove",
                                    "min_len": min_len,
                                    "sites": "all" if sites is None else ("Harappa" if len(sites) == 1 else "2-city"),
                                    "population": pop,
                                    "tablet_class": "+".join(tab_cls),
                                    "top_n": top_n,
                                    "n_tablet": len(t_texts),
                                    "n_seal": len(s_texts),
                                    "gap": gap
                                }
                                grid_cells.append(cell_obj)
                                gaps.append(gap)
                                if gap <= 0:
                                    neg_cells.append(cell_obj)

    output["grid"] = {
        "cells": grid_cells,
        "cells_run": len(grid_cells),
        "positive": sum(1 for g in gaps if g > 0),
        "min": min(gaps),
        "median": statistics.median(gaps),
        "max": max(gaps),
        "negative_cells": neg_cells
    }

    # Part F. Seal measures (section 13, entry 13.7)
    for pop in ("complete", "all"):
        g2_cand = [r for r in get_population("SEAL:S", pop) if r['legible_len'] >= 2 and r['single_line'] and r['left_mark'] == '+' and r['reading_final_tok'] not in ('000', '999')]
        all_leg = [t for r in g2_cand for t in r['legible_tokens']]
        final_leg = [r['reading_final_tok'] for r in g2_cand]
        # non-final legible tokens
        other_leg = []
        for r in g2_cand:
            # reading order: lines_ro[0]
            # final token is the first legible token from stored left
            # all other legible tokens in reading order are the rest
            ro_leg = [t for t in reversed(r['stored_lines'][0]) if t not in ('000', '999')]
            other_leg.extend(ro_leg[:-1])

        sh_all = 100.0 * all_leg.count('740') / len(all_leg) if all_leg else 0.0
        sh_fin = 100.0 * final_leg.count('740') / len(final_leg) if final_leg else 0.0
        sh_oth = 100.0 * other_leg.count('740') / len(other_leg) if other_leg else 0.0
        enr = sh_fin / sh_oth if sh_oth > 0 else None
        output[f"g2.{pop}"] = {
            "texts": len(g2_cand),
            "share_all_tokens": sh_all,
            "share_final": sh_fin,
            "share_other": sh_oth,
            "enrichment": enr
        }

    # g3: complete both-end-eligible texts with at least 3 legible signs (SEAL:S)
    g3_cand = [r for r in get_population("SEAL:S", "complete") if r['single_line'] and r['left_mark'] == '+' and r['right_mark'] == '+' and r['reading_initial_tok'] not in ('000', '999') and r['reading_final_tok'] not in ('000', '999') and r['legible_len'] >= 3]
    first_signs = []
    middle_signs = []
    last_signs = []
    for r in g3_cand:
        ro_leg = [t for t in reversed(r['stored_lines'][0]) if t not in ('000', '999')]
        first_signs.append(ro_leg[0])
        middle_signs.extend(ro_leg[1:-1])
        last_signs.append(ro_leg[-1])

    def calc_ent(tokens):
        c = collections.Counter(tokens)
        n = len(tokens)
        k = len(c)
        h = -sum((cnt / n) * math.log2(cnt / n) for cnt in c.values())
        mm = h + (k - 1) / (2.0 * n * math.log(2))
        return {"plugin": h, "mm": mm, "N": n, "K": k}

    f_ent = calc_ent(first_signs)
    m_ent = calc_ent(middle_signs)
    l_ent = calc_ent(last_signs)
    output["g3"] = {
        "n": len(g3_cand),
        "first": f_ent,
        "middle": m_ent,
        "last": l_ent,
        "mm_gap_first_minus_last": f_ent["mm"] - l_ent["mm"]
    }

    # Part G. Chronology test (PREREG_chronology.md, Amendment 1)
    def get_bprime_cell(row, variant):
        if row['site'] != 'Harappa':
            return None
        if not row['area_section'].startswith('F'):
            return None
        phase = row['phase']
        is_tvi = (row['area_section'] == 'FTrench VI')
        stratum = None
        if variant == 'primary':
            if is_tvi and phase == 'Stratum III':
                stratum = 'Stratum IV'
            elif phase in ('Stratum IV', 'Stratum V', 'Stratum VI', 'Stratum VII'):
                stratum = phase
        elif variant == 'sensitivity':
            if is_tvi:
                if phase == 'Stratum III':
                    stratum = 'Stratum IV'
                elif phase == 'Stratum IV':
                    stratum = 'Stratum V'
                elif phase == 'Stratum V':
                    stratum = 'Stratum VI'
            elif phase in ('Stratum IV', 'Stratum V', 'Stratum VI', 'Stratum VII'):
                stratum = phase
        if not stratum:
            return None
        if stratum == 'Stratum IV':
            return 'IV'
        if stratum in ('Stratum V', 'Stratum VI', 'Stratum VII'):
            return 'V-VII'
        return None

    for var in ('primary', 'sensitivity'):
        cell_results = {}
        for cell in ('V-VII', 'IV'):
            tab_all = [r for r in analyzable_rows if r['type'] == 'TAB:I' and r['legible_len'] >= 2 and get_bprime_cell(r, var) == cell]
            seal_all = [r for r in analyzable_rows if r['type'] == 'SEAL:S' and r['legible_len'] >= 2 and get_bprime_cell(r, var) == cell]
            tab_comp = [r for r in tab_all if r['complete'] == 'Y']
            seal_comp = [r for r in seal_all if r['complete'] == 'Y']

            n_tab_all = len(tab_all)
            n_seal_all = len(seal_all)
            n_tab_complete = len(tab_comp)
            n_seal_complete = len(seal_comp)
            tested = (n_tab_all >= 30 and n_seal_all >= 30)

            if tested:
                # matched-N on all texts
                rng_bp = random.Random(42)
                n_match = min(n_tab_all, n_seal_all)
                larger = tab_all if n_tab_all > n_seal_all else seal_all
                smaller = seal_all if n_tab_all > n_seal_all else tab_all
                tab_is_smaller = (n_tab_all <= n_seal_all)

                matched_gaps = []
                for _ in range(200):
                    sub = rng_bp.sample(larger, n_match)
                    cov_small, _, _ = top10_and_repeat_share(smaller)
                    cov_sub, _, _ = top10_and_repeat_share(sub)
                    c_tab = cov_small if tab_is_smaller else cov_sub
                    c_seal = cov_sub if tab_is_smaller else cov_small
                    matched_gaps.append(c_tab - c_seal)

                p5, p95 = calc_p5_p95(matched_gaps)
                criterion_met = (p5 > 0)
                matched_dict = {
                    "mean": sum(matched_gaps) / len(matched_gaps),
                    "p5": p5,
                    "p95": p95
                }

                _, _, rep_tab = top10_and_repeat_share(tab_all)
                _, _, rep_seal = top10_and_repeat_share(seal_all)

                # d2a_matched
                tab_d2a = deduplicate(tab_all, "D2a")
                seal_d2a = deduplicate(seal_all, "D2a")
                n_d2a = min(len(tab_d2a), len(seal_d2a))
                larger_d2a = tab_d2a if len(tab_d2a) > len(seal_d2a) else seal_d2a
                smaller_d2a = seal_d2a if len(tab_d2a) > len(seal_d2a) else tab_d2a
                tab_d2a_is_smaller = (len(tab_d2a) <= len(seal_d2a))

                rng_d2a = random.Random(42)
                d2a_gaps = []
                for _ in range(200):
                    sub = rng_d2a.sample(larger_d2a, n_d2a)
                    cov_small, _, _ = top10_and_repeat_share(smaller_d2a)
                    cov_sub, _, _ = top10_and_repeat_share(sub)
                    c_tab = cov_small if tab_d2a_is_smaller else cov_sub
                    c_seal = cov_sub if tab_d2a_is_smaller else cov_small
                    d2a_gaps.append(c_tab - c_seal)
                p5_d2a, p95_d2a = calc_p5_p95(d2a_gaps)
                d2a_matched_dict = {
                    "mean": sum(d2a_gaps) / len(d2a_gaps),
                    "p5": p5_d2a,
                    "p95": p95_d2a
                }

                # 740 final rates
                def calc_740_rate(texts):
                    el = [r for r in texts if r['single_line'] and r['left_mark'] == '+' and r['reading_final_tok'] not in ('000', '999')]
                    hits = sum(1 for r in el if r['reading_final_tok'] == '740')
                    return 100.0 * hits / len(el) if el else None

                final740_tab = calc_740_rate(tab_all)
                final740_seal = calc_740_rate(seal_all)
            else:
                matched_dict = None
                criterion_met = False
                rep_tab = None
                rep_seal = None
                d2a_matched_dict = None
                final740_tab = None
                final740_seal = None

            cell_obj = {
                "n_tab_all": n_tab_all,
                "n_seal_all": n_seal_all,
                "n_tab_complete": n_tab_complete,
                "n_seal_complete": n_seal_complete,
                "tested": tested,
                "matched": matched_dict,
                "criterion_met": criterion_met,
                "repeat_share_tab": rep_tab,
                "repeat_share_seal": rep_seal,
                "d2a_matched": d2a_matched_dict,
                "final740_tab": final740_tab,
                "final740_seal": final740_seal
            }
            output[f"bprime.{var}.{cell}"] = cell_obj
            cell_results[cell] = cell_obj

        # Outcome
        if not cell_results["V-VII"]["tested"] or not cell_results["IV"]["tested"]:
            outcome = "C"
        else:
            c_v = cell_results["V-VII"]["criterion_met"]
            c_iv = cell_results["IV"]["criterion_met"]
            if c_v and c_iv:
                outcome = "H"
            elif c_v and not c_iv:
                outcome = "P"
            elif not c_v:
                outcome = "F"
            else:
                outcome = "C"
        output[f"bprime.{var}.outcome"] = outcome

    # Write output.json
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, sort_keys=True, indent=1)

    print(f"Wrote {len(output)} keys to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
