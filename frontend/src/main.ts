import 'zone.js';  
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app/app.component';


bootstrapApplication(AppComponent, {
providers: [
provideAnimations(),
provideHttpClient(),
provideRouter([])
]
}).catch(err => console.error(err));