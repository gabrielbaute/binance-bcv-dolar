import {
  AverageRealtimeResponse,
  BcvRealtimeResponse,
  BinanceRealtimeResponse,
  BcvHistoryItem,
  BinanceHistoryItem,
  HistoryData,
  HistoryResponse,
  DateSelection,
  TimeRange,
} from "../types";
import { MAX_BCV_REFERENCE_AGE_MS, toDateRange } from "../history";

const HISTORY_PAGE_SIZE = 1000;
const MAX_HISTORY_RECORDS = 50000;
const FETCH_TIMEOUT_MS = 15000;

export class ApiClient {
  constructor(private readonly baseUrl: string = "/api/v1") {}

  private async fetchJsonOrDefault<T>(
    path: string,
    defaultValue: T,
  ): Promise<T> {
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
    const response = await fetch(`${this.baseUrl}${path}`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });

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

  async getHistory(
    range: TimeRange,
    selection: DateSelection = {},
  ): Promise<HistoryData> {
    const { start, end } = toDateRange(range, new Date(), selection);

    const [bcv, binance] = await Promise.all([
      this.fetchHistoryPages<HistoryData["bcv"]["currencies"][number]>(
        `/history/bcv?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}&currency=dolar`,
      ),
      this.fetchHistoryPages<HistoryData["binance"]["currencies"][number]>(
        `/history/binance?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}&fiat=VES&asset=USDT&trade_type=BUY`,
      ),
    ]);

    if (range !== "24h" || binance.currencies.length === 0) {
      return { bcv, binance };
    }

    const referenceStart = new Date(
      Date.parse(start) - MAX_BCV_REFERENCE_AGE_MS,
    ).toISOString();
    const previousBcv = await this.fetchJsonOrDefault<
      HistoryResponse<BcvHistoryItem>
    >(
      `/history/bcv?start_date=${encodeURIComponent(referenceStart)}&end_date=${encodeURIComponent(start)}&currency=dolar&skip=0&limit=1`,
      { currencies: [], count: 0 },
    );
    return { bcv, binance, bcvReference: previousBcv.currencies[0] ?? null };
  }

  async getAvailableYears(): Promise<number[]> {
    const paths = [
      "/history/bcv?currency=dolar",
      "/history/binance?fiat=VES&asset=USDT&trade_type=BUY",
    ];
    const bounds = await Promise.all(
      paths.map(async (path) => {
        const latest = await this.fetchJsonOrDefault<
          HistoryResponse<{ date?: string }>
        >(`${path}&skip=0&limit=1`, { currencies: [], count: 0 });
        if (!latest.count) return [];
        const earliest = await this.fetchJsonOrDefault<
          HistoryResponse<{ date?: string }>
        >(`${path}&skip=${latest.count - 1}&limit=1`, {
          currencies: [],
          count: 0,
        });
        return [latest.currencies[0]?.date, earliest.currencies[0]?.date]
          .filter((date): date is string => !!date)
          .map((date) => Number(date.slice(0, 4)));
      }),
    );
    const years = bounds
      .flat()
      .filter((year) => Number.isInteger(year) && year >= 2000);
    if (!years.length) return [];
    const maxYear = Math.min(Math.max(...years), new Date().getUTCFullYear());
    const result: number[] = [];
    for (let year = maxYear; year >= Math.min(...years); year--)
      result.push(year);
    return result;
  }

  async getLatestSavedDates(): Promise<{
    bcv: string | null;
    binance: string | null;
  }> {
    const [bcv, binance] = await Promise.all([
      this.fetchJsonOrDefault<HistoryResponse<BcvHistoryItem>>(
        "/history/bcv?currency=dolar&skip=0&limit=1",
        { currencies: [], count: 0 },
      ),
      this.fetchJsonOrDefault<HistoryResponse<BinanceHistoryItem>>(
        "/history/binance?fiat=VES&asset=USDT&trade_type=BUY&skip=0&limit=1",
        { currencies: [], count: 0 },
      ),
    ]);
    return {
      bcv: bcv.currencies[0]?.date ?? null,
      binance: binance.currencies[0]?.date ?? null,
    };
  }

  private async fetchHistoryPages<T>(
    path: string,
  ): Promise<HistoryResponse<T>> {
    const currencies: T[] = [];
    let count = 0;

    do {
      const separator = path.includes("?") ? "&" : "?";
      const page = await this.fetchJsonOrDefault<HistoryResponse<T>>(
        `${path}${separator}skip=${currencies.length}&limit=${HISTORY_PAGE_SIZE}`,
        { currencies: [], count: 0 },
      );
      if (
        !Array.isArray(page.currencies) ||
        page.currencies.length > HISTORY_PAGE_SIZE ||
        !Number.isInteger(page.count) ||
        page.count < page.currencies.length ||
        (page.count === 0 && currencies.length > 0)
      ) {
        throw new Error("Invalid history payload");
      }
      count = page.count;
      if (count > MAX_HISTORY_RECORDS) {
        throw new Error("History exceeds the supported record limit");
      }
      currencies.push(...page.currencies);
      if (page.currencies.length === 0 && currencies.length < count) {
        throw new Error(
          "History pagination stopped before all records were returned",
        );
      }
    } while (currencies.length < count);

    return { currencies, count };
  }

  private async getBcvRealtimeWithFallback(): Promise<BcvRealtimeResponse> {
    try {
      const realtimeList =
        await this.fetchJson<BcvHistoryItem[]>("/bcv/realtime");
      const dolar = realtimeList.find(
        (item) =>
          String(item.currency).toLowerCase() === "dolar" && item.rate != null,
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

    const lastSaved = await this.fetchJson<BcvRealtimeResponse | null>(
      "/bcv/dolar",
    );
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

    const lastSaved = await this.fetchJson<AverageRealtimeResponse | null>(
      "/dolar/dolar_promedio",
    );
    if (!lastSaved || lastSaved.average_usdt_ves == null) {
      throw new Error("Average payload does not contain average_usdt_ves");
    }

    return lastSaved;
  }
}
