// File: src/app/app.component.ts
import { Component, signal, WritableSignal, inject, OnInit, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ApiService, Dataset } from './services/api.service';
import { PreprocessDialogComponent } from './dialogs/preprocess-dialog.component';
import { ClassifyDialogComponent } from './dialogs/classify-dialog.component';
import { UploadDialogComponent } from './dialogs/upload-dialog.component';
import { HistoryDialogComponent } from './dialogs/history-dialog.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatDialogModule,
    MatSnackBarModule,
    MatProgressBarModule,
    MatTableModule,
    MatIconModule,
    MatListModule,
    MatTooltipModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  private api = inject(ApiService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private renderer = inject(Renderer2);

  // --- Dataset Library ---
  datasets: WritableSignal<Dataset[]> = signal<Dataset[]>([]);
  selectedDataset: WritableSignal<Dataset | null> = signal<Dataset | null>(null);

  // --- Upload & Preview ---
  previewCols = signal<string[]>([]);
  previewRows = signal<any[]>([]);
  uploading = signal(false);

  // --- Theme ---
  isDarkMode = signal(false);

  ngOnInit() {
    this.loadDatasets();
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      this.isDarkMode.set(true);
      this.renderer.addClass(document.body, 'dark-mode');
    }
  }

  loadDatasets() {
    this.api.getDatasets().subscribe({
      next: (data) => this.datasets.set(data),
      error: () =>
        this.snackBar.open('Could not load datasets.', 'Close', { duration: 3000 })
    });
  }

  selectDataset(dataset: Dataset) {
    this.selectedDataset.set(dataset);
    // --- THIS IS THE KEY CHANGE ---
    // Fetch the preview for the selected dataset
    this.fetchPreview(dataset.filename);
  }

  // --- NEW HELPER FUNCTION TO FETCH PREVIEW ---
  fetchPreview(filename: string) {
    this.uploading.set(true);
    this.api.preview(filename).subscribe({
      next: (p) => {
        this.previewCols.set(p.header);
        this.previewRows.set(p.data.slice(0, 10)); // only first 10 rows
        this.uploading.set(false);
      },
      error: () => {
          this.snackBar.open(`Could not load preview for ${filename}`, 'Close', { duration: 3000 });
          this.uploading.set(false);
      }
    });
  }

  // ✅ Upload via Dialog
  openUploadDialog() {
    const dialogRef = this.dialog.open(UploadDialogComponent, { width: '800px' });
    dialogRef.afterClosed().subscribe(result => {
      if (result?.filename) {
        this.snackBar.open(`Successfully uploaded ${result.filename}`, 'Close', {
          duration: 3000
        });
        this.loadDatasets();
      }
    });
  }

  // ✅ Actions
  openPreprocess() {
    if (!this.selectedDataset()) return;
    this.dialog.open(PreprocessDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      disableClose: true,
      data: { 
        filename: this.selectedDataset()!.filename,
        columns: this.selectedDataset()!.columns
      }
    });
  }

  openClassify() {
    if (!this.selectedDataset()) return;
    this.dialog.open(ClassifyDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      disableClose: true,
      data: { 
        filename: this.selectedDataset()!.filename,
        columns: this.selectedDataset()!.columns
      }
    });
  }

  openHistory() {
    if (!this.selectedDataset()) return;
    this.dialog.open(HistoryDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      data: this.selectedDataset()
    });
  }

  // ✅ Theme toggle
  toggleTheme() {
    this.isDarkMode.update(value => !value);
    if (this.isDarkMode()) {
      this.renderer.addClass(document.body, 'dark-mode');
      localStorage.setItem('theme', 'dark');
    } else {
      this.renderer.removeClass(document.body, 'dark-mode');
      localStorage.setItem('theme', 'light');
    }
  }

  deleteDataset(event: MouseEvent, datasetId: number) {
    event.stopPropagation(); // Prevents the list item's click event from firing

    if (confirm('Are you sure you want to delete this dataset? This action cannot be undone.')) {
      this.api.deleteDataset(datasetId).subscribe({
        next: () => {
          this.snackBar.open('Dataset deleted successfully.', 'Close', { duration: 3000 });
          this.loadDatasets();
          this.selectedDataset.set(null); // Deselect if it was the active one
        },
        error: (err) => {
          this.snackBar.open(err?.error?.error ?? 'Failed to delete dataset.', 'Close', { duration: 3000 });
        }
      });
    }
  }
}