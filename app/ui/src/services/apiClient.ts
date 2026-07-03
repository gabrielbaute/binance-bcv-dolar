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
  } else {
    startDate.setDate(startDate.getDate() - 30);
  }

  return {
    start: startDate.toISOString().split("T")[0],
    end: endDate.toISOString().split("T")[0],
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
      const lastSaved = await this.fetchJson<BcvRealtimeResponse | null>("/bcv/dolar");
      if (lastSaved?.rate != null) {
        return lastSaved;
      }
    } catch {
      // Fallback to realtime endpoint when last saved register is unavailable.
    }

    const realtimeList = await this.fetchJson<BcvHistoryItem[]>("/bcv/realtime");
    const dolar = realtimeList.find(
      (item) => String(item.currency).toLowerCase() === "dolar" && item.rate != null,
    );

    if (!dolar) {
      throw new Error("BCV realtime payload does not contain dolar rate");
    }

    return {
      rate: Number(dolar.rate),
      date: dolar.date,
    };
  }

  private async getAverageRealtimeWithFallback(): Promise<AverageRealtimeResponse> {
    try {
      const lastSaved = await this.fetchJson<AverageRealtimeResponse | null>("/dolar/dolar_promedio");
      if (lastSaved?.average_usdt_ves != null) {
        return lastSaved;
      }
    } catch {
      // Fallback to realtime endpoint when average from stored records is unavailable.
    }

    const realtime = await this.fetchJson<AverageRealtimeResponse | null>("/dolar/realtime_dolar_promedio");
    if (!realtime || realtime.average_usdt_ves == null) {
      throw new Error("Average realtime payload does not contain average_usdt_ves");
    }

    return realtime;
  }
}
