// ------------------------------------------------------
// file: src/app/dialogs/preprocess-dialog.component.ts
// ------------------------------------------------------
import { Component, Inject, inject, signal, effect } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-preprocess-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatButtonModule, MatTableModule, MatSnackBarModule],
  template: `
    <h2 mat-dialog-title>Preprocessing</h2>
    <div mat-dialog-content [formGroup]="form">
      <mat-form-field appearance="outline" class="full">
        <mat-label>Task</mat-label>
        <mat-select formControlName="task" required>
          <mat-option value="central_tendency">Statistical description (Central Tendency)</mat-option>
          <mat-option value="dispersion_of_data">Dispersion of data</mat-option>
          <mat-option value="data_cleaning">Data cleaning</mat-option>
          <mat-option value="chi_square_test">Chi-square test</mat-option>
          <mat-option value="correlation_covariance">Correlation & Covariance</mat-option>
          <mat-option value="normalize_min_max">Normalization – Min-Max</mat-option>
          <mat-option value="normalize_z_score">Normalization – Z-Score</mat-option>
          <mat-option value="normalize_decimal_scaling">Normalization – Decimal Scaling</mat-option>
          <mat-option value="discretize_by_binning">Discretization by binning</mat-option>
          <mat-option value="visualization">Visualization</mat-option>
        </mat-select>
      </mat-form-field>

      <!-- dynamic fields -->
      <ng-container [ngSwitch]="form.value.task">
        <ng-container *ngSwitchCase="'central_tendency'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column</mat-label>
            <input matInput formControlName="column" placeholder="e.g. sepal_length" />
          </mat-form-field>
        </ng-container>

        <ng-container *ngSwitchCase="'dispersion_of_data'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column</mat-label>
            <input matInput formControlName="column" />
          </mat-form-field>
        </ng-container>

        <ng-container *ngSwitchCase="'data_cleaning'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Method</mat-label>
            <mat-select formControlName="method" required>
              <mat-option value="remove_rows">Remove rows with missing</mat-option>
              <mat-option value="fill_mean">Fill mean (for a column)</mat-option>
            </mat-select>
          </mat-form-field>
          <mat-form-field class="half" appearance="outline" *ngIf="form.value.method==='fill_mean'">
            <mat-label>Column</mat-label>
            <input matInput formControlName="column" />
          </mat-form-field>
        </ng-container>

        <ng-container *ngSwitchCase="'chi_square_test'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column 1</mat-label>
            <input matInput formControlName="column1" />
          </mat-form-field>
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column 2</mat-label>
            <input matInput formControlName="column2" />
          </mat-form-field>
        </ng-container>

        <ng-container *ngSwitchCase="'correlation_covariance'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column 1</mat-label>
            <input matInput formControlName="column1" />
          </mat-form-field>
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column 2</mat-label>
            <input matInput formControlName="column2" />
          </mat-form-field>
        </ng-container>

        <ng-container *ngSwitchCase="'discretize_by_binning'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Column</mat-label>
            <input matInput formControlName="column" />
          </mat-form-field>
          <mat-form-field class="half" appearance="outline">
            <mat-label>Number of bins</mat-label>
            <input matInput type="number" formControlName="num_bins" />
          </mat-form-field>
        </ng-container>

        <ng-container *ngSwitchCase="'visualization'">
          <mat-form-field class="half" appearance="outline">
            <mat-label>Chart type</mat-label>
            <mat-select formControlName="chart_type">
              <mat-option value="histogram">Histogram</mat-option>
              <mat-option value="scatter_plot">Scatter Plot</mat-option>
            </mat-select>
          </mat-form-field>
          <mat-form-field class="half" appearance="outline" *ngIf="form.value.chart_type==='histogram'">
            <mat-label>Column</mat-label>
            <input matInput formControlName="column" />
          </mat-form-field>
          <mat-form-field class="half" appearance="outline" *ngIf="form.value.chart_type==='histogram'">
            <mat-label>Bins</mat-label>
            <input matInput type="number" formControlName="num_bins" />
          </mat-form-field>
          <ng-container *ngIf="form.value.chart_type==='scatter_plot'">
            <mat-form-field class="half" appearance="outline">
              <mat-label>X Column</mat-label>
              <input matInput formControlName="column1" />
            </mat-form-field>
            <mat-form-field class="half" appearance="outline">
              <mat-label>Y Column</mat-label>
              <input matInput formControlName="column2" />
            </mat-form-field>
          </ng-container>
        </ng-container>

        <ng-container *ngSwitchDefault>
          <!-- Normalizations expect a column -->
          <mat-form-field class="half" appearance="outline" *ngIf="form.value.task?.startsWith('normalize')">
            <mat-label>Column</mat-label>
            <input matInput formControlName="column" />
          </mat-form-field>
        </ng-container>
      </ng-container>

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
export class PreprocessDialogComponent {
  private api = inject(ApiService);
  private snack = inject(MatSnackBar);

  filename = signal<string>('');
  result = signal<any | null>(null);
  fb = inject(FormBuilder);

  form = this.fb.group({
    filename: this.fb.control('', { nonNullable: true, validators: [Validators.required] }),
    task: this.fb.control<string | null>(null, { validators: [Validators.required] }),
    // Common optional fields used per task branch
    column: this.fb.control<string>(''),
    column1: this.fb.control<string>(''),
    column2: this.fb.control<string>(''),
    method: this.fb.control<string>(''),
    num_bins: this.fb.control<number>(10),
    chart_type: this.fb.control<string>('')
  });

  constructor(@Inject(MAT_DIALOG_DATA) public data: { filename: string }) {
    this.filename.set(data.filename);
    this.form.patchValue({ filename: data.filename });
  }

  run() {
    const v = this.form.getRawValue();
    const payload: any = { filename: v.filename, task: v.task };

    if (v.task === 'central_tendency' || v.task === 'dispersion_of_data') {
      payload.column = v.column;
    } else if (v.task === 'correlation_covariance') {
      payload.column1 = v.column1; payload.column2 = v.column2;
    } else if (v.task?.startsWith('normalize')) {
      payload.column = v.column;
    } else if (v.task === 'discretize_by_binning') {
      payload.column = v.column; payload.params = { num_bins: v.num_bins };
    } else if (v.task === 'data_cleaning') {
      payload.column = v.column; payload.params = { method: v.method };
    } else if (v.task === 'chi_square_test') {
      payload.column1 = v.column1; payload.column2 = v.column2;
    } else if (v.task === 'visualization') {
      payload.params = { chart_type: v.chart_type, num_bins: v.num_bins };
      if (v.chart_type === 'histogram') payload.column = v.column;
      if (v.chart_type === 'scatter_plot') { payload.column1 = v.column1; payload.column2 = v.column2; }
    }

    this.api.process(payload).subscribe({
      next: (res) => this.result.set(res),
      error: (err) => this.snack.open(err?.error?.error ?? 'Failed', 'Close', { duration: 3000 })
    });
  }
}
