import Chart from "chart.js/auto";
import { formatRate } from "./formatters";
import { HistorySeries } from "./history";
import { TimeRange } from "./types";

const axisNumber = new Intl.NumberFormat("es-VE", {
  notation: "compact",
  maximumFractionDigits: 1,
});

export class ChartManager {
  private chart: Chart;
  private dates: string[] = [];
  private range: TimeRange = "24h";

  constructor(canvas: HTMLCanvasElement) {
    this.chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Binance P2P USDT/VES",
            data: [],
            borderColor: "#38bdf8",
            backgroundColor: "#38bdf8",
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 5,
            pointHitRadius: 12,
            spanGaps: false,
            tension: 0.15,
          },
          {
            label: "BCV USD/VES",
            data: [],
            borderColor: "#2dd4bf",
            backgroundColor: "#2dd4bf",
            borderDash: [6, 4],
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 5,
            pointHitRadius: 12,
            spanGaps: false,
            tension: 0.15,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { intersect: false, mode: "index" },
        plugins: {
          legend: {
            position: "top",
            align: "start",
            labels: { color: "#cbd5e1", usePointStyle: true, boxWidth: 10, padding: 18 },
          },
          tooltip: {
            backgroundColor: "#0f172a",
            titleColor: "#e2e8f0",
            bodyColor: "#e2e8f0",
            borderColor: "rgba(148, 163, 184, 0.4)",
            borderWidth: 1,
            padding: 12,
            callbacks: {
              title: (items) => this.tooltipDate(items[0]?.dataIndex),
              label: (item) =>
                `${item.dataset.label}: ${item.parsed.y == null ? "Sin dato" : formatRate(item.parsed.y)}`,
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: "#cbd5e1", maxRotation: 0, autoSkip: true, maxTicksLimit: 5 },
          },
          y: {
            beginAtZero: false,
            grid: { color: "rgba(148, 163, 184, 0.15)" },
            ticks: {
              color: "#cbd5e1",
              callback: (value) => axisNumber.format(Number(value)),
            },
            title: { display: true, text: "Bolívares (VES)", color: "#cbd5e1" },
          },
        },
      },
    });
  }

  update(series: HistorySeries, range: TimeRange): void {
    this.dates = series.dates;
    this.range = range;
    this.chart.data.labels = series.labels;
    this.chart.data.datasets[0].data = series.binance;
    this.chart.data.datasets[1].data = series.bcv;
    this.chart.update();
  }

  private tooltipDate(index?: number): string {
    const key = index === undefined ? undefined : this.dates[index];
    if (!key) return "";
    const hourly = this.range === "24h";
    const date = new Date(hourly ? `${key}:00:00Z` : `${key}T00:00:00Z`);
    return new Intl.DateTimeFormat("es-VE", {
      year: "numeric",
      month: "long",
      day: "numeric",
      ...(hourly ? { hour: "2-digit", minute: "2-digit" } : {}),
      timeZone: "UTC",
    }).format(date) + " UTC";
  }
}
