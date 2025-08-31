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
  selector: 'app-classify-dialog',
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
    <h2 mat-dialog-title>Classification & Metrics</h2>
    <div mat-dialog-content [formGroup]="form">
      <mat-form-field class="full" appearance="outline">
        <mat-label>Algorithm</mat-label>
        <mat-select formControlName="task" required>
          <mat-option value="decision_tree">Decision Tree (Entropy/Gain Ratio/Gini)</mat-option>
          <mat-option value="knn">k-NN</mat-option>
          <mat-option value="rule_based_1r">Rule-based (1R)</mat-option>
          <mat-option value="linear_regression">Regression (Simple Linear)</mat-option>
          <mat-option value="naive_bayes">Naïve Bayesian (Gaussian)</mat-option>
          <mat-option value="ann_perceptron">ANN (Single Perceptron)</mat-option>
        </mat-select>
      </mat-form-field>

      <!-- Target attribute for most classifiers -->
      <mat-form-field class="full" appearance="outline" *ngIf="form.value.task!=='linear_regression'">
        <mat-label>Target attribute</mat-label>
        <mat-select formControlName="target_attribute">
          <mat-option *ngFor="let col of data.columns" [value]="col">{{ col }}</mat-option>
        </mat-select>
      </mat-form-field>

      <!-- Decision Tree options -->
      <div *ngIf="form.value.task==='decision_tree'">
        <mat-form-field appearance="outline" class="half">
          <mat-label>Split criterion</mat-label>
          <mat-select formControlName="split_criterion">
            <mat-option value="information_gain">Entropy (Information Gain)</mat-option>
            <mat-option value="gain_ratio">Gain Ratio</mat-option>
            <mat-option value="gini_index">Gini Index</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <!-- kNN options -->
      <div *ngIf="form.value.task==='knn'">
        <mat-form-field class="half" appearance="outline">
          <mat-label>k</mat-label>
          <input matInput type="number" formControlName="k" />
        </mat-form-field>
        <mat-form-field class="full" appearance="outline">
          <mat-label>Test instance (JSON)</mat-label>
          <textarea matInput rows="4" formControlName="test_instance" 
            placeholder='{"sepal_length": 5.1, "sepal_width": 3.5}'></textarea>
        </mat-form-field>
      </div>

      <!-- Naive Bayes options -->
      <div *ngIf="form.value.task==='naive_bayes'">
        <mat-form-field class="full" appearance="outline">
          <mat-label>Test instance (JSON)</mat-label>
          <textarea matInput rows="4" formControlName="test_instance" 
            placeholder='{"feature1": 1.2, "feature2": 3.4}'></textarea>
        </mat-form-field>
      </div>

      <!-- Rule-based 1R options -->
      <div *ngIf="form.value.task==='rule_based_1r'">
        <mat-form-field class="full" appearance="outline">
          <mat-label>Test instance (JSON)</mat-label>
          <textarea matInput rows="4" formControlName="test_instance" 
            placeholder='{"feature1": "value"}'></textarea>
        </mat-form-field>
      </div>

      <!-- Linear Regression options -->
      <div *ngIf="form.value.task==='linear_regression'">
        <mat-form-field class="half" appearance="outline">
          <mat-label>Independent attribute (X)</mat-label>
          <mat-select formControlName="independent_attribute">
            <mat-option *ngFor="let col of data.columns" [value]="col">{{ col }}</mat-option>
          </mat-select>
        </mat-form-field>
        <mat-form-field class="half" appearance="outline">
          <mat-label>Dependent attribute (Y)</mat-label>
          <mat-select formControlName="dependent_attribute">
            <mat-option *ngFor="let col of data.columns" [value]="col">{{ col }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Perceptron options -->
      <div *ngIf="form.value.task==='ann_perceptron'">
        <mat-form-field class="half" appearance="outline">
          <mat-label>Learning rate</mat-label>
          <input matInput type="number" formControlName="learning_rate" />
        </mat-form-field>
        <mat-form-field class="half" appearance="outline">
          <mat-label>Epochs</mat-label>
          <input matInput type="number" formControlName="epochs" />
        </mat-form-field>
      </div>

      <div class="mt"></div>
      <button mat-raised-button color="primary" (click)="run()" [disabled]="!form.valid">Run</button>
    </div>

    <div mat-dialog-content *ngIf="result()">
      <h3>Result</h3>

      <div class="metrics" *ngIf="isObject(result()) && hasMetrics(result())">
        <mat-card class="metric-card" *ngFor="let key of metricKeys(result())">
          <mat-card-title>{{ formatKey(key) }}</mat-card-title>
          <mat-card-content>{{ result()[key] }}</mat-card-content>
        </mat-card>
      </div>

      <pre *ngIf="!hasMetrics(result())" style="white-space: pre-wrap;">
        {{ result() | json }}
      </pre>
    </div>

    <div mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Close</button>
    </div>
  `,
  styles: [`
    .full { width: 100%; }
    .half { width: 49%; margin-right: 1%; }
    .mt { margin-top: 12px; }
    .metrics { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; }
    .metric-card { flex: 1 1 150px; text-align: center; padding: 1rem; }
  `]
})
export class ClassifyDialogComponent {
  private api = inject(ApiService);
  private snack = inject(MatSnackBar);

  filename = signal<string>('');
  result = signal<any | null>(null);
  fb = inject(FormBuilder);

  form = this.fb.group({
    filename: this.fb.control('', { nonNullable: true, validators: [Validators.required] }),
    task: this.fb.control<string | null>(null, { validators: [Validators.required] }),
    target_attribute: this.fb.control<string>(''),
    split_criterion: this.fb.control<string>('information_gain'),
    k: this.fb.control<number>(3),
    test_instance: this.fb.control<string>(''),
    independent_attribute: this.fb.control<string>(''),
    dependent_attribute: this.fb.control<string>(''),
    learning_rate: this.fb.control<number>(0.1),
    epochs: this.fb.control<number>(100)
  });

  constructor(@Inject(MAT_DIALOG_DATA) public data: { filename: string, columns: string[] }) {
    this.filename.set(data.filename);
    this.form.patchValue({ filename: data.filename });
  }

  run() {
    const v = this.form.getRawValue();
    const payload: any = { filename: v.filename, task: v.task, params: {} };

    if (v.task === 'decision_tree') {
      payload.params = { target_attribute: v.target_attribute, split_criterion: v.split_criterion };
    } else if (v.task === 'knn') {
      let ti: any = {};
      try { ti = v.test_instance ? JSON.parse(v.test_instance) : {}; } catch { ti = {}; }
      payload.params = { target_attribute: v.target_attribute, k: v.k, test_instance: ti };
    } else if (v.task === 'naive_bayes') {
      let ti: any = {};
      try { ti = v.test_instance ? JSON.parse(v.test_instance) : {}; } catch { ti = {}; }
      payload.params = { target_attribute: v.target_attribute, test_instance: ti };
    } else if (v.task === 'rule_based_1r') {
      let ti: any = {};
      try { ti = v.test_instance ? JSON.parse(v.test_instance) : {}; } catch { ti = {}; }
      payload.params = { target_attribute: v.target_attribute, test_instance: ti };
    } else if (v.task === 'linear_regression') {
      payload.params = { independent_attribute: v.independent_attribute, dependent_attribute: v.dependent_attribute };
    } else if (v.task === 'ann_perceptron') {
      payload.params = { target_attribute: v.target_attribute, learning_rate: v.learning_rate, epochs: v.epochs };
    }

    this.api.classify(payload).subscribe({
      next: (res) => this.result.set(res),
      error: (err) => this.snack.open(err?.error?.error ?? 'Failed', 'Close', { duration: 3000 })
    });
  }

  // Helpers for card-style summary
  isObject(val: any): boolean {
    return val && typeof val === 'object' && !Array.isArray(val);
  }

  hasMetrics(res: any): boolean {
    if (!this.isObject(res)) return false;
    const keys = Object.keys(res);
    return keys.some(k =>
      ['accuracy','precision','recall','f1','rmse','mae','r2'].includes(k.toLowerCase())
    );
  }

  metricKeys(res: any): string[] {
    return Object.keys(res).filter(k =>
      ['accuracy','precision','recall','f1','rmse','mae','r2'].includes(k.toLowerCase())
    );
  }

  formatKey(key: string): string {
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }
}
