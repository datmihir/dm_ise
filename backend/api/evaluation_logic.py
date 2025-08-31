import random
from collections import Counter
from . import classification_logic

def train_test_split(dataset, test_size=0.2):
    data = dataset[:]
    random.shuffle(data)
    split_idx = int(len(data) * (1 - test_size))
    return data[:split_idx], data[split_idx:]

def predict_with_tree(tree, instance, default=None):
    if not isinstance(tree, dict):
        return tree  

    attr = next(iter(tree))  
    if attr not in instance:
        return default

    value = instance[attr]
    if value in tree[attr]:
        return predict_with_tree(tree[attr][value], instance, default)
    else:
        return default

def generate_confusion_matrix(predictions, actual, class_labels):
    matrix = [[0 for _ in class_labels] for _ in class_labels]
    label_to_idx = {label: i for i, label in enumerate(class_labels)}

    for pred, act in zip(predictions, actual):
        if act in label_to_idx and pred in label_to_idx:
            matrix[label_to_idx[act]][label_to_idx[pred]] += 1

    return {
        "labels": class_labels,
        "matrix": matrix
    }

def evaluate_model(dataset, task, params):
    if not dataset:
        return {'error': 'Dataset is empty.'}

    target_attr = params.get('target_attribute')
    if not target_attr:
        return {'error': 'Target attribute not provided.'}

    attributes = [attr for attr in dataset[0].keys() if attr != target_attr]
    class_labels = list({row[target_attr] for row in dataset})

    train_data, test_data = train_test_split(dataset, test_size=0.2)

    predictions = []
    actual = [row[target_attr] for row in test_data]

    if task == 'decision_tree':
        split_criterion = params.get('split_criterion', 'information_gain')
        processed_train_data = classification_logic.preprocess_for_tree(train_data, attributes)
        model = classification_logic.build_decision_tree(
            processed_train_data, attributes, target_attr, split_criterion
        )

        for row in test_data:
            pred = predict_with_tree(model, row, default=random.choice(class_labels))
            predictions.append(pred)

    elif task == 'knn':
        k = int(params.get('k', 3))
        for row in test_data:
            predictions.append(
                classification_logic.knn_classify(train_data, row, attributes, target_attr, k)
            )

    elif task == 'naive_bayes':
        model = classification_logic.train_naive_bayes(train_data, attributes, target_attr)
        for row in test_data:
            predictions.append(
                classification_logic.naive_bayes_predict(model, row, attributes)
            )

    elif task == 'rule_based_1r':
        model = classification_logic.train_1r(train_data, attributes, target_attr)
        for row in test_data:
            predictions.append(
                classification_logic.predict_1r(model, row)
            )

    else:
        return {'error': f'Unsupported task: {task}'}

    correct = sum(1 for p, a in zip(predictions, actual) if p == a)
    accuracy = round(correct / len(actual) * 100, 2) if actual else 0

    confusion_matrix = generate_confusion_matrix(predictions, actual, class_labels)

    return {
        'task': task,
        'accuracy': accuracy,
        'confusion_matrix': confusion_matrix,
        'sample_predictions': list(zip(predictions[:10], actual[:10])) 
    }
