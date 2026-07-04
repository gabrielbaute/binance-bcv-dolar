import { ApiClient } from "./services/apiClient";
import { Calculator } from "./calculator";
import { ChartManager } from "./chartManager";
import { getById, queryAll, setText } from "./dom";
import { formatChartDate, formatRate, formatTime } from "./formatters";
import { showNotification } from "./notification";
import { updateFreshness, updateStatus } from "./status";
import { Tabs } from "./tabs";
import { CurrentRates, FreshnessStatus, TimeRange } from "./types";

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
  private activeRange: TimeRange = "24h";

  private readonly observedAt: Partial<Record<"binance" | "bcv" | "average", string>> = {};

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
      this.setActiveRange(range);
      void this.updateChart(range);
    });

    queryAll<HTMLButtonElement>(".chart-preset").forEach((button) => {
      button.addEventListener("click", () => {
        const range = (button.dataset.range as TimeRange | undefined) ?? "24h";
        this.setActiveRange(range);
        void this.updateChart(range);
      });
    });

    getById("refresh-chart").addEventListener("click", () => {
      void this.updateChart(this.activeRange);
    });
  }

  private async loadInitialData(): Promise<void> {
    try {
      await Promise.all([
        this.loadBinanceRate(),
        this.loadBcvRate(),
        this.loadAverageRate(),
        this.updateChart(this.activeRange),
      ]);
    } catch (error) {
      console.error("Error loading initial data", error);
      showNotification("No se pudo cargar la data inicial", "error");
    }
  }

  private async loadBinanceRate(): Promise<void> {
    try {
      this.setCardLoading("binance", true);
      updateStatus("binance-status", "loading");
      const data = await this.api.getBinanceRealtime();
      if (data.average_price == null) {
        throw new Error("Invalid Binance payload");
      }

      const observedAt = data.date ?? new Date().toISOString();
      this.observedAt.binance = observedAt;
      this.rates.binance = Number(data.average_price);
      setText("binance-rate", formatRate(this.rates.binance));
      setText("binance-time", formatTime(observedAt));
      this.updateFreshnessFromTimestamp("binance-freshness", observedAt);
      updateStatus("binance-status", "online");
      this.calculator.setRates(this.rates);
    } catch (error) {
      console.error("Error loading Binance", error);
      setText("binance-rate", "Error");
      setText("binance-time", "--");
      updateFreshness("binance-freshness", "stale");
      updateStatus("binance-status", "error");
    } finally {
      this.setCardLoading("binance", false);
    }
  }

  private async loadBcvRate(): Promise<void> {
    try {
      this.setCardLoading("bcv", true);
      updateStatus("bcv-status", "loading");
      const data = await this.api.getBcvRealtime();
      if (data.rate == null) {
        throw new Error("Invalid BCV payload");
      }

      const observedAt = data.date ?? new Date().toISOString();
      this.observedAt.bcv = observedAt;
      this.rates.bcv = Number(data.rate);
      setText("bcv-rate", formatRate(this.rates.bcv));
      setText("bcv-time", formatTime(observedAt));
      this.updateFreshnessFromTimestamp("bcv-freshness", observedAt);
      updateStatus("bcv-status", "online");
      this.calculator.setRates(this.rates);
    } catch (error) {
      console.error("Error loading BCV", error);
      setText("bcv-rate", "Error");
      setText("bcv-time", "--");
      updateFreshness("bcv-freshness", "stale");
      updateStatus("bcv-status", "error");
    } finally {
      this.setCardLoading("bcv", false);
    }
  }

  private async loadAverageRate(): Promise<void> {
    try {
      this.setCardLoading("average", true);
      updateStatus("average-status", "loading");
      const data = await this.api.getAverageRealtime();
      if (data.average_usdt_ves == null) {
        throw new Error("Invalid average payload");
      }

      const observedAt = this.getAverageObservedAt();
      this.observedAt.average = observedAt;
      this.rates.average = Number(data.average_usdt_ves);
      setText("average-rate", formatRate(this.rates.average));
      setText("average-time", formatTime(observedAt));
      this.updateFreshnessFromTimestamp("average-freshness", observedAt);
      updateStatus("average-status", "online");
      this.calculator.setRates(this.rates);
    } catch (error) {
      console.error("Error loading average", error);
      setText("average-rate", "Error");
      setText("average-time", "--");
      updateFreshness("average-freshness", "stale");
      updateStatus("average-status", "error");
    } finally {
      this.setCardLoading("average", false);
    }
  }

  private setCardLoading(card: "binance" | "bcv" | "average", loading: boolean): void {
    const cardElement = getById<HTMLElement>(`${card}-card`);
    cardElement.classList.toggle("is-loading", loading);
  }

  private setActiveRange(range: TimeRange): void {
    this.activeRange = range;
    getById<HTMLSelectElement>("time-range").value = range;

    queryAll<HTMLButtonElement>(".chart-preset").forEach((button) => {
      const isActive = button.dataset.range === range;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  private updateFreshnessFromTimestamp(elementId: string, timestamp?: string): void {
    updateFreshness(elementId, this.resolveFreshnessStatus(timestamp));
  }

  private resolveFreshnessStatus(timestamp?: string): FreshnessStatus {
    if (!timestamp) {
      return "stale";
    }

    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.getTime())) {
      return "stale";
    }

    const elapsedMinutes = Math.max(0, (Date.now() - parsed.getTime()) / 60000);

    if (elapsedMinutes <= 10) {
      return "live";
    }

    if (elapsedMinutes <= 60) {
      return "recent";
    }

    return "stale";
  }

  private getAverageObservedAt(): string {
    const candidates = [this.observedAt.binance, this.observedAt.bcv]
      .filter((value): value is string => Boolean(value))
      .map((value) => new Date(value))
      .filter((date) => !Number.isNaN(date.getTime()));

    if (candidates.length === 0) {
      return new Date().toISOString();
    }

    const oldestDate = candidates.reduce((oldest, current) =>
      current.getTime() < oldest.getTime() ? current : oldest,
    );

    return oldestDate.toISOString();
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
