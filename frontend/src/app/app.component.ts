// File: src/app/app.component.ts
import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ApiService } from './services/api.service';
import { PreprocessDialogComponent } from './dialogs/preprocess-dialog.component';
import { ClassifyDialogComponent } from './dialogs/classify-dialog.component';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatDialogModule, MatProgressBarModule, MatTableModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  private api = inject(ApiService);
  private dialog = inject(MatDialog);

  filename = signal<string | null>(null);
  previewCols = signal<string[]>([]);
  previewRows = signal<any[]>([]);
  uploading = signal(false);

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

  openPreprocess() {
    this.dialog.open(PreprocessDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      disableClose: true,
      data: { filename: this.filename() }
    });
  }

  openClassify() {
    this.dialog.open(ClassifyDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      disableClose: true,
      data: { filename: this.filename() }
    });
  }
}

