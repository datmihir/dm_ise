import csv
import os
import math
from collections import Counter

def load_column_data(file_path, column_name):
    """Loads a specific column from a CSV file, converting to float if possible."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")

    column_data = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if column_name not in reader.fieldnames:
            raise ValueError(f"Column '{column_name}' not found in the file.")
        
        for row in reader:
            try:
                column_data.append(float(row[column_name]))
            except (ValueError, TypeError):
                pass 
    return column_data

def load_full_data(file_path):
    """Loads the entire CSV into a list of dictionaries, converting numbers."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")
    
    dataset = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            processed_row = {}
            for key, value in row.items():
                try:
                    processed_row[key] = float(value)
                except (ValueError, TypeError):
                    processed_row[key] = value
            dataset.append(processed_row)
    return dataset


def calculate_mean(data):
    if not data: return 0
    return sum(data) / len(data)

def calculate_median(data):
    if not data: return 0
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid_index = n // 2
    return sorted_data[mid_index] if n % 2 == 1 else (sorted_data[mid_index - 1] + sorted_data[mid_index]) / 2

def calculate_mode(data):
    if not data: return []
    counts = Counter(data)
    max_count = max(counts.values())
    return [key for key, value in counts.items() if value == max_count]

def calculate_variance(data):
    if len(data) < 2: return 0
    mean = calculate_mean(data)
    return sum((x - mean) ** 2 for x in data) / (len(data) - 1)

def calculate_std_dev(data):
    return math.sqrt(calculate_variance(data))

def calculate_covariance(data1, data2):
    if len(data1) != len(data2) or len(data1) < 2: return 0
    mean1, mean2 = calculate_mean(data1), calculate_mean(data2)
    return sum((x - mean1) * (y - mean2) for x, y in zip(data1, data2)) / (len(data1) - 1)

def calculate_correlation(data1, data2):
    std_dev1, std_dev2 = calculate_std_dev(data1), calculate_std_dev(data2)
    if std_dev1 == 0 or std_dev2 == 0: return 0
    return calculate_covariance(data1, data2) / (std_dev1 * std_dev2)

def normalize_min_max(dataset, column):
    values = [row[column] for row in dataset if isinstance(row.get(column), (int, float))]
    if not values: return dataset
    min_val, max_val = min(values), max(values)
    val_range = max_val - min_val
    if val_range == 0: return dataset
    for row in dataset:
        if isinstance(row.get(column), (int, float)):
            row[column] = (row[column] - min_val) / val_range
    return dataset

def normalize_z_score(dataset, column):
    values = [row[column] for row in dataset if isinstance(row.get(column), (int, float))]
    if not values: return dataset
    mean, std_dev = calculate_mean(values), calculate_std_dev(values)
    if std_dev == 0: return dataset
    for row in dataset:
        if isinstance(row.get(column), (int, float)):
            row[column] = (row[column] - mean) / std_dev
    return dataset

def normalize_decimal_scaling(dataset, column):
    values = [abs(row[column]) for row in dataset if isinstance(row.get(column), (int, float))]
    if not values: return dataset
    max_abs_val = max(values)
    if max_abs_val == 0: return dataset
    k = math.ceil(math.log10(max_abs_val))
    divisor = 10 ** k
    for row in dataset:
        if isinstance(row.get(column), (int, float)):
            row[column] = row[column] / divisor
    return dataset

def discretize_by_binning(dataset, column, num_bins):
    values = [row[column] for row in dataset if isinstance(row.get(column), (int, float))]
    if not values or num_bins <= 0: return dataset
    min_val, max_val = min(values), max(values)
    bin_width = (max_val - min_val) / num_bins
    if bin_width == 0:
        for row in dataset:
            if isinstance(row.get(column), (int, float)): row[column] = f'Bin 1: ({min_val})'
        return dataset
    bins = [min_val + i * bin_width for i in range(num_bins + 1)]
    bins[-1] = max_val
    for row in dataset:
        if isinstance(row.get(column), (int, float)):
            val = row[column]
            for i in range(num_bins):
                if bins[i] <= val <= bins[i+1]:
                    if i < num_bins - 1 and val == bins[i+1]: continue
                    row[column] = f'Bin {i+1}: [{bins[i]:.2f} - {bins[i+1]:.2f}]'
                    break
    return dataset


def handle_missing_values(dataset, method, column=None):
    """Handles missing values by removing rows or filling with mean."""
    if method == 'remove_rows':
        return [row for row in dataset if all(str(val).strip() != '' and val is not None for val in row.values())]
    
    elif method == 'fill_mean':
        if not column: raise ValueError("Column must be specified for 'fill_mean' method.")
        existing_values = [float(row[column]) for row in dataset if str(row.get(column)).strip() != '' and row.get(column) is not None and isinstance(row.get(column), (int, float))]
        if not existing_values: return dataset
        mean_val = calculate_mean(existing_values)
        for row in dataset:
            val = row.get(column)
            if str(val).strip() == '' or val is None:
                row[column] = mean_val
        return dataset
    else:
        raise ValueError(f"Unknown missing value method: {method}")


def calculate_chi_square(dataset, column1, column2):
    """Calculates the Chi-square statistic for two categorical columns."""
    categories1 = sorted(list(set(row[column1] for row in dataset)))
    categories2 = sorted(list(set(row[column2] for row in dataset)))
    contingency_table = {cat1: {cat2: 0 for cat2 in categories2} for cat1 in categories1}
    for row in dataset:
        contingency_table[row[column1]][row[column2]] += 1
    
    row_totals = {cat1: sum(contingency_table[cat1].values()) for cat1 in categories1}
    col_totals = {cat2: sum(contingency_table[cat1][cat2] for cat1 in categories1) for cat2 in categories2}
    grand_total = sum(row_totals.values())
    if grand_total == 0: return 0, 0, {}
        
    chi_square_stat = 0
    for cat1 in categories1:
        for cat2 in categories2:
            expected = (row_totals[cat1] * col_totals[cat2]) / grand_total
            if expected == 0: continue
            observed = contingency_table[cat1][cat2]
            chi_square_stat += ((observed - expected) ** 2) / expected
            
    df = (len(categories1) - 1) * (len(categories2) - 1)
    table_for_json = [[""] + categories2]
    for cat1 in categories1:
        row = [cat1] + [contingency_table[cat1][cat2] for cat2 in categories2]
        table_for_json.append(row)
    return chi_square_stat, df, table_for_json


def prepare_histogram_data(dataset, column, num_bins):
    """Prepares data for a histogram by binning a numerical column."""
    values = [row[column] for row in dataset if isinstance(row.get(column), (int, float))]
    if not values or num_bins <= 0: return {'labels': [], 'counts': []}
    min_val, max_val = min(values), max(values)
    if min_val == max_val: return {'labels': [f'{min_val:.2f}'], 'counts': [len(values)]}
    bin_width = (max_val - min_val) / num_bins
    bins = [min_val + i * bin_width for i in range(num_bins + 1)]
    labels = [f'[{bins[i]:.2f}-{bins[i+1]:.2f}]' for i in range(num_bins)]
    counts = [0] * num_bins
    for val in values:
        bin_index = min(int((val - min_val) / bin_width), num_bins - 1)
        if val == max_val: bin_index = num_bins - 1
        counts[bin_index] += 1
    return {'labels': labels, 'counts': counts}

def prepare_scatter_plot_data(dataset, column1, column2):
    """Prepares data for a scatter plot from two numerical columns."""
    return [{'x': row.get(column1), 'y': row.get(column2)} for row in dataset if isinstance(row.get(column1), (int, float)) and isinstance(row.get(column2), (int, float))]


# -----------------------------
# Clustering: k-Means & k-Medoid
# -----------------------------
def _extract_numeric_matrix(dataset, columns):
    matrix = []
    for row in dataset:
        vec = []
        ok = True
        for c in columns:
            val = row.get(c)
            if isinstance(val, (int, float)):
                vec.append(float(val))
            else:
                ok = False
                break
        if ok:
            matrix.append(vec)
    return matrix

def _euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def k_means(dataset, columns, k=3, max_iter=100):
    """Simple k-means implementation operating on selected numeric columns."""
    matrix = _extract_numeric_matrix(dataset, columns)
    if not matrix: return {'error': 'No numeric data found for selected columns.'}

    import random
    n = len(matrix)
    dim = len(matrix[0])
    # initialize centroids randomly
    centroids = [matrix[i][:] for i in random.sample(range(n), min(k, n))]

    for it in range(max_iter):
        clusters = [[] for _ in range(len(centroids))]
        for vec in matrix:
            dists = [_euclidean(vec, c) for c in centroids]
            idx = dists.index(min(dists))
            clusters[idx].append(vec)

        moved = False
        for i, cluster in enumerate(clusters):
            if not cluster: continue
            new_centroid = [sum(col) / len(cluster) for col in zip(*cluster)]
            if any(abs(a - b) > 1e-6 for a, b in zip(new_centroid, centroids[i])):
                centroids[i] = new_centroid
                moved = True
        if not moved:
            break

    # Map input rows to cluster indexes for a simple response (first N rows considered)
    assignments = []
    for vec in matrix:
        dists = [_euclidean(vec, c) for c in centroids]
        assignments.append(dists.index(min(dists)))

    return {'task': 'k_means', 'k': len(centroids), 'centroids': centroids, 'assignments_sample': assignments[:200]}


def k_medoid(dataset, columns, k=3, max_iter=100):
    """Simple k-medoid (PAM-like) implementation on selected numeric columns."""
    matrix = _extract_numeric_matrix(dataset, columns)
    if not matrix: return {'error': 'No numeric data found for selected columns.'}

    import random
    n = len(matrix)
    if k >= n:
        # trivial: each point is a medoid
        return {'task': 'k_medoid', 'k': n, 'medoids': matrix, 'assignments_sample': list(range(n))}

    medoid_indices = random.sample(range(n), k)
    medoids = [matrix[i] for i in medoid_indices]

    for it in range(max_iter):
        clusters = [[] for _ in range(k)]
        for idx, vec in enumerate(matrix):
            dists = [_euclidean(vec, m) for m in medoids]
            mi = dists.index(min(dists))
            clusters[mi].append(idx)

        changed = False
        for i, cluster in enumerate(clusters):
            if not cluster: continue
            # pick the medoid as the point minimizing total distance to others
            best_idx, best_cost = None, float('inf')
            for candidate_idx in cluster:
                cost = sum(_euclidean(matrix[candidate_idx], matrix[j]) for j in cluster)
                if cost < best_cost:
                    best_cost = cost
                    best_idx = candidate_idx
            if best_idx is not None and matrix[best_idx] != medoids[i]:
                medoids[i] = matrix[best_idx]
                changed = True
        if not changed:
            break

    assignments = []
    for vec in matrix:
        dists = [_euclidean(vec, m) for m in medoids]
        assignments.append(dists.index(min(dists)))

    return {'task': 'k_medoid', 'k': k, 'medoids': medoids, 'assignments_sample': assignments[:200]}


# -----------------------------
# Association Rules: Apriori
# -----------------------------
def apriori(dataset, columns, min_support=0.1, min_confidence=0.6, max_len=3):
    """A small Apriori implementation treating each row as a transaction made of selected column values.
    Values are used as items; to avoid collisions item names are prefixed by column name.
    """
    transactions = []
    for row in dataset:
        items = []
        for c in columns:
            val = row.get(c)
            if val is not None and str(val).strip() != '':
                items.append(f"{c}={val}")
        if items:
            transactions.append(set(items))

    n = len(transactions)
    if n == 0:
        return {'error': 'No transactions created from selected columns.'}

    # support counting
    def support(itemset):
        cnt = sum(1 for t in transactions if itemset.issubset(t))
        return cnt / n

    # generate frequent itemsets
    freq_itemsets = {}
    # L1
    C1 = {}
    for t in transactions:
        for item in t:
            C1[item] = C1.get(item, 0) + 1
    L1 = {frozenset([item]): cnt / n for item, cnt in C1.items() if (cnt / n) >= min_support}
    current_L = set(L1.keys())
    freq_itemsets.update(L1)

    k = 2
    while current_L and k <= max_len:
        # candidate generation (join)
        candidates = set()
        cur_list = list(current_L)
        for i in range(len(cur_list)):
            for j in range(i + 1, len(cur_list)):
                union = cur_list[i].union(cur_list[j])
                if len(union) == k:
                    candidates.add(frozenset(union))

        next_L = set()
        for cand in candidates:
            sup = sum(1 for t in transactions if cand.issubset(t)) / n
            if sup >= min_support:
                freq_itemsets[cand] = sup
                next_L.add(cand)
        current_L = next_L
        k += 1

    # generate rules
    rules = []
    for itemset, sup in list(freq_itemsets.items()):
        if len(itemset) < 2: continue
        items = list(itemset)
        # all non-empty proper subsets
        from itertools import combinations
        for r in range(1, len(items)):
            for antecedent in combinations(items, r):
                A = frozenset(antecedent)
                C = itemset.difference(A)
                if not C: continue
                conf = support(itemset) / support(A)
                if conf >= min_confidence:
                    rules.append({'antecedent': list(A), 'consequent': list(C), 'support': round(sup, 4), 'confidence': round(conf, 4)})

    return {'task': 'apriori', 'frequent_itemsets': {', '.join(list(k)): v for k, v in freq_itemsets.items()}, 'rules': rules}


# -----------------------------
# Web Mining: PageRank & HITS
# -----------------------------
def pagerank_from_edges(dataset, source_col, target_col, damping=0.85, max_iter=100, tol=1e-6):
    edges = []
    for row in dataset:
        s = row.get(source_col); t = row.get(target_col)
        if s is None or t is None: continue
        edges.append((str(s), str(t)))

    nodes = set([u for u, v in edges] + [v for u, v in edges])
    if not nodes:
        return {'error': 'No edges found using selected columns.'}

    node_list = list(nodes)
    idx = {n: i for i, n in enumerate(node_list)}
    N = len(node_list)

    out_links = {n: set() for n in node_list}
    in_links = {n: set() for n in node_list}
    for u, v in edges:
        out_links[u].add(v)
        in_links[v].add(u)

    pr = {n: 1.0 / N for n in node_list}
    for it in range(max_iter):
        new_pr = {}
        diff = 0.0
        for n in node_list:
            rank = (1 - damping) / N
            rank += damping * sum(pr.get(q, 0.0) / max(1, len(out_links[q])) for q in in_links[n])
            new_pr[n] = rank
            diff += abs(rank - pr[n])
        pr = new_pr
        if diff < tol:
            break

    # return sorted
    sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)
    return {'task': 'pagerank', 'scores': [{ 'node': n, 'score': round(s, 6)} for n, s in sorted_pr]}


def hits_from_edges(dataset, source_col, target_col, max_iter=100, tol=1e-6):
    edges = []
    for row in dataset:
        s = row.get(source_col); t = row.get(target_col)
        if s is None or t is None: continue
        edges.append((str(s), str(t)))

    nodes = set([u for u, v in edges] + [v for u, v in edges])
    if not nodes:
        return {'error': 'No edges found using selected columns.'}

    node_list = list(nodes)
    in_links = {n: set() for n in node_list}
    out_links = {n: set() for n in node_list}
    for u, v in edges:
        out_links[u].add(v)
        in_links[v].add(u)

    auth = {n: 1.0 for n in node_list}
    hub = {n: 1.0 for n in node_list}
    for it in range(max_iter):
        # update authority
        new_auth = {}
        for n in node_list:
            new_auth[n] = sum(hub.get(q, 0.0) for q in in_links[n])
        # normalize
        norm = math.sqrt(sum(v * v for v in new_auth.values())) or 1.0
        for n in node_list:
            new_auth[n] /= norm

        # update hub
        new_hub = {}
        for n in node_list:
            new_hub[n] = sum(new_auth.get(q, 0.0) for q in out_links[n])
        norm2 = math.sqrt(sum(v * v for v in new_hub.values())) or 1.0
        for n in node_list:
            new_hub[n] /= norm2

        # check convergence
        diff = sum(abs(new_auth[n] - auth.get(n, 0.0)) for n in node_list) + sum(abs(new_hub[n] - hub.get(n, 0.0)) for n in node_list)
        auth, hub = new_auth, new_hub
        if diff < tol:
            break

    sorted_auth = sorted(auth.items(), key=lambda x: x[1], reverse=True)
    sorted_hub = sorted(hub.items(), key=lambda x: x[1], reverse=True)
    return {
        'task': 'hits',
        'authorities': [{ 'node': n, 'score': round(s, 6)} for n, s in sorted_auth],
        'hubs': [{ 'node': n, 'score': round(s, 6)} for n, s in sorted_hub]
    }

