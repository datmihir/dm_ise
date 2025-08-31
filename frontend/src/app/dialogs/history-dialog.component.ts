import { Component, Inject, inject, signal, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule, JsonPipe } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-history-dialog',
  standalone: true,
  imports: [
    CommonModule,
    JsonPipe,
    MatDialogModule,
    MatButtonModule,
    MatExpansionModule,
    MatListModule,
    MatIconModule
  ],
  template: `
    <h2 mat-dialog-title>Analysis History for {{ dataset.filename }}</h2>
    <div mat-dialog-content>
      <mat-accordion *ngIf="analyses().length > 0; else noHistory">
        <mat-expansion-panel *ngFor="let analysis of analyses()">
          <mat-expansion-panel-header>
            <mat-panel-title>
              <strong>{{ analysis.task_name }}</strong>
            </mat-panel-title>
            <mat-panel-description>
              {{ analysis.analysis_date }}
            </mat-panel-description>
          </mat-expansion-panel-header>

          <h4>Parameters</h4>
          <pre>{{ analysis.task_parameters | json }}</pre>

          <h4>Result</h4>
          <pre>{{ analysis.result | json }}</pre>
        </mat-expansion-panel>
      </mat-accordion>

      <ng-template #noHistory>
        <p class="empty-state">No analyses have been run on this dataset yet.</p>
      </ng-template>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Close</button>
    </div>
  `,
  styles: [`
    pre {
      background-color: #f5f5f5;
      padding: 1rem;
      border-radius: 4px;
      white-space: pre-wrap;
    }
    .empty-state {
      text-align: center;
      color: #888;
      padding: 2rem;
    }
  `]
})
export class HistoryDialogComponent implements OnInit {
  private api = inject(ApiService);
  private snackBar = inject(MatSnackBar);

  analyses = signal<any[]>([]);

  constructor(@Inject(MAT_DIALOG_DATA) public dataset: { id: number, filename: string }) {}

  ngOnInit() {
    this.api.getAnalyses(this.dataset.id).subscribe({
      next: (data) => this.analyses.set(data),
      error: () => this.snackBar.open('Could not load analysis history.', 'Close', { duration: 3000 })
    });
  }
}
