import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async'; 
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    // These providers are essential for our app
    provideRouter(routes),
    provideHttpClient(),
    provideAnimationsAsync()
    // By not including provideZoneChangeDetection, our app is zoneless.
  ]
};
