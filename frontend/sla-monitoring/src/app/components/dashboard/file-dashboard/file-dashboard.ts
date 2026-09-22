import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, input, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
import { appRoutes } from '../../../data/app-routes';
import { CHART_CATEGORICAL_PALETTE } from '../../../data/chart-palette';
import { Upload } from '../../../services/upload';
import { ServiceLogGroup } from '../../../types/interfaces/service-log';
import { FileStatsResponse } from '../../../types/interfaces/stats';
import { LineChart, LineChartDataset } from '../../charts/line-chart/line-chart';

/**
 * File dashboard: reached by clicking a successfully-processed file's name
 * in the upload history table. Two independently collapsible accordions --
 * SLA compliance (expanded by default: overall + per-service pass/fail,
 * uptime, and a per-day-per-service failure trend chart) and logs
 * (collapsed by default: fetched only once the panel is first opened, then
 * paginated per service via "Show more").
 */
@Component({
  selector: 'app-file-dashboard',
  imports: [
    DatePipe,
    MatButtonModule,
    MatExpansionModule,
    MatIconModule,
    MatProgressSpinnerModule,
    LineChart,
  ],
  templateUrl: './file-dashboard.html',
  styleUrl: './file-dashboard.scss',
})
export class FileDashboard implements OnInit {
  private readonly uploadService = inject(Upload);
  private readonly router = inject(Router);

  /** Bound from the route's `:guid` segment via `withComponentInputBinding()`. */
  guid = input.required<string>();

  protected readonly stats = signal<FileStatsResponse | null>(null);
  protected readonly isLoadingStats = signal(true);

  protected readonly logGroups = signal<ServiceLogGroup[]>([]);
  protected readonly isLoadingLogs = signal(false);
  protected readonly logsRequested = signal(false);
  protected readonly loadingMoreServiceId = signal<string | null>(null);

  /** Every distinct day present in the failure data, sorted ascending -- the chart's x-axis. */
  protected readonly chartLabels = computed<string[]>(() => {
    const days = new Set(this.stats()?.dailyFailures.map((point) => point.day) ?? []);
    return [...days].sort();
  });

  protected readonly chartDisplayLabels = computed<string[]>(() =>
    this.chartLabels().map((day) => this.formatDayLabel(day)),
  );

  /**
   * One line per service (present even if a service had zero failures every
   * day, so the legend/chart stay stable across files), colored from the
   * fixed categorical palette by a stable sort order rather than API order.
   */
  protected readonly chartDatasets = computed<LineChartDataset[]>(() => {
    const stats = this.stats();
    if (!stats) {
      return [];
    }

    const labels = this.chartLabels();
    const countsByService = new Map<string, { name: string; counts: Map<string, number> }>();

    for (const service of stats.services) {
      countsByService.set(service.serviceId, { name: service.serviceName, counts: new Map() });
    }
    for (const point of stats.dailyFailures) {
      countsByService.get(point.serviceId)?.counts.set(point.day, point.failureCount);
    }

    return [...countsByService.values()]
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((entry, index) => ({
        label: entry.name,
        data: labels.map((day) => entry.counts.get(day) ?? 0),
        color: CHART_CATEGORICAL_PALETTE[index % CHART_CATEGORICAL_PALETTE.length],
      }));
  });

  ngOnInit(): void {
    this.isLoadingStats.set(true);
    this.uploadService
      .getFileStats(this.guid())
      .pipe(finalize(() => this.isLoadingStats.set(false)))
      .subscribe((response) => this.stats.set(response));
  }

  /** Fires the logs API only the first time the accordion is expanded, per the spec. */
  protected onLogsPanelOpened(): void {
    if (this.logsRequested()) {
      return;
    }
    this.logsRequested.set(true);
    this.isLoadingLogs.set(true);
    this.uploadService
      .getFileLogs(this.guid())
      .pipe(finalize(() => this.isLoadingLogs.set(false)))
      .subscribe((response) => this.logGroups.set(response.services));
  }

  protected loadMoreLogs(serviceId: string): void {
    const group = this.logGroups().find((candidate) => candidate.serviceId === serviceId);
    if (!group) {
      return;
    }

    this.loadingMoreServiceId.set(serviceId);
    this.uploadService
      .getFileLogs(this.guid(), { serviceId, offset: group.logs.length })
      .pipe(finalize(() => this.loadingMoreServiceId.set(null)))
      .subscribe((response) => {
        const nextBatch = response.services[0];
        if (!nextBatch) {
          return;
        }
        this.logGroups.update((groups) =>
          groups.map((candidate) =>
            candidate.serviceId === serviceId
              ? {
                  ...candidate,
                  logs: [...candidate.logs, ...nextBatch.logs],
                  hasMore: nextBatch.hasMore,
                }
              : candidate,
          ),
        );
      });
  }

  protected isLoadingMore(serviceId: string): boolean {
    return this.loadingMoreServiceId() === serviceId;
  }

  protected async goBack(): Promise<void> {
    await this.router.navigateByUrl(appRoutes.uploadHistory);
  }

  /** Parses a `YYYY-MM-DD` day string as a UTC date, so it never shifts a day under a local timezone. */
  private formatDayLabel(day: string): string {
    const [year, month, date] = day.split('-').map(Number);
    return new Date(Date.UTC(year, month - 1, date)).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC',
    });
  }
}
