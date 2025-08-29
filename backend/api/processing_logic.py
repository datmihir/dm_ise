import csv
import os
import math
from collections import Counter

# --- Helper Functions ---

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
                pass # Skip non-numeric data
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

# --- Statistical Calculation Functions (Existing) ---

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

# --- Normalization and Discretization (Existing) ---

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

# --- NEW: Data Cleaning ---

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

# --- NEW: Chi-Square Test ---

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

# --- NEW: Visualization Data Preparation ---

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
