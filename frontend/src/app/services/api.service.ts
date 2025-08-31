import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Dataset {
  id: number;
  filename: string;
  upload_date: string;
  columns: string[];
}

export interface Analysis {
  id: number;
  task_name: string;
  task_parameters: Record<string, any>;
  result: any;
  analysis_date: string;
  dataset: number;
}

export interface PreviewResponse {
  filename: string;
  header: string[];
  data: any[];
}

export interface UploadResponse {
  message: string;
  file_url: string;
  dataset_id?: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private readonly BASE_URL = 'http://127.0.0.1:8000/api';

  getDatasets(): Observable<Dataset[]> {
    return this.http.get<Dataset[]>(`${this.BASE_URL}/datasets/`);
  }

  getAnalyses(datasetId: number): Observable<Analysis[]> {
    return this.http.get<Analysis[]>(`${this.BASE_URL}/datasets/${datasetId}/analyses/`);
  }

  upload(file: File): Observable<UploadResponse> {
    const form = new FormData();
    form.append('dataset', file);
    return this.http.post<UploadResponse>(`${this.BASE_URL}/upload/`, form);
  }

  preview(filename: string): Observable<PreviewResponse> {
    return this.http.get<PreviewResponse>(
      `${this.BASE_URL}/preview/${encodeURIComponent(filename)}/`
    );
  }

  process(payload: any): Observable<any> {
    return this.http.post<any>(`${this.BASE_URL}/process/`, payload);
  }

  classify(payload: any): Observable<any> {
    return this.http.post<any>(`${this.BASE_URL}/classify/`, payload);
  }
  deleteDataset(datasetId: number) {
    return this.http.delete<any>(`${this.BASE_URL}/datasets/${datasetId}/delete/`);
  }
}
