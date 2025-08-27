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
  filename = signal<string | null>(null);
  previewCols = signal<string[]>([]);
  previewRows = signal<any[]>([]);
  uploading = signal(false);

  // --- Theme ---
  isDarkMode = signal(false);

  ngOnInit() {
    this.loadDatasets();

    // Optional: check for user's system preference for dark mode
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      this.toggleTheme();
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
    this.filename.set(dataset.filename);
  }

  // ✅ File upload via hidden <input type="file">
  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploading.set(true);
    this.filename.set(null);
    this.previewCols.set([]);
    this.previewRows.set([]);

    this.api.upload(file).subscribe({
      next: (res) => {
        const parts = res.file_url.split('/');
        const fn = decodeURIComponent(parts[parts.length - 1]);
        this.filename.set(fn);

        this.loadDatasets();

        this.api.preview(fn).subscribe({
          next: (p) => {
            this.previewCols.set(p.header);
            this.previewRows.set(p.data);
            this.uploading.set(false);
          },
          error: () => this.uploading.set(false)
        });
      },
      error: () => this.uploading.set(false)
    });
  }

  // ✅ Upload via Dialog
  openUploadDialog() {
    const dialogRef = this.dialog.open(UploadDialogComponent, { width: '500px' });
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
      data: { filename: this.selectedDataset()!.filename }
    });
  }

  openClassify() {
    if (!this.selectedDataset()) return;
    this.dialog.open(ClassifyDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      disableClose: true,
      data: { filename: this.selectedDataset()!.filename }
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
      this.renderer.addClass(document.body, 'dark-theme');
    } else {
      this.renderer.removeClass(document.body, 'dark-theme');
    }
  }
}
