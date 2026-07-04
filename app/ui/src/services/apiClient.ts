import {
  AverageRealtimeResponse,
  BcvRealtimeResponse,
  BinanceRealtimeResponse,
  BcvHistoryItem,
  HistoryData,
  TimeRange,
} from "../types";

function toDateRange(timeRange: TimeRange): { start: string; end: string } {
  const endDate = new Date();
  const startDate = new Date();

  if (timeRange === "24h") {
    startDate.setHours(startDate.getHours() - 24);
  } else if (timeRange === "7d") {
    startDate.setDate(startDate.getDate() - 7);
  } else if (timeRange === "30d") {
    startDate.setDate(startDate.getDate() - 30);
  } else if (timeRange === "90d") {
    startDate.setDate(startDate.getDate() - 90);
  } else {
    startDate.setMonth(0, 1);
    startDate.setHours(0, 0, 0, 0);
  }

  const toLocalYyyyMmDd = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  return {
    start: toLocalYyyyMmDd(startDate),
    end: toLocalYyyyMmDd(endDate),
  };
}

export class ApiClient {
  constructor(private readonly baseUrl: string = "/api/v1") {}

  private async fetchJsonOrDefault<T>(path: string, defaultValue: T): Promise<T> {
    try {
      return await this.fetchJson<T>(path);
    } catch (error) {
      const message = error instanceof Error ? error.message : "";
      if (message.startsWith("HTTP 404")) {
        return defaultValue;
      }

      throw error;
    }
  }

  private async fetchJson<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`);

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`HTTP ${response.status}: ${body.slice(0, 200)}`);
    }

    return (await response.json()) as T;
  }

  getBinanceRealtime(): Promise<BinanceRealtimeResponse> {
    return this.fetchJson<BinanceRealtimeResponse>("/binance/realtime_ves");
  }

  getBcvRealtime(): Promise<BcvRealtimeResponse> {
    return this.getBcvRealtimeWithFallback();
  }

  getAverageRealtime(): Promise<AverageRealtimeResponse> {
    return this.getAverageRealtimeWithFallback();
  }

  async getHistory(range: TimeRange): Promise<HistoryData> {
    const { start, end } = toDateRange(range);

    const [bcv, binance] = await Promise.all([
      this.fetchJsonOrDefault<HistoryData["bcv"]>(
        `/history/bcv?start_date=${start}&end_date=${end}&currency=dolar`,
        { currencies: [] },
      ),
      this.fetchJsonOrDefault<HistoryData["binance"]>(
        `/history/binance?start_date=${start}&end_date=${end}&fiat=VES&asset=USDT&trade_type=BUY`,
        { currencies: [] },
      ),
    ]);

    return { bcv, binance };
  }

  private async getBcvRealtimeWithFallback(): Promise<BcvRealtimeResponse> {
    try {
      const realtimeList = await this.fetchJson<BcvHistoryItem[]>("/bcv/realtime");
      const dolar = realtimeList.find(
        (item) => String(item.currency).toLowerCase() === "dolar" && item.rate != null,
      );

      if (dolar) {
        return {
          rate: Number(dolar.rate),
          date: dolar.date,
        };
      }
    } catch {
      // Fallback to persisted endpoint when realtime endpoint is unavailable.
    }

    const lastSaved = await this.fetchJson<BcvRealtimeResponse | null>("/bcv/dolar");
    if (!lastSaved || lastSaved.rate == null) {
      throw new Error("BCV payload does not contain dolar rate");
    }

    return lastSaved;
  }

  private async getAverageRealtimeWithFallback(): Promise<AverageRealtimeResponse> {
    try {
      const realtime = await this.fetchJson<AverageRealtimeResponse | null>(
        "/dolar/realtime_dolar_promedio",
      );
      if (realtime?.average_usdt_ves != null) {
        return realtime;
      }
    } catch {
      // Fallback to persisted endpoint when realtime endpoint is unavailable.
    }

    const lastSaved = await this.fetchJson<AverageRealtimeResponse | null>("/dolar/dolar_promedio");
    if (!lastSaved || lastSaved.average_usdt_ves == null) {
      throw new Error("Average payload does not contain average_usdt_ves");
    }

    return lastSaved;
  }
}
