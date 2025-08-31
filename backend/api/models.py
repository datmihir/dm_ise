from django.db import models

class Dataset(models.Model):
    """
    Represents an uploaded dataset file.
    """
    filename = models.CharField(max_length=255, unique=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    columns = models.JSONField(default=list)

    def __str__(self):
        return self.filename

class AnalysisResult(models.Model):
    """
    Logs the result of a pre-processing or classification task.
    """
    dataset = models.ForeignKey(Dataset, related_name='analyses', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    task_parameters = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    analysis_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_name} on {self.dataset.filename}"
