import { formatChartDate } from "./formatters";
import { BcvHistoryItem, HistoryData, TimeRange } from "./types";

export const MAX_BCV_REFERENCE_AGE_MS = 72 * 60 * 60 * 1000;

export interface HistorySeries {
  dates: string[];
  labels: string[];
  bcv: Array<number | null>;
  binance: Array<number | null>;
  bcvObservedAt?: Array<string | null>;
  binanceObservedAt?: Array<string | null>;
}

export interface SpreadPoint {
  date: string;
  label: string;
  amount: number | null;
  percent: number | null;
  bcvObservedAt?: string | null;
}

export function buildSpreadSeries(
  series: HistorySeries,
  options: { carryBcv?: boolean; bcvReference?: BcvHistoryItem | null } = {},
): SpreadPoint[] {
  const referenceDate = parseTimestamp(options.bcvReference?.date);
  const referenceRate = Number(options.bcvReference?.rate);
  let lastBcv =
    referenceDate && Number.isFinite(referenceRate) && referenceRate > 0
      ? { rate: referenceRate, time: referenceDate.getTime() }
      : null;
  return series.dates.map((date, index) => {
    const bcv = series.bcv[index];
    const binance = series.binance[index];
    const bcvDate = parseTimestamp(series.bcvObservedAt?.[index] ?? undefined);
    const binanceDate = parseTimestamp(
      series.binanceObservedAt?.[index] ?? undefined,
    );
    const intervalStart = parseTimestamp(
      options.carryBcv ? `${date}:00:00Z` : `${date}T00:00:00Z`,
    );
    const comparisonTime =
      binanceDate?.getTime() ?? intervalStart?.getTime() ?? 0;
    const observationTime = bcvDate?.getTime() ?? intervalStart?.getTime() ?? 0;
    if (
      options.carryBcv &&
      bcv != null &&
      bcv > 0 &&
      observationTime <= comparisonTime
    ) {
      lastBcv = { rate: bcv, time: observationTime };
    }
    const effectiveBcv = options.carryBcv
      ? lastBcv &&
        comparisonTime >= lastBcv.time &&
        comparisonTime - lastBcv.time <= MAX_BCV_REFERENCE_AGE_MS
        ? lastBcv.rate
        : null
      : bcv;
    const amount =
      effectiveBcv != null && binance != null && effectiveBcv > 0 && binance > 0
        ? binance - effectiveBcv
        : null;
    const usedBcvDate =
      options.carryBcv && amount != null && lastBcv
        ? new Date(lastBcv.time).toISOString()
        : (series.bcvObservedAt?.[index] ?? null);
    if (
      options.carryBcv &&
      bcv != null &&
      bcv > 0 &&
      observationTime > comparisonTime
    ) {
      lastBcv = { rate: bcv, time: observationTime };
    }
    return {
      date,
      label: series.labels[index],
      amount,
      percent:
        amount == null || effectiveBcv == null
          ? null
          : (amount / effectiveBcv) * 100,
      bcvObservedAt: usedBcvDate,
    };
  });
}

export function toDateRange(
  timeRange: TimeRange,
  now = new Date(),
): { start: string; end: string } {
  const start = new Date(now);
  if (timeRange === "24h") {
    start.setUTCHours(start.getUTCHours() - 24);
  } else if (timeRange === "7d") {
    start.setUTCDate(start.getUTCDate() - 7);
  } else if (timeRange === "30d") {
    start.setUTCDate(start.getUTCDate() - 30);
  } else if (timeRange === "90d") {
    start.setUTCDate(start.getUTCDate() - 90);
  } else if (timeRange === "ytd") {
    start.setUTCMonth(0, 1);
    start.setUTCHours(0, 0, 0, 0);
  } else {
    const year = now.getUTCFullYear() - 1;
    return {
      start: new Date(Date.UTC(year, 0, 1)).toISOString(),
      end: new Date(Date.UTC(year + 1, 0, 1) - 1).toISOString(),
    };
  }
  return { start: start.toISOString(), end: now.toISOString() };
}

function parseTimestamp(value?: string): Date | null {
  if (!value) return null;
  // SQLite-backed API timestamps omit the UTC suffix.
  const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
    ? value
    : `${value}Z`;
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function buildHistorySeries(
  history: HistoryData,
  range: TimeRange,
): HistorySeries {
  const hourly = range === "24h";
  const bcv = new Map<string, { timestamp: number; rate: number }>();
  const binance = new Map<string, { timestamp: number; rate: number }>();

  const add = (
    target: typeof bcv,
    timestamp: string | undefined,
    rawRate: number | string,
  ) => {
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
  history.binance.currencies?.forEach((item) =>
    add(binance, item.date, item.average_price),
  );

  const observedDates = Array.from(
    new Set([...bcv.keys(), ...binance.keys()]),
  ).sort();
  const dates: string[] = [];
  if (observedDates.length > 0) {
    const start = Date.parse(
      `${observedDates[0]}${hourly ? ":00:00Z" : "T00:00:00Z"}`,
    );
    const end = Date.parse(
      `${observedDates[observedDates.length - 1]}${hourly ? ":00:00Z" : "T00:00:00Z"}`,
    );
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
    bcvObservedAt: dates.map((date) => {
      const timestamp = bcv.get(date)?.timestamp;
      return timestamp == null ? null : new Date(timestamp).toISOString();
    }),
    binanceObservedAt: dates.map((date) => {
      const timestamp = binance.get(date)?.timestamp;
      return timestamp == null ? null : new Date(timestamp).toISOString();
    }),
  };
}
