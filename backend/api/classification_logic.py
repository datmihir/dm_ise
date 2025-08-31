import math
from collections import Counter, defaultdict
import random
import copy

# --- Helper Functions ---

def euclidean_distance(row1, row2, attributes):
    """Calculates the Euclidean distance between two rows for given numeric attributes."""
    distance = 0.0
    for attr in attributes:
        val1, val2 = row1.get(attr, 0), row2.get(attr, 0)
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            distance += (val1 - val2) ** 2
    return math.sqrt(distance)

# --- Decision Tree ---

def _discretize_column(dataset, column, num_bins=4):
    """Helper to discretize a single numeric column into categorical bins."""
    values = [row[column] for row in dataset if isinstance(row.get(column), (int, float))]
    if not values: return
    
    min_val, max_val = min(values), max(values)
    if min_val == max_val: return

    bin_width = (max_val - min_val) / num_bins
    
    for row in dataset:
        if isinstance(row.get(column), (int, float)):
            val = row[column]
            if bin_width == 0:
                bin_index = 0
            else:
                bin_index = min(int((val - min_val) / bin_width), num_bins - 1)
                if val == max_val: bin_index = num_bins - 1
            
            lower_bound = min_val + bin_index * bin_width
            upper_bound = min_val + (bin_index + 1) * bin_width
            row[column] = f"[{lower_bound:.2f}-{upper_bound:.2f}]"

def preprocess_for_tree(dataset, attributes):
    """Discretizes all numeric attributes in the dataset for the decision tree."""
    processed_dataset = copy.deepcopy(dataset)
    for attr in attributes:
        # Check if the column is likely numeric and continuous
        if any(isinstance(row.get(attr), float) for row in processed_dataset):
             _discretize_column(processed_dataset, attr)
        else: # For integer types, check if there are many unique values
            unique_values = set(row[attr] for row in processed_dataset if isinstance(row.get(attr), int))
            if len(unique_values) > 5: # Threshold for when to discretize integers
                _discretize_column(processed_dataset, attr)
    return processed_dataset

def calculate_entropy(data, target_attr):
    total_count = len(data)
    if total_count == 0: return 0
    value_counts = Counter(row[target_attr] for row in data)
    entropy = 0
    for count in value_counts.values():
        p = count / total_count
        if p > 0: entropy -= p * math.log2(p)
    return entropy

def calculate_information_gain(data, attribute, target_attr):
    total_entropy = calculate_entropy(data, target_attr)
    attribute_values = set(row[attribute] for row in data)
    weighted_entropy = 0
    for value in attribute_values:
        subset = [row for row in data if row[attribute] == value]
        weighted_entropy += (len(subset) / len(data)) * calculate_entropy(subset, target_attr)
    return total_entropy - weighted_entropy

def calculate_split_info(data, attribute):
    total_count = len(data)
    if total_count == 0: return 0
    value_counts = Counter(row[attribute] for row in data)
    split_info = 0
    for count in value_counts.values():
        p = count / total_count
        if p > 0: split_info -= p * math.log2(p)
    return split_info

def calculate_gain_ratio(data, attribute, target_attr):
    info_gain = calculate_information_gain(data, attribute, target_attr)
    split_info = calculate_split_info(data, attribute)
    return info_gain / split_info if split_info != 0 else 0

def calculate_gini_index(data, target_attr):
    total_count = len(data)
    if total_count == 0: return 0
    value_counts = Counter(row[target_attr] for row in data)
    impurity = 1
    for count in value_counts.values(): impurity -= (count / total_count) ** 2
    return impurity

def calculate_gini_gain(data, attribute, target_attr):
    total_gini = calculate_gini_index(data, target_attr)
    attribute_values = set(row[attribute] for row in data)
    weighted_gini = 0
    for value in attribute_values:
        subset = [row for row in data if row[attribute] == value]
        weighted_gini += (len(subset) / len(data)) * calculate_gini_index(subset, target_attr)
    return total_gini - weighted_gini

def find_best_attribute(data, attributes, target_attr, split_criterion):
    gains = {}
    for attribute in attributes:
        if split_criterion == 'information_gain':
            gains[attribute] = calculate_information_gain(data, attribute, target_attr)
        elif split_criterion == 'gini_index':
            gains[attribute] = calculate_gini_gain(data, attribute, target_attr)
        elif split_criterion == 'gain_ratio':
            gains[attribute] = calculate_gain_ratio(data, attribute, target_attr)
            
    return max(gains, key=gains.get) if gains else None

def build_decision_tree(data, attributes, target_attr, split_criterion):
    target_values = [row[target_attr] for row in data]
    if len(set(target_values)) == 1: return target_values[0]
    if not attributes: return Counter(target_values).most_common(1)[0][0]
    
    best_attribute = find_best_attribute(data, attributes, target_attr, split_criterion)
    if best_attribute is None: return Counter(target_values).most_common(1)[0][0]
    
    tree = {best_attribute: {}}
    remaining_attributes = [attr for attr in attributes if attr != best_attribute]
    
    for value in set(row[best_attribute] for row in data):
        subset = [row for row in data if row[best_attribute] == value]
        tree[best_attribute][value] = build_decision_tree(subset, remaining_attributes, target_attr, split_criterion) if subset else Counter(target_values).most_common(1)[0][0]
    return tree

# --- Other Classifiers ---
def predict_knn(train_data, test_instance, k, attributes, target_attr):
    distances = sorted([(train_row, euclidean_distance(train_row, test_instance, attributes)) for train_row in train_data], key=lambda x: x[1])
    neighbors = [d[0] for d in distances[:k]]
    prediction = Counter(row[target_attr] for row in neighbors).most_common(1)[0][0]
    return prediction, [(n[target_attr], d[1]) for n, d in zip(neighbors, distances[:k])]

def train_naive_bayes(train_data, attributes, target_attr):
    model = {'priors': {}, 'conditionals': {}}
    class_counts = Counter(row[target_attr] for row in train_data)
    for class_val, count in class_counts.items(): model['priors'][class_val] = count / len(train_data)
    for attr in attributes:
        model['conditionals'][attr] = {}
        for class_val in class_counts:
            subset = [row for row in train_data if row[target_attr] == class_val]
            attr_values = [row[attr] for row in subset if isinstance(row.get(attr), (int, float))]
            mean = sum(attr_values) / len(attr_values) if attr_values else 0
            std_dev = (sum([(x - mean) ** 2 for x in attr_values]) / len(attr_values)) ** 0.5 if attr_values else 0
            model['conditionals'][attr][class_val] = {'mean': mean, 'std_dev': std_dev}
    return model

def gaussian_pdf(x, mean, std_dev):
    if std_dev == 0: return 1 if x == mean else 1e-9
    exponent = math.exp(-((x - mean) ** 2 / (2 * std_dev ** 2)))
    return (1 / (math.sqrt(2 * math.pi) * std_dev)) * exponent

def predict_naive_bayes(model, test_instance, attributes):
    probabilities = {}
    for class_val, prior in model['priors'].items():
        probabilities[class_val] = math.log(prior)
        for attr in attributes:
            if isinstance(test_instance.get(attr), (int, float)):
                stats = model['conditionals'][attr][class_val]
                cond_prob = gaussian_pdf(test_instance[attr], stats['mean'], stats['std_dev'])
                probabilities[class_val] += math.log(cond_prob)
    return max(probabilities, key=probabilities.get)

def train_1r(train_data, attributes, target_attr):
    best_attribute, min_error, best_rules = None, float('inf'), {}
    for attr in attributes:
        rules, counts = {}, defaultdict(lambda: defaultdict(int))
        for row in train_data: counts[row[attr]][row[target_attr]] += 1
        for attr_val, target_counts in counts.items(): rules[attr_val] = max(target_counts, key=target_counts.get)
        error = sum(1 for row in train_data if rules.get(row[attr]) != row[target_attr])
        if error < min_error:
            min_error, best_attribute, best_rules = error, attr, rules
    return {'attribute': best_attribute, 'rules': best_rules, 'error_rate': min_error / len(train_data)}

# --- THIS IS THE CORRECTED 1R PREDICTION FUNCTION ---
def predict_1r(model, test_instance):
    """Predicts using the trained 1R model by checking numeric ranges."""
    attr_to_use = model.get('attribute')
    if not attr_to_use:
        return "Unknown (Model has no attribute)"

    test_value = test_instance.get(attr_to_use)
    if test_value is None:
        return "Unknown (Attribute missing in test instance)"

    rules = model.get('rules', {})
    
    # Handle numeric attributes by checking ranges
    if isinstance(test_value, (int, float)):
        for interval, label in rules.items():
            # Check if the key is a string representation of an interval
            if isinstance(interval, str) and interval.startswith('[') and '-' in interval:
                try:
                    # Parse the interval string like "[0.10-0.70]"
                    low_str, high_str = interval.strip("[]").split('-')
                    low = float(low_str)
                    high = float(high_str)
                    if low <= test_value <= high:
                        return label
                except (ValueError, IndexError):
                    continue # Skip malformed rule keys
    
    # Fallback for exact match (for categorical data) or if range check fails
    return rules.get(test_value, "Unknown (No rule for this value)")

def train_linear_regression(dataset, independent_attr, dependent_attr):
    x = [row[independent_attr] for row in dataset if isinstance(row.get(independent_attr), (int, float))]
    y = [row[dependent_attr] for row in dataset if isinstance(row.get(dependent_attr), (int, float))]
    if len(x) != len(y) or len(x) < 2: raise ValueError("Columns must have at least 2 matching numeric rows.")
    n, x_mean, y_mean = len(x), sum(x) / len(x), sum(y) / len(y)
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((val - x_mean) ** 2 for val in x)
    if denominator == 0: raise ValueError("Cannot perform regression, independent variable is constant.")
    b1 = numerator / denominator
    b0 = y_mean - (b1 * x_mean)
    return {'B0_intercept': b0, 'B1_slope': b1}

def train_perceptron(train_data, attributes, target_attr, learning_rate, epochs):
    target_map = {val: i for i, val in enumerate(sorted(list(set(row[target_attr] for row in train_data))))}
    if len(target_map) != 2: raise ValueError("Perceptron requires a binary target attribute.")
    weights = [random.uniform(-0.5, 0.5) for _ in range(len(attributes) + 1)]
    errors = []
    for epoch in range(epochs):
        sum_error = 0
        for row in train_data:
            inputs = [row.get(attr, 0) for attr in attributes]
            target = target_map[row[target_attr]]
            activation = weights[0] + sum(weights[i+1] * inputs[i] for i in range(len(attributes)))
            prediction = 1 if activation >= 0 else 0
            error = target - prediction
            sum_error += error**2
            weights[0] += learning_rate * error
            for i in range(len(attributes)):
                weights[i+1] += learning_rate * error * inputs[i]
        errors.append(sum_error)
    return {'weights': weights, 'target_map': target_map, 'error_per_epoch': errors}
