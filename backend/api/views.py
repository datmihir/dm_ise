from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
import csv
import json
from .models import Dataset, AnalysisResult
from . import processing_logic, classification_logic
from . import evaluation_logic

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('dataset'):
        uploaded_file = request.FILES['dataset']
        fs = FileSystemStorage()
        
        if fs.exists(uploaded_file.name):
            fs.delete(uploaded_file.name)
            
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, [])
            
            dataset, created = Dataset.objects.update_or_create(
                filename=filename,
                defaults={'columns': header}
            )
        except Exception as e:
            return JsonResponse({'error': f'Could not process CSV headers: {str(e)}'}, status=400)

        return JsonResponse({
            'message': f'File "{filename}" uploaded successfully.',
            'file_url': fs.url(filename),
            'dataset_id': dataset.id
        }, status=201)
        
    return JsonResponse({'error': 'Invalid request method or no file provided.'}, status=400)

def preview_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(file_path): return JsonResponse({'error': 'File not found.'}, status=404)
    try:
        preview_data, header = [], []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            if header is None: return JsonResponse({'error': 'Cannot read header.'}, status=400)
            for i, row in enumerate(reader):
                if i >= 20: break
                preview_data.append({header[j]: cell for j, cell in enumerate(row)})
        return JsonResponse({'filename': filename, 'header': header, 'data': preview_data})
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def process_data(request):
    if request.method != 'POST': return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    try:
        body = json.loads(request.body)
        filename, task = body.get('filename'), body.get('task')
        if not all([filename, task]): return JsonResponse({'error': 'Missing filename or task'}, status=400)
        
        try:
            dataset_obj = Dataset.objects.get(filename=filename)
        except Dataset.DoesNotExist:
            return JsonResponse({'error': 'Dataset not found in database.'}, status=404)

        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        result = {}

        if task in ['central_tendency', 'dispersion_of_data']:
            column = body.get('column')
            if not column: return JsonResponse({'error': 'Missing column name'}, status=400)
            data = processing_logic.load_column_data(file_path, column)
            if task == 'central_tendency':
                result = {'task': 'Measures of Central Tendency', 'column': column, 'mean': round(processing_logic.calculate_mean(data), 4), 'median': round(processing_logic.calculate_median(data), 4), 'mode': processing_logic.calculate_mode(data)}
            elif task == 'dispersion_of_data':
                result = {'task': 'Dispersion of Data', 'column': column, 'variance': round(processing_logic.calculate_variance(data), 4), 'standard_deviation': round(processing_logic.calculate_std_dev(data), 4)}

        elif task == 'correlation_covariance':
            col1, col2 = body.get('column1'), body.get('column2')
            if not all([col1, col2]): return JsonResponse({'error': 'Missing column1 or column2'}, status=400)
            data1, data2 = processing_logic.load_column_data(file_path, col1), processing_logic.load_column_data(file_path, col2)
            result = {'task': 'Correlation and Covariance', 'columns': f'{col1} and {col2}', 'covariance': round(processing_logic.calculate_covariance(data1, data2), 4), 'correlation_coefficient': round(processing_logic.calculate_correlation(data1, data2), 4)}

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
            result = {'task': task, 'column': column, 'processed_data': result_data[:100]}

        elif task == 'data_cleaning':
            method = body.get('params', {}).get('method')
            if not method: return JsonResponse({'error': 'Missing cleaning method'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            if method == 'fill_mean':
                column = body.get('column')
                if not column: return JsonResponse({'error': 'Missing column for fill_mean'}, status=400)
                result_data = processing_logic.handle_missing_values(dataset, method, column)
            else: result_data = processing_logic.handle_missing_values(dataset, method)
            result = {'task': 'Data Cleaning', 'method': method, 'rows_before': len(dataset), 'rows_after': len(result_data), 'processed_data': result_data[:100]}

        elif task == 'chi_square_test':
            col1, col2 = body.get('column1'), body.get('column2')
            if not all([col1, col2]): return JsonResponse({'error': 'Missing column1 or column2'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            statistic, df, table = processing_logic.calculate_chi_square(dataset, col1, col2)
            result = {'task': 'Chi-square Test', 'columns': f'{col1} and {col2}', 'chi_square_statistic': round(statistic, 4), 'degrees_of_freedom': df, 'contingency_table': table}

        elif task == 'visualization':
            params = body.get('params', {})
            chart_type = params.get('chart_type')
            if not chart_type: return JsonResponse({'error': 'Missing chart_type'}, status=400)
            dataset = processing_logic.load_full_data(file_path)
            if chart_type == 'histogram':
                column = body.get('column')
                num_bins = params.get('num_bins', 10)
                chart_data = processing_logic.prepare_histogram_data(dataset, column, num_bins)
                result = {'task': 'Visualization', 'chart_type': 'histogram', 'chart_data': chart_data}
            elif chart_type == 'scatter_plot':
                col1, col2 = body.get('column1'), body.get('column2')
                chart_data = processing_logic.prepare_scatter_plot_data(dataset, col1, col2)
                result = {'task': 'Visualization', 'chart_type': 'scatter_plot', 'chart_data': chart_data}

        elif task == 'clustering':
            # params: algorithm ('kmeans'|'kmedoid'), columns: [col1,col2,..], k, max_iter
            params = body.get('params', {})
            algo = params.get('algorithm')
            columns = params.get('columns', [])
            k = int(params.get('k', 3))
            max_iter = int(params.get('max_iter', 100))
            dataset = processing_logic.load_full_data(file_path)
            if not columns:
                return JsonResponse({'error': 'Missing columns for clustering'}, status=400)
            if algo == 'kmeans':
                result = processing_logic.k_means(dataset, columns, k=k, max_iter=max_iter)
            elif algo == 'kmedoid' or algo == 'k-medoid':
                result = processing_logic.k_medoid(dataset, columns, k=k, max_iter=max_iter)
            else:
                return JsonResponse({'error': 'Unknown clustering algorithm'}, status=400)

        elif task == 'apriori':
            params = body.get('params', {})
            columns = params.get('columns', [])
            min_support = float(params.get('min_support', 0.1))
            min_confidence = float(params.get('min_confidence', 0.6))
            max_len = int(params.get('max_len', 3))
            dataset = processing_logic.load_full_data(file_path)
            if not columns:
                return JsonResponse({'error': 'Missing columns for apriori'}, status=400)
            result = processing_logic.apriori(dataset, columns, min_support=min_support, min_confidence=min_confidence, max_len=max_len)

        elif task == 'pagerank':
            params = body.get('params', {})
            source_col = params.get('source_column')
            target_col = params.get('target_column')
            damping = float(params.get('damping', 0.85))
            dataset = processing_logic.load_full_data(file_path)
            if not all([source_col, target_col]):
                return JsonResponse({'error': 'Missing source_column or target_column for pagerank'}, status=400)
            result = processing_logic.pagerank_from_edges(dataset, source_col, target_col, damping=damping)

        elif task == 'hits':
            params = body.get('params', {})
            source_col = params.get('source_column')
            target_col = params.get('target_column')
            dataset = processing_logic.load_full_data(file_path)
            if not all([source_col, target_col]):
                return JsonResponse({'error': 'Missing source_column or target_column for hits'}, status=400)
            result = processing_logic.hits_from_edges(dataset, source_col, target_col)

        if result:
            AnalysisResult.objects.create(dataset=dataset_obj, task_name=task, task_parameters=body, result=result)
        
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@csrf_exempt
def classify_data(request):
    if request.method != 'POST': return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    try:
        body = json.loads(request.body)
        filename, task = body.get('filename'), body.get('task')
        params = body.get('params', {})
        if not all([filename, task, params]): return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        try:
            dataset_obj = Dataset.objects.get(filename=filename)
        except Dataset.DoesNotExist:
            return JsonResponse({'error': 'Dataset not found in database.'}, status=404)

        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        dataset = processing_logic.load_full_data(file_path)
        target_attribute = params.get('target_attribute')
        if not target_attribute and task not in ['linear_regression']: 
            return JsonResponse({'error': 'Missing target_attribute in params'}, status=400)
        
        attributes = [key for key in dataset[0].keys() if key != target_attribute] if target_attribute else []
        result = {}

        if task == 'decision_tree':
            split_criterion = params.get('split_criterion', 'information_gain')
            processed_data = classification_logic.preprocess_for_tree(dataset, attributes)
            model = classification_logic.build_decision_tree(processed_data, attributes, target_attribute, split_criterion)
            result = {'task': 'Decision Tree', 'params': params, 'model': model}

        elif task == 'knn':
            k = params.get('k', 3)
            test_instance = params.get('test_instance')
            if not test_instance: return JsonResponse({'error': 'Missing test_instance'}, status=400)
            for key, val in test_instance.items():
                try: test_instance[key] = float(val)
                except (ValueError, TypeError): pass
            prediction, neighbors = classification_logic.predict_knn(dataset, test_instance, k, attributes, target_attribute)
            result = {'task': 'k-Nearest Neighbors', 'params': params, 'prediction': prediction, 'nearest_neighbors': neighbors}

        elif task == 'naive_bayes':
            test_instance = params.get('test_instance')
            if not test_instance: return JsonResponse({'error': 'Missing test_instance'}, status=400)
            for key, val in test_instance.items():
                try: test_instance[key] = float(val)
                except (ValueError, TypeError): pass
            model = classification_logic.train_naive_bayes(dataset, attributes, target_attribute)
            prediction = classification_logic.predict_naive_bayes(model, test_instance, attributes)
            result = {'task': 'Naive Bayesian Classifier', 'params': params, 'prediction': prediction}

        elif task == 'rule_based_1r':
            test_instance = params.get('test_instance')
            if not test_instance: return JsonResponse({'error': 'Missing test_instance'}, status=400)
            processed_data = classification_logic.preprocess_for_tree(dataset, attributes)
            model = classification_logic.train_1r(processed_data, attributes, target_attribute)
            prediction = classification_logic.predict_1r(model, test_instance)
            result = {'task': 'Rule-Based (1R)', 'params': params, 'model': model, 'prediction': prediction}

        elif task == 'linear_regression':
            independent_attr = params.get('independent_attribute')
            dependent_attr = params.get('dependent_attribute')
            if not all([independent_attr, dependent_attr]): return JsonResponse({'error': 'Missing attributes'}, status=400)
            model = classification_logic.train_linear_regression(dataset, independent_attr, dependent_attr)
            result = {'task': 'Simple Linear Regression', 'params': params, 'model': model}

        elif task == 'ann_perceptron':
            learning_rate = params.get('learning_rate', 0.1)
            epochs = params.get('epochs', 100)
            model = classification_logic.train_perceptron(dataset, attributes, target_attribute, learning_rate, epochs)
            result = {'task': 'ANN (Single Perceptron)', 'params': params, 'model': model}

        if result:
            AnalysisResult.objects.create(dataset=dataset_obj, task_name=task, task_parameters=params, result=result)

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


def list_datasets(request):
    """
    Returns a list of all datasets stored in the database.
    """
    datasets = Dataset.objects.all().order_by('-upload_date')
    data = [{
        'id': ds.id,
        'filename': ds.filename,
        'upload_date': ds.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'columns': ds.columns
    } for ds in datasets]
    return JsonResponse(data, safe=False)

def list_dataset_analyses(request, dataset_id):
    """
    Returns a list of all analyses performed on a specific dataset.
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        analyses = dataset.analyses.all().order_by('-analysis_date')
        data = [{
            'id': an.id,
            'task_name': an.task_name,
            'task_parameters': an.task_parameters,
            'result': an.result,
            'analysis_date': an.analysis_date.strftime('%Y-%m-%d %H:%M:%S')
        } for an in analyses]
        return JsonResponse(data, safe=False)
    except Dataset.DoesNotExist:
        return JsonResponse({'error': 'Dataset not found.'}, status=404)

@csrf_exempt
def delete_dataset(request, dataset_id):
    """
    Deletes a dataset record from the database and its corresponding file.
    """
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE method is allowed'}, status=405)

    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        
        file_path = os.path.join(settings.MEDIA_ROOT, dataset.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        dataset.delete()
        
        return JsonResponse({'message': f'Successfully deleted {dataset.filename}'}, status=200)
        
    except Dataset.DoesNotExist:
        return JsonResponse({'error': 'Dataset not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
