import assert from "node:assert/strict";
import { test } from "node:test";

import {
  buildHistorySeries,
  buildSpreadSeries,
  toDateRange,
} from "../app/ui/src/history";
import { ApiClient } from "../app/ui/src/services/apiClient";
import { createChartScene } from "@tanstack/charts";
import { historyChart, spreadChart } from "../app/ui/src/chartManager";

test("24-hour history retains hourly points and selects the latest valid value", () => {
  const series = buildHistorySeries(
    {
      bcv: {
        count: 3,
        currencies: [
          { date: "2026-10-09T10:05:00", rate: 100 },
          { date: "2026-10-09T10:55:00", rate: 102 },
          { date: "2026-10-09T11:00:00", rate: "NaN" },
        ],
      },
      binance: {
        count: 1,
        currencies: [{ date: "2026-10-09T12:30:00Z", average_price: 105 }],
      },
    },
    "24h",
  );

  assert.deepEqual(series.dates, [
    "2026-10-09T10",
    "2026-10-09T11",
    "2026-10-09T12",
  ]);
  assert.deepEqual(series.bcv, [102, null, null]);
  assert.deepEqual(series.binance, [null, null, 105]);
});

test("longer history keeps one latest sample per UTC day", () => {
  const history = {
    bcv: {
      count: 2,
      currencies: [
        { date: "2026-10-09T08:00:00", rate: 100 },
        { date: "2026-10-09T20:00:00", rate: 101 },
      ],
    },
    binance: {
      count: 1,
      currencies: [{ date: "2026-10-11T01:00:00Z", average_price: 110 }],
    },
  };
  const series = buildHistorySeries(history, "7d");
  assert.deepEqual(series.dates, ["2026-10-09", "2026-10-10", "2026-10-11"]);
  assert.deepEqual(series.bcv, [101, null, null]);
  assert.deepEqual(series.binance, [null, null, 110]);
  assert.equal(
    toDateRange("24h", new Date("2026-10-09T12:00:00Z")).start,
    "2026-10-08T12:00:00.000Z",
  );
});

test("selected year covers the complete calendar year, including leap years", () => {
  assert.deepEqual(
    toDateRange("year", new Date("2026-10-09T12:00:00Z"), { year: 2025 }),
    {
      start: "2025-01-01T00:00:00.000Z",
      end: "2025-12-31T23:59:59.999Z",
    },
  );
  assert.deepEqual(
    toDateRange("year", new Date("2026-02-01T00:00:00Z"), { year: 2024 }),
    {
      start: "2024-01-01T00:00:00.000Z",
      end: "2024-12-31T23:59:59.999Z",
    },
  );
  assert.deepEqual(
    toDateRange("year", new Date("2026-10-17T12:00:00Z"), { year: 2026 }),
    {
      start: "2026-01-01T00:00:00.000Z",
      end: "2026-10-17T12:00:00.000Z",
    },
  );
});

test("custom dates are inclusive and invalid intervals are rejected", () => {
  const now = new Date("2026-10-13T12:00:00Z");
  assert.deepEqual(
    toDateRange("custom", now, { from: "2020-03-27", to: "2020-03-30" }),
    {
      start: "2020-03-27T00:00:00.000Z",
      end: "2020-03-30T23:59:59.999Z",
    },
  );
  assert.throws(() =>
    toDateRange("custom", now, { from: "2020-02-30", to: "2020-03-30" }),
  );
  assert.throws(() =>
    toDateRange("custom", now, { from: "2021-01-01", to: "2020-01-01" }),
  );
  assert.throws(() =>
    toDateRange("custom", now, { from: "2026-10-13", to: "2026-10-14" }),
  );
});

test("available years span the stored BCV and Binance dates", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (input) => {
    const url = new URL(String(input), "http://localhost");
    const bcv = url.pathname.endsWith("/bcv");
    const count = bcv ? 3 : 2;
    const first = Number(url.searchParams.get("skip")) === 0;
    const date = bcv
      ? first
        ? "2026-10-12T00:00:00"
        : "2020-03-27T00:00:00"
      : first
        ? "2026-10-13T00:00:00"
        : "2025-11-22T00:00:00";
    return new Response(JSON.stringify({ count, currencies: [{ date }] }), {
      status: 200,
    });
  };
  try {
    assert.deepEqual(
      await new ApiClient().getAvailableYears(),
      [2026, 2025, 2024, 2023, 2022, 2021, 2020],
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("a BCV-only year keeps its official rates without creating spread points", () => {
  const series = buildHistorySeries(
    {
      bcv: {
        count: 2,
        currencies: [
          { date: "2024-07-01T19:40:00Z", rate: 36.45 },
          { date: "2024-07-03T00:00:00Z", rate: 36.5 },
        ],
      },
      binance: { count: 0, currencies: [] },
    },
    "year",
  );
  assert.deepEqual(series.bcv, [36.45, null, 36.5]);
  assert.deepEqual(series.binance, [null, null, null]);
  assert.ok(buildSpreadSeries(series).every((point) => point.percent == null));
});

test("history client loads all pages for both providers", async () => {
  const originalFetch = globalThis.fetch;
  const calls: string[] = [];
  globalThis.fetch = async (input) => {
    const url = new URL(String(input), "http://localhost");
    calls.push(url.pathname + url.search);
    const skip = Number(url.searchParams.get("skip"));
    const bcv = url.pathname.endsWith("/bcv");
    const total = bcv ? 1001 : 2;
    const size = Math.min(1000, total - skip);
    const currencies = Array.from({ length: size }, (_, index) => ({
      date: "2026-10-09T12:00:00Z",
      ...(bcv ? { rate: index + 1 } : { average_price: index + 1 }),
    }));
    return new Response(JSON.stringify({ count: total, currencies }), {
      status: 200,
    });
  };

  try {
    const history = await new ApiClient().getHistory("7d");
    assert.equal(history.bcv.currencies.length, 1001);
    assert.equal(history.binance.currencies.length, 2);
    assert.equal(
      calls.filter((call) => call.includes("/history/bcv")).length,
      2,
    );
    assert.ok(calls.some((call) => call.includes("skip=1000&limit=1000")));
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("missing provider history remains empty instead of inventing a realtime point", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response("Not found", { status: 404 });
  try {
    const history = await new ApiClient().getHistory("24h");
    assert.deepEqual(buildHistorySeries(history, "24h").dates, []);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("latest persisted dates explain an empty rolling 24-hour range", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (input) => {
    const url = new URL(String(input), "http://localhost");
    if (url.searchParams.has("start_date")) {
      return new Response("Not found", { status: 404 });
    }
    const bcv = url.pathname.endsWith("/bcv");
    return new Response(
      JSON.stringify({
        count: 1,
        currencies: [
          { date: bcv ? "2026-10-10T00:00:00" : "2026-10-10T20:00:00" },
        ],
      }),
      { status: 200 },
    );
  };

  try {
    const client = new ApiClient();
    const history = await client.getHistory("24h");
    assert.equal(history.bcv.count, 0);
    assert.equal(history.binance.count, 0);
    assert.deepEqual(await client.getLatestSavedDates(), {
      bcv: "2026-10-10T00:00:00",
      binance: "2026-10-10T20:00:00",
    });
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("24-hour history loads the latest BCV observation before the window", async () => {
  const originalFetch = globalThis.fetch;
  const calls: URL[] = [];
  globalThis.fetch = async (input) => {
    const url = new URL(String(input), "http://localhost");
    calls.push(url);
    const baseline =
      url.pathname.endsWith("/bcv") && url.searchParams.get("limit") === "1";
    const binance = url.pathname.endsWith("/binance");
    const currencies = baseline
      ? [{ date: "2026-10-10T00:00:00", rate: 100 }]
      : binance
        ? [{ date: "2026-10-11T22:00:00", average_price: 120 }]
        : [];
    return new Response(
      JSON.stringify({ count: currencies.length, currencies }),
      {
        status: 200,
      },
    );
  };

  try {
    const history = await new ApiClient().getHistory("24h");
    assert.equal(history.bcv.currencies.length, 0);
    assert.equal(history.binance.currencies.length, 1);
    assert.equal(history.bcvReference?.rate, 100);
    assert.equal(calls.length, 3);
    assert.ok(calls[2].searchParams.has("start_date"));
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("spread uses only paired positive observations in the same UTC interval", () => {
  const series = buildHistorySeries(
    {
      bcv: {
        count: 3,
        currencies: [
          { date: "2026-10-09T10:15:00Z", rate: 100 },
          { date: "2026-10-09T11:00:00Z", rate: 105 },
          { date: "2026-10-09T12:00:00Z", rate: 0 },
        ],
      },
      binance: {
        count: 2,
        currencies: [
          { date: "2026-10-09T10:40:00Z", average_price: 110 },
          { date: "2026-10-09T12:30:00Z", average_price: 120 },
        ],
      },
    },
    "24h",
  );
  const spread = buildSpreadSeries(series);
  assert.deepEqual(
    spread.map((point) => point.amount),
    [10, null, null],
  );
  assert.deepEqual(
    spread.map((point) => point.percent),
    [10, null, null],
  );
});

test("spread can be negative without replacing missing rates with zero", () => {
  const spread = buildSpreadSeries({
    dates: ["2026-10-09", "2026-10-10"],
    labels: ["9 oct", "10 oct"],
    bcv: [100, null],
    binance: [90, 110],
  });
  assert.deepEqual(
    spread.map((point) => point.amount),
    [-10, null],
  );
  assert.deepEqual(
    spread.map((point) => point.percent),
    [-10, null],
  );
});

test("24-hour spread carries an observed BCV rate forward without looking ahead", () => {
  const spread = buildSpreadSeries(
    {
      dates: ["2026-10-11T10", "2026-10-11T11", "2026-10-11T12"],
      labels: ["10", "11", "12"],
      bcv: [null, 110, null],
      binance: [120, 130, 140],
      bcvObservedAt: [null, "2026-10-11T11:45:00Z", null],
      binanceObservedAt: [
        "2026-10-11T10:30:00Z",
        "2026-10-11T11:30:00Z",
        "2026-10-11T12:30:00Z",
      ],
    },
    {
      carryBcv: true,
      bcvReference: { date: "2026-10-10T00:00:00Z", rate: 100 },
    },
  );
  assert.deepEqual(
    spread.map((point) => point.amount),
    [20, 30, 30],
  );
  assert.deepEqual(
    spread.map((point) => point.percent),
    [20, 30, (30 / 110) * 100],
  );
  assert.equal(spread[1].bcvObservedAt, "2026-10-10T00:00:00.000Z");
  assert.equal(spread[2].bcvObservedAt, "2026-10-11T11:45:00.000Z");
});

test("24-hour spread drops a BCV reference older than 72 hours", () => {
  const spread = buildSpreadSeries(
    {
      dates: ["2026-10-11T10"],
      labels: ["10"],
      bcv: [null],
      binance: [120],
      binanceObservedAt: ["2026-10-11T10:30:00Z"],
    },
    {
      carryBcv: true,
      bcvReference: { date: "2026-10-08T10:00:00Z", rate: 100 },
    },
  );
  assert.equal(spread[0].amount, null);
  assert.equal(spread[0].percent, null);
});

test("a single daily observation remains visible in both historical charts", () => {
  const series = {
    dates: ["2026-10-11"],
    labels: ["11 oct"],
    bcv: [100],
    binance: [110],
  };
  const size = { width: 640, height: 390 };
  const historyScene = createChartScene(historyChart(series), size);
  const spreadScene = createChartScene(
    spreadChart(buildSpreadSeries(series)),
    size,
  );

  assert.ok(
    (JSON.stringify(historyScene).match(/"kind":"dot"/g) ?? []).length >= 2,
  );
  assert.ok(
    (JSON.stringify(spreadScene).match(/"kind":"dot"/g) ?? []).length >= 1,
  );
});
