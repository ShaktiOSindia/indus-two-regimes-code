"""Independent implementation, part 2: the headline section 13 numbers.
Written independently by Gemini CLI from SPEC_decision2_DRAFT.md, PREREG_R2-2_slot_null.md,
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
import time

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # deposit root
INPUT_CSV = os.path.join(BASE_DIR, "data", "input.csv")  # deposit: the reader places the pinned file here
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "output_v2.json")
EXPECTED_SHA = "c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98"
MARKS = {'+', '[', ']'}
SLOT = {'032', '033', '034'}


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


def top10_and_repeat_share(texts):
    n = len(texts)
    if n == 0:
        return 0.0, [], 0.0
    counts = collections.Counter(r['key'] for r in texts)
    ser_map = {r['key']: r['ser'] for r in texts}
    ordered = sorted(counts.keys(), key=lambda k: (-counts[k], ser_map[k]))
    top10_keys = ordered[:min(10, len(ordered))]
    cov10 = 100.0 * sum(counts[k] for k in top10_keys) / n
    top10_ser = [ser_map[k] for k in top10_keys]
    repeat_share = 100.0 * sum(c for c in counts.values() if c >= 2) / n
    return cov10, top10_ser, repeat_share


def topN_cov(texts, N):
    if not texts:
        return 0.0
    counts = collections.Counter(r['key'] for r in texts)
    ser_map = {r['key']: r['ser'] for r in texts}
    ordered = sorted(counts.keys(), key=lambda k: (-counts[k], ser_map[k]))
    topN_keys = ordered[:min(N, len(ordered))]
    return 100.0 * sum(counts[k] for k in topN_keys) / len(texts)


def compute_h3_and_mm(texts):
    trigrams = []
    contexts = collections.Counter()
    tri_counts = collections.Counter()
    for r in texts:
        for run in r['runs']:
            if len(run) >= 3:
                for i in range(len(run) - 2):
                    tri = (run[i], run[i+1], run[i+2])
                    ctx = (run[i], run[i+1])
                    trigrams.append(tri)
                    contexts[ctx] += 1
                    tri_counts[tri] += 1
    N = len(trigrams)
    if N == 0:
        return None, None, 0, 0
    h3 = 0.0
    for tri, c_t in tri_counts.items():
        c_x = contexts[(tri[0], tri[1])]
        prob_tri = c_t / N
        cond_prob = c_t / c_x
        h3 -= prob_tri * math.log2(cond_prob)
    k_tri = len(tri_counts)
    k_ctx = len(contexts)
    mm_h3 = h3 + (k_tri - k_ctx) / (2.0 * N * math.log(2))
    return h3, mm_h3, N, k_tri


def parse_corpus(csv_path):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    analyzable = []
    for idx, r in enumerate(raw_rows):
        s = r['text'].strip()
        left_mark = s[0] if s and s[0] in MARKS else ""
        s_core = s[1:] if left_mark else s
        right_mark = s_core[-1] if s_core and s_core[-1] in MARKS else ""
        core = s_core[:-1] if right_mark else s_core

        if '+' in core:
            sys.exit(f"Core contains '+': row {r['id']}")

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
            continue

        legible_tokens = [t for t in all_tokens if t not in ('000', '999')]
        if len(legible_tokens) == 0:
            continue

        # Reading order (R1)
        lines_ro = tuple(tuple(t for t in reversed(l) if t != '999') for l in reversed(stored_lines))
        key = (right_mark, lines_ro, left_mark)
        ser = right_mark + "|" + "/".join("-".join(line) for line in lines_ro) + "|" + left_mark
        gated_ro = tuple(t for line in lines_ro for t in line if t != '000')

        # Runs (Section 4, Spec 1)
        is_bus = (r['dir.'].strip() == 'BUS')
        has_slash = ('/' in r['text'])
        bus_no_slash = is_bus and not has_slash

        runs = []
        if not bus_no_slash:
            for l in reversed(stored_lines):
                curr = []
                for t in reversed(l):
                    if t in ('000', '999'):
                        if curr:
                            runs.append(tuple(curr))
                            curr = []
                    else:
                        curr.append(t)
                if curr:
                    runs.append(tuple(curr))

        # Single-line texts (Section 5): no '/' in code AND dir. not BUS
        single_line = (not has_slash) and (not is_bus)
        reading_initial_tok = None
        reading_final_tok = None
        if single_line and stored_lines:
            reading_initial_tok = stored_lines[0][-1]
            reading_final_tok = stored_lines[0][0]

        # Find-spots D2a (Section 6)
        site = r['site'].strip()
        area = r['area-section'].strip()
        if is_missing(area) or (area.endswith('-') and 'trench' not in area.lower()):
            findspot_d2a = ("row", idx)
        else:
            findspot_d2a = (site, area)

        analyzable.append({
            "id": r['id'].strip(),
            "row_index": idx,
            "type": r['type'].strip(),
            "site": site,
            "complete": r['complete'].strip(),
            "dir": r['dir.'].strip(),
            "left_mark": left_mark,
            "right_mark": right_mark,
            "key": key,
            "ser": ser,
            "gated_ro": gated_ro,
            "legible_len": len(legible_tokens),
            "runs": runs,
            "single_line": single_line,
            "reading_final_tok": reading_final_tok,
            "reading_initial_tok": reading_initial_tok,
            "findspot_d2a": findspot_d2a
        })

    return analyzable


# --- Analysis 13.4: Slot null ---
def compute_13_4(pop_rows):
    # Population as registered: all analyzable TAB:I texts, complete texts beside
    tab_texts = [r for r in pop_rows if r['type'] == 'TAB:I']
    seal_texts = [r for r in pop_rows if r['type'] == 'SEAL:S']

    def calc_t(texts):
        return sum(1 for r in texts if len(set(r['gated_ro']).intersection(SLOT)) >= 2)

    def compute_exact_e(texts):
        by_len = {}
        for r in texts:
            L = len(r['gated_ro'])
            by_len.setdefault(L, []).append(r['gated_ro'])

        E_total = 0.0
        for L, group in by_len.items():
            if L < 2:
                continue
            M = len(group)
            q = []
            Q = []
            for p in range(L):
                col = [t[p] for t in group]
                qp = {s: col.count(s) / M for s in SLOT}
                Qp = sum(qp.values())
                q.append(qp)
                Q.append(Qp)

            prod_no_slot = 1.0
            for p in range(L):
                prod_no_slot *= (1.0 - Q[p])

            sum_single_slot = 0.0
            for s in SLOT:
                prod_s = 1.0
                for p in range(L):
                    prod_s *= (1.0 - Q[p] + q[p][s])
                sum_single_slot += (prod_s - prod_no_slot)

            P_le_1 = prod_no_slot + sum_single_slot
            P_ge_2 = 1.0 - P_le_1
            E_total += M * P_ge_2

        return E_total

    def run_n1_simulation(texts, B=10000, seed=42):
        rng = random.Random(seed)
        by_len = {}
        for r in texts:
            L = len(r['gated_ro'])
            by_len.setdefault(L, []).append(r['gated_ro'])

        sorted_lengths = sorted([L for L in by_len.keys() if L >= 2])
        cols_by_len = {}
        for L in sorted_lengths:
            M = len(by_len[L])
            cols = []
            for p in range(L):
                cols.append([by_len[L][i][p] for i in range(M)])
            cols_by_len[L] = cols

        T_null_list = []
        for _ in range(B):
            T_draw = 0
            for L in sorted_lengths:
                M = len(by_len[L])
                shuffled_cols = []
                for p in range(L):
                    c = list(cols_by_len[L][p])
                    rng.shuffle(c)
                    shuffled_cols.append(c)

                for i in range(M):
                    signs_present = set()
                    for p in range(L):
                        s = shuffled_cols[p][i]
                        if s in SLOT:
                            signs_present.add(s)
                    if len(signs_present) >= 2:
                        T_draw += 1
            T_null_list.append(T_draw)
        return T_null_list

    # TAB:I
    t_obs_tab = calc_t(tab_texts)
    e_exact_tab = compute_exact_e(tab_texts)
    t_null_tab = run_n1_simulation(tab_texts, B=10000, seed=42)
    mc_mean_tab = sum(t_null_tab) / len(t_null_tab)
    mc_var_tab = sum((x - mc_mean_tab)**2 for x in t_null_tab) / (len(t_null_tab) - 1)
    mc_se_tab = math.sqrt(mc_var_tab) / math.sqrt(len(t_null_tab))
    p_tab = (1 + sum(1 for x in t_null_tab if x <= t_obs_tab)) / (1 + len(t_null_tab))
    outcome_tab = "A" if p_tab <= 0.01 else "B"

    # G5 independence expectation
    n_tab_total = len(tab_texts)
    n_032 = sum(1 for r in tab_texts if '032' in r['gated_ro'])
    n_033 = sum(1 for r in tab_texts if '033' in r['gated_ro'])
    n_034 = sum(1 for r in tab_texts if '034' in r['gated_ro'])
    g5_tab = (n_032 * n_033 + n_032 * n_034 + n_033 * n_034) / n_tab_total if n_tab_total > 0 else 0.0

    # SEAL:S control
    t_obs_seal = calc_t(seal_texts)
    e_exact_seal = compute_exact_e(seal_texts)
    t_null_seal = run_n1_simulation(seal_texts, B=10000, seed=42)
    mc_mean_seal = sum(t_null_seal) / len(t_null_seal)
    mc_var_seal = sum((x - mc_mean_seal)**2 for x in t_null_seal) / (len(t_null_seal) - 1)
    mc_se_seal = math.sqrt(mc_var_seal) / math.sqrt(len(t_null_seal))
    p_seal = (1 + sum(1 for x in t_null_seal if x <= t_obs_seal)) / (1 + len(t_null_seal))
    exclusivity_beyond_position = (p_seal <= 0.01)

    return {
        "TAB:I": {
            "T_obs": t_obs_tab,
            "E_exact": e_exact_tab,
            "mc_mean": mc_mean_tab,
            "mc_se": mc_se_tab,
            "p": p_tab,
            "draws": 10000,
            "outcome": outcome_tab,
            "independence_expectation_G5": g5_tab
        },
        "SEAL:S_control": {
            "T_obs": t_obs_seal,
            "E_exact": e_exact_seal,
            "mc_mean": mc_mean_seal,
            "mc_se": mc_se_seal,
            "p": p_seal,
            "draws": 10000,
            "exclusivity_beyond_position": exclusivity_beyond_position
        }
    }


# --- Analysis 13.6: Reuse at fixed length ---
def compute_13_6(pop_rows):
    res = {}
    for L in (2, 3, 4, 5):
        tab_L = [r for r in pop_rows if r['type'] == 'TAB:I' and r['legible_len'] == L]
        seal_L = [r for r in pop_rows if r['type'] == 'SEAL:S' and r['legible_len'] == L]
        cov_tab, _, _ = top10_and_repeat_share(tab_L)
        cov_seal, _, _ = top10_and_repeat_share(seal_L)
        res[str(L)] = {
            "TAB:I": {
                "N": len(tab_L),
                "cov10": cov_tab
            },
            "SEAL:S": {
                "N": len(seal_L),
                "cov10": cov_seal
            }
        }
    return res


# --- Analysis 13.9: Site control ---
def compute_13_9(pop_rows):
    tab_harappa = [r for r in pop_rows if r['type'] == 'TAB:I' and r['site'] == 'Harappa' and r['legible_len'] >= 2]
    seal_harappa = [r for r in pop_rows if r['type'] == 'SEAL:S' and r['site'] == 'Harappa' and r['legible_len'] >= 2]
    seal_md = [r for r in pop_rows if r['type'] == 'SEAL:S' and r['site'] == 'Mohenjo-daro' and r['legible_len'] >= 2]

    # S4
    def get_group_stats(texts):
        n = len(texts)
        cov10, _, rep = top10_and_repeat_share(texts)
        once_pct = 100.0 - rep
        el = [r for r in texts if r['single_line'] and r['left_mark'] == '+' and r['reading_final_tok'] not in ('000', '999')]
        hits = sum(1 for r in el if r['reading_final_tok'] == '740')
        rate = (100.0 * hits / len(el)) if el else 0.0
        return {
            "N": n,
            "cov10": cov10,
            "once_pct": once_pct,
            "final740": {
                "eligible": len(el),
                "hits": hits,
                "rate": rate
            }
        }

    s4_tab_h = get_group_stats(tab_harappa)
    s4_seal_h = get_group_stats(seal_harappa)
    s4_seal_md = get_group_stats(seal_md)

    # within_Harappa_matched
    n_match = min(len(tab_harappa), len(seal_harappa))
    tab_is_smaller = (len(tab_harappa) <= len(seal_harappa))
    smaller = tab_harappa if tab_is_smaller else seal_harappa
    larger = seal_harappa if tab_is_smaller else tab_harappa

    rng_matched = random.Random(42)
    matched_diffs = []
    for _ in range(200):
        sub = rng_matched.sample(larger, n_match)
        cov_small, _, _ = top10_and_repeat_share(smaller)
        cov_sub, _, _ = top10_and_repeat_share(sub)
        c_tab = cov_small if tab_is_smaller else cov_sub
        c_seal = cov_sub if tab_is_smaller else cov_small
        matched_diffs.append(c_tab - c_seal)

    p5_m, p95_m = calc_p5_p95(matched_diffs)
    within_Harappa_matched = {
        "n": n_match,
        "mean": sum(matched_diffs) / len(matched_diffs),
        "p5": p5_m,
        "p95": p95_m
    }

    # within_Harappa_findspot_interval
    clusters_tab_map = collections.OrderedDict()
    for r in tab_harappa:
        clusters_tab_map.setdefault(r['findspot_d2a'], []).append(r)
    clusters_tab = list(clusters_tab_map.values())

    clusters_seal_map = collections.OrderedDict()
    for r in seal_harappa:
        clusters_seal_map.setdefault(r['findspot_d2a'], []).append(r)
    clusters_seal = list(clusters_seal_map.values())

    rng_interval = random.Random(42)
    interval_diffs = []
    draws_discarded = 0
    while len(interval_diffs) < 200:
        chosen_tab = rng_interval.choices(clusters_tab, k=len(clusters_tab))
        chosen_seal = rng_interval.choices(clusters_seal, k=len(clusters_seal))
        rows_tab = [r for c in chosen_tab for r in c]
        rows_seal = [r for c in chosen_seal for r in c]
        if len(rows_tab) < 2 or len(rows_seal) < 2:
            draws_discarded += 1
            continue
        n_resample = min(len(rows_tab), len(rows_seal))
        if len(rows_tab) > n_resample:
            rows_tab = rng_interval.sample(rows_tab, n_resample)
        if len(rows_seal) > n_resample:
            rows_seal = rng_interval.sample(rows_seal, n_resample)
        cov_t, _, _ = top10_and_repeat_share(rows_tab)
        cov_s, _, _ = top10_and_repeat_share(rows_seal)
        interval_diffs.append(cov_t - cov_s)

    p5_int, p95_int = calc_p5_p95(interval_diffs)
    within_Harappa_findspot_interval = {
        "p5": p5_int,
        "p95": p95_int,
        "draws_discarded": draws_discarded
    }

    s4 = {
        "TAB:I@Harappa": s4_tab_h,
        "SEAL:S@Harappa": s4_seal_h,
        "SEAL:S@Mohenjo-daro": s4_seal_md,
        "within_Harappa_matched": within_Harappa_matched,
        "within_Harappa_findspot_interval": within_Harappa_findspot_interval
    }

    # S6: Harappa, legible lengths 2, 3, 4, cells with >= 15 texts per class
    s6 = {}
    for L in (2, 3, 4):
        tab_L = [r for r in tab_harappa if r['legible_len'] == L]
        seal_L = [r for r in seal_harappa if r['legible_len'] == L]
        n_t = len(tab_L)
        n_s = len(seal_L)
        if n_t >= 15 and n_s >= 15:
            n_sub = min(n_t, n_s)
            rng_s6 = random.Random(42)
            tab_is_smaller_l = (n_t <= n_s)
            diffs_l = []
            tab_covs = []
            seal_covs = []
            for _ in range(200):
                if tab_is_smaller_l:
                    sub_seal = rng_s6.sample(seal_L, n_sub)
                    c_t, _, _ = top10_and_repeat_share(tab_L)
                    c_s, _, _ = top10_and_repeat_share(sub_seal)
                else:
                    sub_tab = rng_s6.sample(tab_L, n_sub)
                    c_t, _, _ = top10_and_repeat_share(sub_tab)
                    c_s, _, _ = top10_and_repeat_share(seal_L)
                diffs_l.append(c_t - c_s)
                tab_covs.append(c_t)
                seal_covs.append(c_s)
            p5_d, p95_d = calc_p5_p95(diffs_l)
            p5_t, p95_t = calc_p5_p95(tab_covs)
            p5_s, p95_s = calc_p5_p95(seal_covs)
            s6[str(L)] = {
                "n": n_sub,
                "n_tab": n_t,
                "n_seal": n_s,
                "diff": {"mean": sum(diffs_l) / 200, "p5": p5_d, "p95": p95_d},
                "tab": {"mean": sum(tab_covs) / 200, "p5": p5_t, "p95": p95_t},
                "seal": {"mean": sum(seal_covs) / 200, "p5": p5_s, "p95": p95_s}
            }

    # S7_bias: TAB:I at Harappa subsampled to 700, 500, 300, 150, 60 (skip sizes > N)
    s7_bias = {}
    for sz in (700, 500, 300, 150, 60):
        if sz <= len(tab_harappa):
            rng_s7 = random.Random(42)
            covs = []
            for _ in range(200):
                sub = rng_s7.sample(tab_harappa, sz)
                c, _, _ = top10_and_repeat_share(sub)
                covs.append(c)
            s7_bias[str(sz)] = sum(covs) / 200

    # S5_estimability: Harappa, lengths 2, 3, 4, 5, per class: texts, n_tri, k_tri, ktri_over_n
    s5_estimability = {}
    for L in (2, 3, 4, 5):
        for cls_name, cls_texts in [("TAB:I", tab_harappa), ("SEAL:S", seal_harappa)]:
            sub_texts = [r for r in cls_texts if r['legible_len'] == L]
            _, _, N_tri, K_tri = compute_h3_and_mm(sub_texts)
            ktri_over_n = (100.0 * K_tri / N_tri) if N_tri > 0 else 0.0
            s5_estimability[f"{L}.{cls_name}"] = {
                "texts": len(sub_texts),
                "n_tri": N_tri,
                "k_tri": K_tri,
                "ktri_over_n": ktri_over_n
            }

    # H3_line_within_Harappa
    h3_tab, mm_tab, N_tri_tab, _ = compute_h3_and_mm(tab_harappa)
    h3_seal, mm_seal, N_tri_seal, _ = compute_h3_and_mm(seal_harappa)

    tab_fewer = (N_tri_tab <= N_tri_seal)
    fixed_class = "TAB:I" if tab_fewer else "SEAL:S"
    T = min(N_tri_tab, N_tri_seal)
    fixed_h3 = h3_tab if tab_fewer else h3_seal
    fixed_mm = mm_tab if tab_fewer else mm_seal
    other_texts = seal_harappa if tab_fewer else tab_harappa

    rng_h3 = random.Random(42)
    plugin_diffs = []
    mm_diffs = []
    achieved_tokens_list = []

    for _ in range(200):
        shuffled = list(other_texts)
        rng_h3.shuffle(shuffled)
        taken = []
        cur_tokens = 0
        for r in shuffled:
            taken.append(r)
            for run in r['runs']:
                if len(run) >= 3:
                    cur_tokens += len(run) - 2
            if cur_tokens >= T:
                break
        h3_draw, mm_draw, ach_tokens, _ = compute_h3_and_mm(taken)
        achieved_tokens_list.append(ach_tokens)
        if tab_fewer:
            # Difference is always SEAL:S - TAB:I
            plugin_diffs.append(h3_draw - fixed_h3)
            mm_diffs.append(mm_draw - fixed_mm)
        else:
            plugin_diffs.append(fixed_h3 - h3_draw)
            mm_diffs.append(fixed_mm - mm_draw)

    p5_p, p95_p = calc_p5_p95(plugin_diffs)
    p5_mm, p95_mm = calc_p5_p95(mm_diffs)

    h3_line = {
        "fixed_class": fixed_class,
        "T": T,
        "plugin_diff_mean": sum(plugin_diffs) / len(plugin_diffs),
        "plugin_diff_p5": p5_p,
        "plugin_diff_p95": p95_p,
        "mm_diff_mean": sum(mm_diffs) / len(mm_diffs),
        "mm_diff_p5": p5_mm,
        "mm_diff_p95": p95_mm,
        "mean_achieved_tokens": sum(achieved_tokens_list) / len(achieved_tokens_list)
    }

    return {
        "S4": s4,
        "S6": s6,
        "S7_bias": s7_bias,
        "S5_estimability": s5_estimability,
        "H3_line_within_Harappa": h3_line
    }


# --- Analysis 13.10: Duplicate-provenance test ---
def compute_13_10(pop_rows, all_analyzable_rows):
    # [M2] per class (TAB:I, SEAL:S; multi-sign)
    def run_m2(texts, seed=42):
        key_to_texts = collections.OrderedDict()
        for r in texts:
            k = r['key']
            key_to_texts.setdefault(k, []).append(r)

        repeated_groups = [g for g in key_to_texts.values() if len(g) >= 2]
        repeated_keys = len(repeated_groups)
        repeat_pairs = sum(len(g) - 1 for g in repeated_groups)

        observed_gaps = []
        group_sizes = []
        for g in repeated_groups:
            idxs = sorted(r['row_index'] for r in g)
            group_sizes.append(len(idxs))
            for i in range(1, len(idxs)):
                observed_gaps.append(idxs[i] - idxs[i-1])

        median_gap_obs = statistics.median(observed_gaps) if observed_gaps else 0.0
        share_le2_obs = 100.0 * sum(1 for x in observed_gaps if x <= 2) / len(observed_gaps) if observed_gaps else 0.0

        rng = random.Random(seed)
        class_row_idxs = [r['row_index'] for r in texts]
        null_gaps = []
        for _ in range(200):
            for k in group_sizes:
                s_idxs = sorted(rng.sample(class_row_idxs, k))
                for i in range(1, len(s_idxs)):
                    null_gaps.append(s_idxs[i] - s_idxs[i-1])

        median_gap_null = statistics.median(null_gaps) if null_gaps else 0.0
        share_le2_null = 100.0 * sum(1 for x in null_gaps if x <= 2) / len(null_gaps) if null_gaps else 0.0

        return {
            "repeated_keys": repeated_keys,
            "repeat_pairs": repeat_pairs,
            "median_gap_observed": median_gap_obs,
            "median_gap_null": median_gap_null,
            "share_gap_le2_observed": share_le2_obs,
            "share_gap_le2_null": share_le2_null
        }

    tab_ms = [r for r in pop_rows if r['type'] == 'TAB:I' and r['legible_len'] >= 2]
    seal_ms = [r for r in pop_rows if r['type'] == 'SEAL:S' and r['legible_len'] >= 2]

    m2_tab = run_m2(tab_ms, seed=42)
    m2_seal = run_m2(seal_ms, seed=42)

    # [M3] collapse, over all analyzable rows:
    # within each (type, key) group in row-index order, a run starts at a row and takes every later row within 2 of that FIRST row;
    # each run keeps its first row (as script 16).
    by_type_key = collections.OrderedDict()
    for r in all_analyzable_rows:
        tk = (r['type'], r['key'])
        by_type_key.setdefault(tk, []).append(r)

    surviving_rows = []
    collapsed_count = 0
    for tk, group in by_type_key.items():
        i = 0
        while i < len(group):
            first_row = group[i]
            surviving_rows.append(first_row)
            first_idx = first_row['row_index']
            j = i + 1
            while j < len(group) and (group[j]['row_index'] - first_idx <= 2):
                collapsed_count += 1
                j += 1
            i = j

    surviving_set = set(r['row_index'] for r in surviving_rows)

    # M3_original on population multi-sign texts
    cov_tab_orig, _, _ = top10_and_repeat_share(tab_ms)
    cov_seal_orig, _, _ = top10_and_repeat_share(seal_ms)
    m3_original = {
        "TAB:I_cov10": cov_tab_orig,
        "TAB:I_N": len(tab_ms),
        "SEAL:S_cov10": cov_seal_orig,
        "SEAL:S_N": len(seal_ms),
        "gap": cov_tab_orig - cov_seal_orig
    }

    # M3_collapsed on surviving population multi-sign texts
    tab_ms_surv = [r for r in tab_ms if r['row_index'] in surviving_set]
    seal_ms_surv = [r for r in seal_ms if r['row_index'] in surviving_set]
    cov_tab_coll, _, _ = top10_and_repeat_share(tab_ms_surv)
    cov_seal_coll, _, _ = top10_and_repeat_share(seal_ms_surv)
    m3_collapsed = {
        "TAB:I_cov10": cov_tab_coll,
        "TAB:I_N": len(tab_ms_surv),
        "SEAL:S_cov10": cov_seal_coll,
        "SEAL:S_N": len(seal_ms_surv),
        "gap": cov_tab_coll - cov_seal_coll
    }

    # M3_sweep: top-N 5, 10, 20 x sites all and Harappa, cells with >= 30 texts per class
    gaps = []
    for site in ["all", "Harappa"]:
        tab_site = tab_ms_surv if site == "all" else [r for r in tab_ms_surv if r['site'] == 'Harappa']
        seal_site = seal_ms_surv if site == "all" else [r for r in seal_ms_surv if r['site'] == 'Harappa']
        n_t = len(tab_site)
        n_s = len(seal_site)
        if n_t >= 30 and n_s >= 30:
            for top_n in [5, 10, 20]:
                c_t = topN_cov(tab_site, top_n)
                c_s = topN_cov(seal_site, top_n)
                gaps.append(c_t - c_s)

    m3_sweep = {
        "cells": len(gaps),
        "positive": sum(1 for g in gaps if g > 0),
        "min": min(gaps) if gaps else 0.0
    }

    return {
        "M2": {
            "TAB:I": m2_tab,
            "SEAL:S": m2_seal
        },
        "M3_rows_collapsed": collapsed_count,
        "M3_original": m3_original,
        "M3_collapsed": m3_collapsed,
        "M3_sweep": m3_sweep
    }


# --- Analysis 13.11: Label-permutation null, CLUSTER-AWARE ---
def compute_13_11(pop_rows, seed=42):
    tab_texts = [r for r in pop_rows if r['type'] == 'TAB:I' and r['legible_len'] >= 2]
    seal_texts = [r for r in pop_rows if r['type'] == 'SEAL:S' and r['legible_len'] >= 2]

    obs_tab, _, _ = top10_and_repeat_share(tab_texts)
    obs_seal, _, _ = top10_and_repeat_share(seal_texts)
    obs_diff = obs_tab - obs_seal

    # Units = each class's own find-spots over multi-sign TAB:I and SEAL:S texts
    units_tab = collections.OrderedDict()
    for r in tab_texts:
        units_tab.setdefault(r['findspot_d2a'], []).append(r)

    units_seal = collections.OrderedDict()
    for r in seal_texts:
        units_seal.setdefault(r['findspot_d2a'], []).append(r)

    all_units = list(units_tab.values()) + list(units_seal.values())
    all_units.sort(key=lambda u: u[0]['row_index'])

    n_tab = len(tab_texts)

    # Cluster-aware shuffle: 1,000 permutations, random.Random(42)
    rng_cluster = random.Random(seed)
    cluster_null_diffs = []
    for _ in range(1000):
        shuffled_units = list(all_units)
        rng_cluster.shuffle(shuffled_units)
        pseudo_tab = []
        idx = 0
        while len(pseudo_tab) < n_tab:
            pseudo_tab.extend(shuffled_units[idx])
            idx += 1
        pseudo_seal = []
        for u in shuffled_units[idx:]:
            pseudo_seal.extend(u)

        cov_ptab = topN_cov(pseudo_tab, 10)
        cov_pseal = topN_cov(pseudo_seal, 10)
        cluster_null_diffs.append(cov_ptab - cov_pseal)

    null_mean_c = sum(cluster_null_diffs) / len(cluster_null_diffs)
    null_max_c = max(cluster_null_diffs)
    n_ge_c = sum(1 for d in cluster_null_diffs if d >= obs_diff)
    p_c = (1 + n_ge_c) / (1 + 1000)

    # Text-level shuffle: pool = TAB:I then SEAL:S texts in row-index order, shuffled in place 1,000 times
    rng_text = random.Random(seed)
    pool = list(tab_texts) + list(seal_texts)
    text_null_diffs = []
    for _ in range(1000):
        rng_text.shuffle(pool)
        pseudo_tab = pool[:n_tab]
        pseudo_seal = pool[n_tab:]
        cov_ptab = topN_cov(pseudo_tab, 10)
        cov_pseal = topN_cov(pseudo_seal, 10)
        text_null_diffs.append(cov_ptab - cov_pseal)

    null_mean_t = sum(text_null_diffs) / len(text_null_diffs)
    null_max_t = max(text_null_diffs)
    n_ge_t = sum(1 for d in text_null_diffs if d >= obs_diff)
    p_t = (1 + n_ge_t) / (1 + 1000)

    return {
        "observed": obs_diff,
        "units": len(all_units),
        "cluster": {
            "null_mean": null_mean_c,
            "null_max": null_max_c,
            "n_ge_observed": n_ge_c,
            "p": p_c
        },
        "text_level": {
            "null_mean": null_mean_t,
            "null_max": null_max_t,
            "n_ge_observed": n_ge_t,
            "p": p_t
        }
    }


def main():
    start_time = time.time()
    verify_input_sha(INPUT_CSV)
    all_analyzable_rows = parse_corpus(INPUT_CSV)

    output = {}
    for pop in ("complete", "all"):
        if pop == "complete":
            pop_rows = [r for r in all_analyzable_rows if r['complete'] == 'Y']
        else:
            pop_rows = all_analyzable_rows

        output[f"13.4.{pop}"] = compute_13_4(pop_rows)
        output[f"13.6.{pop}"] = compute_13_6(pop_rows)
        output[f"13.9.{pop}"] = compute_13_9(pop_rows)
        output[f"13.10.{pop}"] = compute_13_10(pop_rows, all_analyzable_rows)
        output[f"13.11.{pop}"] = compute_13_11(pop_rows, seed=42)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, sort_keys=True, indent=1)

    elapsed = time.time() - start_time
    print(f"Computed all 10 keys in {elapsed:.2f}s and wrote to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
