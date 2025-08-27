// ------------------------------------------------------
// file: src/app/dialogs/visualization-dialog.component.ts
// ------------------------------------------------------
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { NgxChartsModule } from '@swimlane/ngx-charts';

@Component({
  selector: 'app-visualization-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, NgxChartsModule],
  template: `
    <h2 mat-dialog-title>Chart Visualization</h2>
    <div mat-dialog-content class="chart-container">
      <ng-container [ngSwitch]="data.chart_type">
        
        <!-- Histogram -->
        <ngx-charts-bar-vertical
          *ngSwitchCase="'histogram'"
          [results]="chartData"
          [xAxis]="true"
          [yAxis]="true"
          [legend]="false"
          [xAxisLabel]="data.params.column"
          yAxisLabel="Frequency">
        </ngx-charts-bar-vertical>

        <!-- Scatter Plot (implemented with bubble chart) -->
        <ngx-charts-bubble-chart
          *ngSwitchCase="'scatter_plot'"
          [results]="chartData"
          [xAxis]="true"
          [yAxis]="true"
          [legend]="true"
          [xAxisLabel]="data.params.column1"
          [yAxisLabel]="data.params.column2">
        </ngx-charts-bubble-chart>

      </ng-container>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Close</button>
    </div>
  `,
  styles: [`
    .chart-container {
      height: 500px;
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  `]
})
export class VisualizationDialogComponent {
  chartData: any[] = [];

  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {
    // Format the backend data into the format ngx-charts expects
    if (data.chart_type === 'histogram') {
      this.chartData = data.chart_data.labels.map((label: string, index: number) => ({
        name: label,
        value: data.chart_data.counts[index]
      }));
    } else if (data.chart_type === 'scatter_plot') {
      this.chartData = [{
        name: `${data.params.column1} vs ${data.params.column2}`,
        series: data.chart_data.map((point: any, index: number) => ({
          name: `${index}`,  // required string identifier
          x: point.x,
          y: point.y,
          r: 5               // constant radius to mimic scatter plot
        }))
      }];
    }
  }
}
