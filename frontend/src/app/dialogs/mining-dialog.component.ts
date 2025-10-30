import { Component, Inject, inject, signal } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-mining-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatSnackBarModule,
    MatCardModule
  ],
  template: `
    <h2 mat-dialog-title>Data Mining</h2>
    <div mat-dialog-content [formGroup]="form">
      <mat-form-field class="full" appearance="outline">
        <mat-label>Task</mat-label>
        <mat-select formControlName="task" required>
          <mat-option value="clustering">Clustering (k-Means / k-Medoid)</mat-option>
          <mat-option value="apriori">Apriori Association Rules</mat-option>
          <mat-option value="pagerank">PageRank</mat-option>
          <mat-option value="hits">HITS (Hubs & Authorities)</mat-option>
        </mat-select>
      </mat-form-field>

      <!-- Clustering options -->
      <div *ngIf="form.value.task==='clustering'">
        <mat-form-field class="full" appearance="outline">
          <mat-label>Algorithm</mat-label>
          <mat-select formControlName="algorithm">
            <mat-option value="kmeans">k-Means</mat-option>
            <mat-option value="kmedoid">k-Medoid</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field class="full" appearance="outline">
          <mat-label>Columns (comma separated)</mat-label>
          <input matInput formControlName="columns" placeholder="col1,col2" />
        </mat-form-field>

        <mat-form-field class="half" appearance="outline">
          <mat-label>k (clusters)</mat-label>
          <input matInput type="number" formControlName="k" />
        </mat-form-field>
      </div>

      <!-- Apriori options -->
      <div *ngIf="form.value.task==='apriori'">
        <mat-form-field class="full" appearance="outline">
          <mat-label>Columns (comma separated)</mat-label>
          <input matInput formControlName="columns" placeholder="col1,col2" />
        </mat-form-field>
        <mat-form-field class="half" appearance="outline">
          <mat-label>Min Support</mat-label>
          <input matInput type="number" step="0.01" formControlName="min_support" />
        </mat-form-field>
        <mat-form-field class="half" appearance="outline">
          <mat-label>Min Confidence</mat-label>
          <input matInput type="number" step="0.01" formControlName="min_confidence" />
        </mat-form-field>
      </div>

      <!-- Graph mining options -->
      <div *ngIf="form.value.task==='pagerank' || form.value.task==='hits'">
        <mat-form-field class="full" appearance="outline">
          <mat-label>Source Column</mat-label>
          <mat-select formControlName="source_column">
            <mat-option *ngFor="let col of data.columns" [value]="col">{{ col }}</mat-option>
          </mat-select>
        </mat-form-field>
        <mat-form-field class="full" appearance="outline">
          <mat-label>Target Column</mat-label>
          <mat-select formControlName="target_column">
            <mat-option *ngFor="let col of data.columns" [value]="col">{{ col }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <div class="mt"></div>
      <button mat-raised-button color="primary" (click)="run()" [disabled]="!form.valid">Run</button>
    </div>

    <div mat-dialog-content *ngIf="result()">
      <h3>Result</h3>
      <pre style="white-space: pre-wrap;">{{ result() | json }}</pre>
    </div>

    <div mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Close</button>
    </div>
  `,
  styles: [`
    .full { width: 100%; }
    .half { width: 49%; margin-right: 1%; }
    .mt { margin-top: 12px; }
  `]
})
export class MiningDialogComponent {
  private api = inject(ApiService);
  private snack = inject(MatSnackBar);

  filename = signal<string>('');
  result = signal<any | null>(null);
  fb = inject(FormBuilder);

  form = this.fb.group({
    filename: this.fb.control('', { nonNullable: true, validators: [Validators.required] }),
    task: this.fb.control<string | null>(null, { validators: [Validators.required] }),
    algorithm: this.fb.control<string>('kmeans'),
    columns: this.fb.control<string>(''),
    k: this.fb.control<number>(3),
    min_support: this.fb.control<number>(0.1),
    min_confidence: this.fb.control<number>(0.6),
    source_column: this.fb.control<string>(''),
    target_column: this.fb.control<string>('')
  });

  constructor(@Inject(MAT_DIALOG_DATA) public data: { filename: string, columns: string[] }) {
    this.filename.set(data.filename);
    this.form.patchValue({ filename: data.filename });
  }

  run() {
    const v = this.form.getRawValue();
    const payload: any = { filename: v.filename, task: v.task, params: {} };

    if (v.task === 'clustering') {
      const cols = (v.columns ?? '').split(',').map((s: string) => s.trim()).filter((s: string) => s);
      payload.params = { algorithm: v.algorithm, columns: cols, k: v.k };
    } else if (v.task === 'apriori') {
      const cols = (v.columns ?? '').split(',').map((s: string) => s.trim()).filter((s: string) => s);
      payload.params = { columns: cols, min_support: v.min_support, min_confidence: v.min_confidence };
    } else if (v.task === 'pagerank' || v.task === 'hits') {
      payload.params = { source_column: v.source_column, target_column: v.target_column };
    }

    this.api.process(payload).subscribe({
      next: (res) => this.result.set(res),
      error: (err) => this.snack.open(err?.error?.error ?? 'Failed', 'Close', { duration: 3000 })
    });
  }
}
