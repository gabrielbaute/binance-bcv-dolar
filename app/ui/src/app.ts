import { ApiClient } from "./services/apiClient";
import { Calculator } from "./calculator";
import { ChartManager } from "./chartManager";
import { getById, setText } from "./dom";
import { formatChartDate, formatRate, formatTime } from "./formatters";
import { showNotification } from "./notification";
import { updateStatus } from "./status";
import { Tabs } from "./tabs";
import { CurrentRates, TimeRange } from "./types";

export class ExchangeRateApp {
  private readonly api = new ApiClient("/api/v1");
  private readonly chart = new ChartManager(getById<HTMLCanvasElement>("rateChart"));
  private readonly calculator = new Calculator();
  private readonly tabs = new Tabs((tab) => {
    if (tab === "calculator") {
      this.calculator.updateRateLabels();
    }
  });

  private readonly rates: CurrentRates = {
    binance: 0,
    bcv: 0,
    average: 0,
  };

  async init(): Promise<void> {
    this.bindEvents();
    await this.loadInitialData();
    this.tabs.switchTo("history");
  }

  private bindEvents(): void {
    getById("refresh-data").addEventListener("click", () => void this.refreshData());
    getById("export-data").addEventListener("click", () => void this.exportData());

    getById<HTMLSelectElement>("time-range").addEventListener("change", (event) => {
      const range = (event.target as HTMLSelectElement).value as TimeRange;
      void this.updateChart(range);
    });

    getById("refresh-chart").addEventListener("click", () => {
      const range = getById<HTMLSelectElement>("time-range").value as TimeRange;
      void this.updateChart(range);
    });
  }

  private async loadInitialData(): Promise<void> {
    try {
      await Promise.all([
        this.loadBinanceRate(),
        this.loadBcvRate(),
        this.loadAverageRate(),
        this.updateChart("24h"),
      ]);
    } catch (error) {
      console.error("Error loading initial data", error);
      showNotification("No se pudo cargar la data inicial", "error");
    }
  }

  private async loadBinanceRate(): Promise<void> {
    try {
      updateStatus("binance-status", "loading");
      const data = await this.api.getBinanceRealtime();
      if (data.average_price == null) {
        throw new Error("Invalid Binance payload");
      }

      this.rates.binance = Number(data.average_price);
      setText("binance-rate", formatRate(this.rates.binance));
      setText("binance-time", formatTime(data.date ?? new Date().toISOString()));
      updateStatus("binance-status", "online");
      this.calculator.setRates(this.rates);
    } catch (error) {
      console.error("Error loading Binance", error);
      setText("binance-rate", "Error");
      setText("binance-time", "--");
      updateStatus("binance-status", "error");
    }
  }

  private async loadBcvRate(): Promise<void> {
    try {
      updateStatus("bcv-status", "loading");
      const data = await this.api.getBcvRealtime();
      if (data.rate == null) {
        throw new Error("Invalid BCV payload");
      }

      this.rates.bcv = Number(data.rate);
      setText("bcv-rate", formatRate(this.rates.bcv));
      setText("bcv-time", formatTime(data.date));
      updateStatus("bcv-status", "online");
      this.calculator.setRates(this.rates);
    } catch (error) {
      console.error("Error loading BCV", error);
      setText("bcv-rate", "Error");
      setText("bcv-time", "--");
      updateStatus("bcv-status", "error");
    }
  }

  private async loadAverageRate(): Promise<void> {
    try {
      updateStatus("average-status", "loading");
      const data = await this.api.getAverageRealtime();
      if (data.average_usdt_ves == null) {
        throw new Error("Invalid average payload");
      }

      this.rates.average = Number(data.average_usdt_ves);
      setText("average-rate", formatRate(this.rates.average));
      updateStatus("average-status", "online");
      this.calculator.setRates(this.rates);
    } catch (error) {
      console.error("Error loading average", error);
      setText("average-rate", "Error");
      updateStatus("average-status", "error");
    }
  }

  private async updateChart(range: TimeRange): Promise<void> {
    try {
      const history = await this.api.getHistory(range);
      const allDates = new Set<string>();

      history.bcv.currencies?.forEach((item) => {
        if (item.date) {
          allDates.add(item.date.split("T")[0]);
        }
      });

      history.binance.currencies?.forEach((item) => {
        if (item.date) {
          allDates.add(item.date.split("T")[0]);
        }
      });

      if (allDates.size === 0) {
        await this.renderRealtimeChartSnapshot();
        return;
      }

      const sortedDates = Array.from(allDates).sort();
      const labels = sortedDates.map(formatChartDate);

      const bcvValues = sortedDates.map((date) => {
        const item = history.bcv.currencies?.find((entry) => entry.date?.startsWith(date));
        return item ? Number(item.rate) : null;
      });

      const binanceValues = sortedDates.map((date) => {
        const item = history.binance.currencies?.find((entry) => entry.date?.startsWith(date));
        return item ? Number(item.average_price) : null;
      });

      this.chart.update(labels, binanceValues, bcvValues);
    } catch (error) {
      console.error("Error updating chart", error);
      showNotification("No se pudo actualizar el gráfico", "error");
    }
  }

  private async renderRealtimeChartSnapshot(): Promise<void> {
    const [binanceResult, bcvResult] = await Promise.allSettled([
      this.api.getBinanceRealtime(),
      this.api.getBcvRealtime(),
    ]);

    const binanceRate =
      binanceResult.status === "fulfilled" ? Number(binanceResult.value.average_price) : null;
    const bcvRate = bcvResult.status === "fulfilled" ? Number(bcvResult.value.rate) : null;

    if (binanceRate == null && bcvRate == null) {
      this.chart.update([], [], []);
      return;
    }

    const label = new Intl.DateTimeFormat("es-VE", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date());

    this.chart.update([label], [binanceRate], [bcvRate]);
  }

  private async refreshData(): Promise<void> {
    showNotification("Actualizando datos...", "info");
    await this.loadInitialData();
    showNotification("Datos actualizados", "success");
  }

  private async exportData(): Promise<void> {
    try {
      const history = await this.api.getHistory("30d");
      const allDates = new Set<string>();

      history.bcv.currencies?.forEach((item) => {
        if (item.date) {
          allDates.add(item.date.split("T")[0]);
        }
      });

      history.binance.currencies?.forEach((item) => {
        if (item.date) {
          allDates.add(item.date.split("T")[0]);
        }
      });

      const sortedDates = Array.from(allDates).sort();
      let csv = "Date,BCV_Rate,Binance_Rate\n";

      sortedDates.forEach((date) => {
        const bcvItem = history.bcv.currencies?.find((entry) => entry.date?.startsWith(date));
        const binanceItem = history.binance.currencies?.find((entry) => entry.date?.startsWith(date));

        csv += `${date},${bcvItem?.rate ?? ""},${binanceItem?.average_price ?? ""}\n`;
      });

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `exchange_rates_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      URL.revokeObjectURL(url);
      document.body.removeChild(link);

      showNotification("CSV exportado", "success");
    } catch (error) {
      console.error("Error exporting data", error);
      showNotification("No se pudo exportar CSV", "error");
    }
  }

}
