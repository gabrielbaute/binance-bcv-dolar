import { formatChartDate } from "./formatters";
import { HistoryData, TimeRange } from "./types";

export interface HistorySeries {
  dates: string[];
  labels: string[];
  bcv: Array<number | null>;
  binance: Array<number | null>;
}

export function toDateRange(timeRange: TimeRange, now = new Date()): { start: string; end: string } {
  const start = new Date(now);
  if (timeRange === "24h") {
    start.setUTCHours(start.getUTCHours() - 24);
  } else if (timeRange === "7d") {
    start.setUTCDate(start.getUTCDate() - 7);
  } else if (timeRange === "30d") {
    start.setUTCDate(start.getUTCDate() - 30);
  } else if (timeRange === "90d") {
    start.setUTCDate(start.getUTCDate() - 90);
  } else {
    start.setUTCMonth(0, 1);
    start.setUTCHours(0, 0, 0, 0);
  }
  return { start: start.toISOString(), end: now.toISOString() };
}

function parseTimestamp(value?: string): Date | null {
  if (!value) return null;
  // SQLite-backed API timestamps omit the UTC suffix.
  const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value) ? value : `${value}Z`;
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function buildHistorySeries(history: HistoryData, range: TimeRange): HistorySeries {
  const hourly = range === "24h";
  const bcv = new Map<string, { timestamp: number; rate: number }>();
  const binance = new Map<string, { timestamp: number; rate: number }>();

  const add = (target: typeof bcv, timestamp: string | undefined, rawRate: number | string) => {
    const date = parseTimestamp(timestamp);
    const rate = Number(rawRate);
    if (!date || !Number.isFinite(rate) || rate <= 0) return;
    const key = date.toISOString().slice(0, hourly ? 13 : 10);
    const previous = target.get(key);
    if (!previous || date.getTime() > previous.timestamp) {
      target.set(key, { timestamp: date.getTime(), rate });
    }
  };

  history.bcv.currencies?.forEach((item) => add(bcv, item.date, item.rate));
  history.binance.currencies?.forEach((item) => add(binance, item.date, item.average_price));

  const observedDates = Array.from(new Set([...bcv.keys(), ...binance.keys()])).sort();
  const dates: string[] = [];
  if (observedDates.length > 0) {
    const start = Date.parse(`${observedDates[0]}${hourly ? ":00:00Z" : "T00:00:00Z"}`);
    const end = Date.parse(`${observedDates[observedDates.length - 1]}${hourly ? ":00:00Z" : "T00:00:00Z"}`);
    for (let time = start; time <= end; time += hourly ? 3600000 : 86400000) {
      dates.push(new Date(time).toISOString().slice(0, hourly ? 13 : 10));
    }
  }
  const labels = dates.map((date) =>
    hourly
      ? new Intl.DateTimeFormat("es-VE", {
          day: "numeric",
          month: "short",
          hour: "2-digit",
          minute: "2-digit",
          timeZone: "UTC",
        }).format(new Date(`${date}:00:00Z`))
      : formatChartDate(date),
  );

  return {
    dates,
    labels,
    bcv: dates.map((date) => bcv.get(date)?.rate ?? null),
    binance: dates.map((date) => binance.get(date)?.rate ?? null),
  };
}
