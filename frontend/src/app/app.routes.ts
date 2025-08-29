import { Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { UploadDialogComponent } from './dialogs/upload-dialog.component';
import { PreprocessDialogComponent } from './dialogs/preprocess-dialog.component';
import { ClassifyDialogComponent } from './dialogs/classify-dialog.component';

export const routes: Routes = [
  { path: '', component: AppComponent },
  { path: 'upload', component: UploadDialogComponent },
  { path: 'preprocess', component: PreprocessDialogComponent },
  { path: 'classify', component: ClassifyDialogComponent },
];
