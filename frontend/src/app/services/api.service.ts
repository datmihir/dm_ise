import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  // --- THIS IS THE CRITICAL FIX ---
  // The URL must point to your Django backend server, not the Angular one.
  private readonly BASE_URL = 'http://127.0.0.1:8000/api';

  upload(file: File) {
    const form = new FormData();
    form.append('dataset', file);
    return this.http.post<{ message: string; file_url: string }>(`${this.BASE_URL}/upload/`, form);
  }

  preview(filename: string) {
    return this.http.get<{ filename: string; header: string[]; data: any[] }>(`${this.BASE_URL}/preview/${encodeURIComponent(filename)}/`);
  }

  process(payload: any) {
    return this.http.post<any>(`${this.BASE_URL}/process/`, payload);
  }

  classify(payload: any) {
    return this.http.post<any>(`${this.BASE_URL}/classify/`, payload);
  }
}
