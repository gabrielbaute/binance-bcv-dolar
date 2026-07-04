export type TimeRange = "24h" | "7d" | "30d" | "90d" | "ytd";

export type CurrencyMode = "USD" | "VES";

export type FreshnessStatus = "live" | "recent" | "stale";

export interface CurrentRates {
  binance: number;
  bcv: number;
  average: number;
}

export interface BinanceRealtimeResponse {
  average_price: number;
  date?: string;
}

export interface BcvRealtimeResponse {
  rate: number;
  date?: string;
}

export interface AverageRealtimeResponse {
  average_usdt_ves: number;
}

export interface HistoryResponse<T> {
  currencies?: T[];
}

export interface BcvHistoryItem {
  currency?: string;
  date?: string;
  rate: number | string;
}

export interface BinanceHistoryItem {
  date?: string;
  average_price: number | string;
}

export interface HistoryData {
  bcv: HistoryResponse<BcvHistoryItem>;
  binance: HistoryResponse<BinanceHistoryItem>;
}
