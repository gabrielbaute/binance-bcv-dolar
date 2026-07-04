import Chart from "chart.js/auto";

export class ChartManager {
  private chart: Chart;

  constructor(canvas: HTMLCanvasElement) {
    this.chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Binance P2P",
            data: [],
            borderColor: "#0ea5e9",
            backgroundColor: "rgba(14, 165, 233, 0.15)",
            borderWidth: 2,
            fill: true,
            tension: 0.35,
          },
          {
            label: "BCV",
            data: [],
            borderColor: "#14b8a6",
            backgroundColor: "rgba(20, 184, 166, 0.12)",
            borderWidth: 2,
            fill: true,
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Histórico de Tasas",
          },
          legend: {
            position: "top",
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
        },
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: "VES",
            },
          },
        },
      },
    });
  }

  update(labels: string[], binance: Array<number | null>, bcv: Array<number | null>): void {
    this.chart.data.labels = labels;
    this.chart.data.datasets[0].data = binance;
    this.chart.data.datasets[1].data = bcv;
    this.chart.update();
  }
}
