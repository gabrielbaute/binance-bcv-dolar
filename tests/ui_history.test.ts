import assert from "node:assert/strict";
import { test } from "node:test";

import { buildHistorySeries, toDateRange } from "../app/ui/src/history";
import { ApiClient } from "../app/ui/src/services/apiClient";

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

  assert.deepEqual(series.dates, ["2026-10-09T10", "2026-10-09T11", "2026-10-09T12"]);
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
  assert.equal(toDateRange("24h", new Date("2026-10-09T12:00:00Z")).start, "2026-10-08T12:00:00.000Z");
});

test("previous year selects the complete prior calendar year, including leap years", () => {
  assert.deepEqual(toDateRange("previous-year", new Date("2026-10-09T12:00:00Z")), {
    start: "2025-01-01T00:00:00.000Z",
    end: "2025-12-31T23:59:59.999Z",
  });
  assert.deepEqual(toDateRange("previous-year", new Date("2025-02-01T00:00:00Z")), {
    start: "2024-01-01T00:00:00.000Z",
    end: "2024-12-31T23:59:59.999Z",
  });
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
    return new Response(JSON.stringify({ count: total, currencies }), { status: 200 });
  };

  try {
    const history = await new ApiClient().getHistory("7d");
    assert.equal(history.bcv.currencies.length, 1001);
    assert.equal(history.binance.currencies.length, 2);
    assert.equal(calls.filter((call) => call.includes("/history/bcv")).length, 2);
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
