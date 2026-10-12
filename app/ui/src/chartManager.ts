import { barY, defineChart, lineY } from "@tanstack/charts";
import { scaleBand } from "@tanstack/charts/scales/band";
import { scaleLinear } from "@tanstack/charts/scales/linear";
import { scalePoint } from "@tanstack/charts/scales/point";
import { tooltip } from "@tanstack/charts/tooltip";
import type { HistorySeries, SpreadPoint } from "./history";
import type { RateSource, RateSnapshot } from "./types";

const colors: Record<RateSource, string> = {
  binance: "var(--color-binance)",
  bcv: "var(--color-bcv)",
  average: "var(--color-average)",
};

const names: Record<RateSource, string> = {
  binance: "Binance P2P",
  bcv: "BCV",
  average: "Referencia",
};

export function currentChart(rates: Record<RateSource, RateSnapshot>) {
  const rows = (["binance", "bcv", "average"] as const)
    .filter((source) => rates[source].value != null)
    .map((source) => ({
      source: names[source],
      value: rates[source].value as number,
      color: colors[source],
    }));
  return defineChart({
    marks: rows.map((row) =>
      barY([row], { x: "source", y: "value", fill: row.color }),
    ),
    scales: {
      x: { scale: () => scaleBand<string>().padding(0.3) },
      y: {
        scale: scaleLinear,
        nice: true,
        grid: true,
        axis: { label: "Bs. por USD / USDT" },
      },
    },
    tooltip,
  });
}

export function historyChart(series: HistorySeries) {
  const labels = new Map(
    series.dates.map((date, index) => [date, series.labels[index]]),
  );
  const bcv = series.dates.map((date, index) => ({
    date,
    value: series.bcv[index],
  }));
  const binance = series.dates.map((date, index) => ({
    date,
    value: series.binance[index],
  }));
  return defineChart({
    marks: [
      lineY(bcv, {
        x: "date",
        y: "value",
        stroke: colors.bcv,
        strokeWidth: 2.5,
        points: true,
      }),
      lineY(binance, {
        x: "date",
        y: "value",
        stroke: colors.binance,
        strokeWidth: 2.5,
        points: true,
      }),
    ],
    scales: {
      x: {
        scale: scalePoint<string>,
        axis: {
          ticks: {
            count: 6,
            format: (value: string) => labels.get(value) ?? value,
          },
        },
      },
      y: {
        scale: scaleLinear,
        nice: true,
        grid: true,
        axis: { label: "Bs. por USD / USDT" },
      },
    },
    tooltip,
  });
}

export function spreadChart(points: SpreadPoint[]) {
  const labels = new Map(points.map((point) => [point.date, point.label]));
  const rows = points.map((point) => ({
    date: point.date,
    percent: point.percent,
  }));
  return defineChart({
    marks: [
      lineY(rows, {
        x: "date",
        y: "percent",
        stroke: "var(--color-spread)",
        strokeWidth: 3,
        points: true,
      }),
    ],
    scales: {
      x: {
        scale: scalePoint<string>,
        axis: {
          ticks: {
            count: 6,
            format: (value: string) => labels.get(value) ?? value,
          },
        },
      },
      y: {
        scale: scaleLinear,
        nice: true,
        grid: true,
        axis: { label: "Brecha (%)" },
      },
    },
    tooltip,
  });
}
