import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  effect,
  input,
  viewChild,
} from '@angular/core';
import {
  CategoryScale,
  Chart,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
  type ChartOptions,
} from 'chart.js';

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
);

/** One series of a `LineChart`: a service's per-day values plus the fixed color assigned to it. */
export interface LineChartDataset {
  label: string;
  data: number[];
  color: string;
}

/**
 * Thin Chart.js wrapper: takes plain labels/datasets and renders/updates a
 * line chart. Marks and interaction follow the house dataviz spec -- 2px
 * lines, a shared crosshair tooltip across every series at the hovered x
 * position (`mode: 'index'`), and a legend (never color-only identity)
 * since a service dashboard always has 2+ series.
 */
@Component({
  selector: 'app-line-chart',
  templateUrl: './line-chart.html',
  styleUrl: './line-chart.scss',
})
export class LineChart implements AfterViewInit, OnDestroy {
  labels = input.required<string[]>();
  datasets = input.required<LineChartDataset[]>();
  ariaLabel = input('Line chart');

  private readonly canvasRef = viewChild.required<ElementRef<HTMLCanvasElement>>('canvasRef');
  private chart: Chart<'line'> | null = null;

  constructor() {
    // Re-renders in place whenever `labels`/`datasets` change after the
    // initial chart exists (e.g. logs loading async after the view is up).
    // No-ops on the effect's first run, before `ngAfterViewInit` has
    // created the chart yet.
    effect(() => {
      const labels = this.labels();
      const datasets = this.datasets();
      if (!this.chart) {
        return;
      }
      this.chart.data.labels = labels;
      this.chart.data.datasets = this.toChartJsDatasets(datasets);
      this.chart.update();
    });
  }

  ngAfterViewInit(): void {
    this.chart = new Chart(this.canvasRef().nativeElement, {
      type: 'line',
      data: {
        labels: this.labels(),
        datasets: this.toChartJsDatasets(this.datasets()),
      },
      options: this.buildOptions(),
    });
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  private toChartJsDatasets(datasets: LineChartDataset[]) {
    return datasets.map((dataset) => ({
      label: dataset.label,
      data: dataset.data,
      borderColor: dataset.color,
      backgroundColor: dataset.color,
      borderWidth: 2,
      pointRadius: 3,
      pointHoverRadius: 5,
      pointHitRadius: 12,
      pointBackgroundColor: dataset.color,
      tension: 0.25,
    }));
  }

  private buildOptions(): ChartOptions<'line'> {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'start',
          labels: {
            usePointStyle: true,
            pointStyle: 'line',
            boxHeight: 2,
            color: '#52514e',
            font: { size: 12 },
          },
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
      scales: {
        x: {
          grid: { color: '#e1e0d9' },
          border: { color: '#c3c2b7' },
          ticks: { color: '#898781' },
        },
        y: {
          beginAtZero: true,
          grid: { color: '#e1e0d9' },
          border: { color: '#c3c2b7' },
          ticks: { color: '#898781', precision: 0 },
        },
      },
    };
  }
}
