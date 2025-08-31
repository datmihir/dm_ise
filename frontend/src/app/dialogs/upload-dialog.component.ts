import { Component, Inject, inject, signal } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-upload-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatTableModule, MatIconModule, MatProgressBarModule],
  template: `
    <h2 mat-dialog-title>Upload & Preview Dataset</h2>
    <div mat-dialog-content>
      <input type="file" (change)="onFile($event)" accept=".csv" />
      <div *ngIf="uploading()"><mat-progress-bar mode="indeterminate"></mat-progress-bar></div>
      <div *ngIf="filename()" class="info">Uploaded: <b>{{ filename() }}</b></div>

      <div *ngIf="previewCols().length" class="table-wrap">
        <table mat-table [dataSource]="previewRows()" class="mat-elevation-z2">
          <ng-container *ngFor="let col of previewCols()" [matColumnDef]="col">
            <th mat-header-cell *matHeaderCellDef>{{ col }}</th>
            <td mat-cell *matCellDef="let row">{{ row[col] }}</td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="previewCols(); sticky: true"></tr>
          <tr mat-row *matRowDef="let row; columns: previewCols();"></tr>
        </table>
      </div>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Close</button>
      <button mat-raised-button color="primary" [disabled]="!filename()" (click)="done()">Use this dataset</button>
    </div>
  `,
  styles: [`
    .table-wrap { max-height: 420px; overflow: auto; margin-top: 12px; }
    .info { margin-top: 8px; }
    table { width: 100%; }
  `]
})
export class UploadDialogComponent {
  private api = inject(ApiService);
  private dialogRef = inject(MatDialogRef<UploadDialogComponent>);

  filename = signal<string | null>(null);
  uploading = signal(false);
  previewCols = signal<string[]>([]);
  previewRows = signal<any[]>([]);

  onFile(ev: Event) {
    const input = ev.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.uploading.set(true);
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

  done() { this.dialogRef.close({ filename: this.filename()! }); }
}
