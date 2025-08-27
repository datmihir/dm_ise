from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
import csv
import json
from . import processing_logic
from . import classification_logic

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('dataset'):
        uploaded_file = request.FILES['dataset']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        return JsonResponse({'message': f'File "{filename}" uploaded successfully.', 'file_url': file_url}, status=201)
    return JsonResponse({'error': 'Invalid request method or no file provided.'}, status=400)

def preview_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found.'}, status=404)
    try:
        preview_data, header = [], []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            if header is None: return JsonResponse({'error': 'Cannot read header from empty file.'}, status=400)
            for i, row in enumerate(reader):
                if i >= 20: break
                preview_data.append({header[j]: cell for j, cell in enumerate(row)})
        return JsonResponse({'filename': filename, 'header': header, 'data': preview_data})
    except Exception as e:
        return JsonResponse({'error': f'An error occurred while reading the file: {str(e)}'}, status=500)

@csrf_exempt
def process_data(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        body = json.loads(request.body)
        filename, task = body.get('filename'), body.get('task')
        if not all([filename, task]):
            return JsonResponse({'error': 'Missing filename or task'}, status=400)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # --- TASK ROUTING ---
        if task in ['central_tendency', 'dispersion_of_data']:
            column = body.get('column')
            if not column: return JsonResponse({'error': 'Missing column name'}, status=400)
            data = processing_logic.load_column_data(file_path, column)
            if task == 'central_tendency':
                if not data: return JsonResponse({'error': f'No numeric data in column "{column}"'}, status=400)
                return JsonResponse({'task': 'Measures of Central Tendency', 'column': column, 'mean': round(processing_logic.calculate_mean(data), 4), 'median': round(processing_logic.calculate_median(data), 4), 'mode': processing_logic.calculate_mode(data)})
            elif task == 'dispersion_of_data':
                if not data or len(data) < 2: return JsonResponse({'error': f'Not enough numeric data in column "{column}"'}, status=400)
                return JsonResponse({'task': 'Dispersion of Data', 'column': column, 'variance': round(processing_logic.calculate_variance(data), 4), 'standard_deviation': round(processing_logic.calculate_std_dev(data), 4)})

        elif task == 'correlation_covariance':
            col1, col2 = body.get('column1'), body.get('column2')
            if not all([col1, col2]): return JsonResponse({'error': 'Missing column1 or column2'}, status=400)
            data1, data2 = processing_logic.load_column_data(file_path, col1), processing_logic.load_column_data(file_path, col2)
            if len(data1) != len(data2): return JsonResponse({'error': 'Columns have unequal number of numeric values'}, status=400)
            return JsonResponse({'task': 'Correlation and Covariance', 'columns': f'{col1} and {col2}', 'covariance': round(processing_logic.calculate_covariance(data1, data2), 4), 'correlation_coefficient': round(processing_logic.calculate_correlation(data1, data2), 4)})

        elif task in ['normalize_min_max', 'normalize_z_score', 'normalize_decimal_scaling', 'discretize_by_binning']:
            column = body.get('column')
            if not column: return JsonResponse({'error': 'Missing column name'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            if task == 'normalize_min_max': result_data = processing_logic.normalize_min_max(dataset, column)
            elif task == 'normalize_z_score': result_data = processing_logic.normalize_z_score(dataset, column)
            elif task == 'normalize_decimal_scaling': result_data = processing_logic.normalize_decimal_scaling(dataset, column)
            elif task == 'discretize_by_binning':
                num_bins = body.get('params', {}).get('num_bins', 5)
                result_data = processing_logic.discretize_by_binning(dataset, column, num_bins)
            return JsonResponse({'task': task, 'column': column, 'processed_data': result_data[:100]})

        elif task == 'data_cleaning':
            method = body.get('params', {}).get('method')
            if not method: return JsonResponse({'error': 'Missing cleaning method in params'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            if method == 'fill_mean':
                column = body.get('column')
                if not column: return JsonResponse({'error': 'Missing column for fill_mean'}, status=400)
                result_data = processing_logic.handle_missing_values(dataset, method, column)
            else: result_data = processing_logic.handle_missing_values(dataset, method)
            return JsonResponse({'task': 'Data Cleaning', 'method': method, 'rows_before': len(dataset), 'rows_after': len(result_data), 'processed_data': result_data[:100]})

        elif task == 'chi_square_test':
            col1, col2 = body.get('column1'), body.get('column2')
            if not all([col1, col2]): return JsonResponse({'error': 'Missing column1 or column2'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            statistic, df, table = processing_logic.calculate_chi_square(dataset, col1, col2)
            return JsonResponse({'task': 'Chi-square Test', 'columns': f'{col1} and {col2}', 'chi_square_statistic': round(statistic, 4), 'degrees_of_freedom': df, 'contingency_table': table})

        elif task == 'visualization':
            params = body.get('params', {})
            chart_type = params.get('chart_type')
            if not chart_type: return JsonResponse({'error': 'Missing chart_type in params'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            if chart_type == 'histogram':
                column = body.get('column')
                if not column: return JsonResponse({'error': 'Missing column for histogram'}, status=400)
                num_bins = params.get('num_bins', 10)
                chart_data = processing_logic.prepare_histogram_data(dataset, column, num_bins)
                return JsonResponse({'task': 'Visualization', 'chart_type': 'histogram', 'chart_data': chart_data})
            elif chart_type == 'scatter_plot':
                col1, col2 = body.get('column1'), body.get('column2')
                if not all([col1, col2]): return JsonResponse({'error': 'Missing column1 or column2 for scatter plot'}, status=400)
                chart_data = processing_logic.prepare_scatter_plot_data(dataset, col1, col2)
                return JsonResponse({'task': 'Visualization', 'chart_type': 'scatter_plot', 'chart_data': chart_data})
            else: return JsonResponse({'error': f'Unknown chart_type: {chart_type}'}, status=400)

        else:
            return JsonResponse({'error': f'Unknown task: {task}'}, status=400)

    except (json.JSONDecodeError, FileNotFoundError, ValueError, KeyError) as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@csrf_exempt
def classify_data(request):
    if request.method != 'POST': return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    try:
        body = json.loads(request.body)
        filename, task = body.get('filename'), body.get('task')
        params = body.get('params', {})
        if not all([filename, task, params]): return JsonResponse({'error': 'Missing filename, task, or params'}, status=400)
        
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        dataset = processing_logic.load_full_data(file_path)
        
        target_attribute = params.get('target_attribute')
        if not target_attribute and task not in ['linear_regression']: 
            return JsonResponse({'error': 'Missing target_attribute in params'}, status=400)
        
        attributes = [key for key in dataset[0].keys() if key != target_attribute] if target_attribute else []

        # --- Task Routing for Classifiers ---
        
        if task == 'decision_tree':
            split_criterion = params.get('split_criterion', 'information_gain')
            model = classification_logic.build_decision_tree(dataset, attributes, target_attribute, split_criterion)
            return JsonResponse({'task': 'Decision Tree', 'params': params, 'model': model})

        elif task == 'knn':
            k = params.get('k', 3)
            test_instance = params.get('test_instance')
            if not test_instance: return JsonResponse({'error': 'Missing test_instance for k-NN prediction'}, status=400)
            for key, val in test_instance.items():
                try: test_instance[key] = float(val)
                except (ValueError, TypeError): pass
            prediction, neighbors = classification_logic.predict_knn(dataset, test_instance, k, attributes, target_attribute)
            return JsonResponse({'task': 'k-Nearest Neighbors', 'params': params, 'prediction': prediction, 'nearest_neighbors': neighbors})

        elif task == 'naive_bayes':
            test_instance = params.get('test_instance')
            if not test_instance: return JsonResponse({'error': 'Missing test_instance for Naive Bayes prediction'}, status=400)
            for key, val in test_instance.items():
                try: test_instance[key] = float(val)
                except (ValueError, TypeError): pass
            model = classification_logic.train_naive_bayes(dataset, attributes, target_attribute)
            prediction = classification_logic.predict_naive_bayes(model, test_instance, attributes)
            return JsonResponse({'task': 'Naive Bayesian Classifier', 'params': params, 'prediction': prediction})

        elif task == 'rule_based_1r':
            test_instance = params.get('test_instance')
            if not test_instance: return JsonResponse({'error': 'Missing test_instance for 1R prediction'}, status=400)
            model = classification_logic.train_1r(dataset, attributes, target_attribute)
            prediction = classification_logic.predict_1r(model, test_instance)
            return JsonResponse({'task': 'Rule-Based (1R)', 'params': params, 'model': model, 'prediction': prediction})

        elif task == 'linear_regression':
            independent_attr = params.get('independent_attribute')
            dependent_attr = params.get('dependent_attribute')
            if not all([independent_attr, dependent_attr]): return JsonResponse({'error': 'Missing independent or dependent attribute'}, status=400)
            model = classification_logic.train_linear_regression(dataset, independent_attr, dependent_attr)
            return JsonResponse({'task': 'Simple Linear Regression', 'params': params, 'model': model})

        elif task == 'ann_perceptron':
            learning_rate = params.get('learning_rate', 0.1)
            epochs = params.get('epochs', 100)
            model = classification_logic.train_perceptron(dataset, attributes, target_attribute, learning_rate, epochs)
            return JsonResponse({'task': 'ANN (Single Perceptron)', 'params': params, 'model': model})

        else:
            return JsonResponse({'error': f'Unknown classification task: {task}'}, status=400)

    except (json.JSONDecodeError, FileNotFoundError, ValueError, KeyError, IndexError) as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)