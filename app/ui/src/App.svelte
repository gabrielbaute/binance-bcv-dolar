<script lang="ts">
  import { onMount, tick } from "svelte";
  import { Chart } from "@tanstack/charts/svelte";
  import { ApiClient } from "./services/apiClient";
  import { currentChart, historyChart, spreadChart } from "./chartManager";
  import {
    buildHistorySeries,
    buildSpreadSeries,
    type HistorySeries,
  } from "./history";
  import { formatAmount, formatRate, formatTime } from "./formatters";
  import type {
    BcvHistoryItem,
    RateSnapshot,
    RateSource,
    TimeRange,
  } from "./types";

  type Tab = "summary" | "history" | "spread" | "calculator";

  const api = new ApiClient();
  const tabs: { id: Tab; label: string }[] = [
    { id: "summary", label: "Resumen" },
    { id: "history", label: "Histórico" },
    { id: "spread", label: "Brecha" },
    { id: "calculator", label: "Calculadora" },
  ];
  const ranges: { id: TimeRange; label: string }[] = [
    { id: "24h", label: "24 h" },
    { id: "7d", label: "7 días" },
    { id: "30d", label: "30 días" },
    { id: "90d", label: "90 días" },
    { id: "ytd", label: "Este año" },
    { id: "previous-year", label: String(new Date().getUTCFullYear() - 1) },
  ];
  const emptySeries: HistorySeries = {
    dates: [],
    labels: [],
    bcv: [],
    binance: [],
  };
  const emptyRate = (): RateSnapshot => ({
    value: null,
    observedAt: null,
    status: "loading",
  });

  let activeTab = $state<Tab>("summary");
  let activeRange = $state<TimeRange>("7d");
  let rates = $state<Record<RateSource, RateSnapshot>>({
    binance: emptyRate(),
    bcv: emptyRate(),
    average: emptyRate(),
  });
  let history = $state<HistorySeries | null>(null);
  let bcvReference = $state<BcvHistoryItem | null>(null);
  let latestSaved = $state<{
    bcv: string | null;
    binance: string | null;
  } | null>(null);
  let historyStatus = $state<"loading" | "ready" | "error">("loading");
  let refreshing = $state(false);
  let mode = $state<"USD" | "VES">("USD");
  let amount = $state("");
  let requestId = 0;

  const spreadPoints = $derived(
    buildSpreadSeries(history ?? emptySeries, {
      carryBcv: activeRange === "24h",
      bcvReference,
    }),
  );
  const pairedPoints = $derived(
    spreadPoints.filter((point) => point.percent != null),
  );
  const latestSpread = $derived(pairedPoints.at(-1) ?? null);
  const latestSavedSummary = $derived(
    [
      latestSaved?.bcv ? `BCV ${formatTime(latestSaved.bcv)}` : null,
      latestSaved?.binance
        ? `Binance ${formatTime(latestSaved.binance)}`
        : null,
    ]
      .filter(Boolean)
      .join("; "),
  );
  const currentSpread = $derived(
    rates.binance.value != null &&
      rates.bcv.value != null &&
      rates.bcv.value > 0
      ? {
          amount: rates.binance.value - rates.bcv.value,
          percent:
            ((rates.binance.value - rates.bcv.value) / rates.bcv.value) * 100,
        }
      : null,
  );
  const currentValues = $derived(
    Object.values(rates).filter((rate) => rate.value != null).length,
  );
  const historyValues = $derived(
    (history?.bcv ?? []).some((value) => value != null) ||
      (history?.binance ?? []).some((value) => value != null),
  );
  const currentDefinition = $derived(currentChart(rates));
  const historyDefinition = $derived(historyChart(history ?? emptySeries));
  const spreadDefinition = $derived(spreadChart(spreadPoints));

  function validRate(value: unknown): number | null {
    const parsed = Number(value);
    return value != null && Number.isFinite(parsed) && parsed > 0
      ? parsed
      : null;
  }

  function validDate(value: string | undefined): string | null {
    if (!value) return null;
    const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
      ? value
      : `${value}Z`;
    const parsed = new Date(normalized);
    return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
  }

  function snapshot(value: unknown, date?: string): RateSnapshot {
    const parsed = validRate(value);
    return {
      value: parsed,
      observedAt: validDate(date),
      status: parsed == null ? "error" : "ready",
    };
  }

  async function loadRates(): Promise<void> {
    rates = {
      binance: { ...rates.binance, status: "loading" },
      bcv: { ...rates.bcv, status: "loading" },
      average: { ...rates.average, status: "loading" },
    };
    const [binance, bcv, average] = await Promise.allSettled([
      api.getBinanceRealtime(),
      api.getBcvRealtime(),
      api.getAverageRealtime(),
    ]);
    const nextBinance =
      binance.status === "fulfilled"
        ? snapshot(binance.value.average_price, binance.value.date)
        : { value: null, observedAt: null, status: "error" as const };
    const nextBcv =
      bcv.status === "fulfilled"
        ? snapshot(bcv.value.rate, bcv.value.date)
        : { value: null, observedAt: null, status: "error" as const };
    const dates = [nextBinance.observedAt, nextBcv.observedAt].filter(
      (date): date is string => date != null,
    );
    const averageDate = dates.length === 2 ? dates.sort()[0] : undefined;
    rates = {
      binance: nextBinance,
      bcv: nextBcv,
      average:
        average.status === "fulfilled"
          ? snapshot(average.value.average_usdt_ves, averageDate)
          : { value: null, observedAt: null, status: "error" },
    };
  }

  async function loadHistory(range = activeRange): Promise<void> {
    const currentRequest = ++requestId;
    historyStatus = "loading";
    history = null;
    bcvReference = null;
    latestSaved = null;
    try {
      const data = await api.getHistory(range);
      if (currentRequest !== requestId) return;
      const series = buildHistorySeries(data, range);
      history = series;
      bcvReference = data.bcvReference ?? null;
      if (range === "24h" && series.dates.length === 0) {
        try {
          const saved = await api.getLatestSavedDates();
          if (currentRequest !== requestId) return;
          latestSaved = {
            bcv: validDate(saved.bcv ?? undefined),
            binance: validDate(saved.binance ?? undefined),
          };
        } catch (error) {
          console.error(
            "No se pudo consultar la fecha del último registro",
            error,
          );
        }
      }
      if (currentRequest !== requestId) return;
      historyStatus = "ready";
    } catch (error) {
      if (currentRequest !== requestId) return;
      console.error("No se pudo cargar el histórico", error);
      historyStatus = "error";
    }
  }

  async function refresh(): Promise<void> {
    refreshing = true;
    await Promise.all([loadRates(), loadHistory()]);
    refreshing = false;
  }

  function changeRange(range: TimeRange): void {
    if (range === activeRange) return;
    activeRange = range;
    void loadHistory(range);
  }

  function changeTab(tab: Tab): void {
    activeTab = tab;
    const url = new URL(window.location.href);
    if (tab === "summary") url.searchParams.delete("tab");
    else url.searchParams.set("tab", tab);
    window.history.replaceState(null, "", url);
  }

  async function handleTabKeydown(event: KeyboardEvent): Promise<void> {
    const current = tabs.findIndex((tab) => tab.id === activeTab);
    let next = current;
    if (event.key === "ArrowRight") next = (current + 1) % tabs.length;
    else if (event.key === "ArrowLeft")
      next = (current - 1 + tabs.length) % tabs.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = tabs.length - 1;
    else return;
    event.preventDefault();
    changeTab(tabs[next].id);
    await tick();
    document.getElementById(`tab-${tabs[next].id}`)?.focus();
  }

  function exportCsv(): void {
    if (!history?.dates.length) return;
    const rows = history.dates.map(
      (date, index) =>
        `${date},${history?.bcv[index] ?? ""},${history?.binance[index] ?? ""}`,
    );
    const csv = `Fecha_UTC,BCV_VES,Binance_VES\n${rows.join("\n")}\n`;
    const url = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `exchange_rates_${activeRange}_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function conversion(source: RateSource): string {
    const rate = rates[source].value;
    const input = Number(amount);
    if (rate == null || !Number.isFinite(input) || input <= 0) return "—";
    return formatAmount(mode === "USD" ? input * rate : input / rate);
  }

  function percent(value: number): string {
    return (
      new Intl.NumberFormat("es-VE", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
        signDisplay: "always",
      }).format(value) + "%"
    );
  }

  onMount(() => {
    const tab = new URLSearchParams(window.location.search).get("tab");
    if (tabs.some((item) => item.id === tab)) activeTab = tab as Tab;
    void refresh();
    if ("serviceWorker" in navigator) {
      void navigator.serviceWorker
        .register("/static/js/sw.js", { updateViaCache: "none" })
        .catch((error) => console.error("No se pudo registrar la PWA", error));
    }
  });
</script>

<svelte:head>
  <title>Tasas de cambio en Venezuela | Dolar Pulse VE</title>
</svelte:head>

<a class="skip-link" href="#main-content">Saltar al contenido principal</a>
<div class="shell">
  <header class="masthead">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true">↗</span><span
        >Dolar Pulse <strong>VE</strong></span
      >
    </div>
    <div class="masthead-right">
      <span class="market-label">BCV + Binance P2P · VES</span><button
        class="refresh-button"
        onclick={() => void refresh()}
        disabled={refreshing}
        >{refreshing ? "Actualizando…" : "Actualizar tasas"}</button
      >
    </div>
  </header>

  <main id="main-content">
    <section class="intro" aria-label="Tasas actuales">
      <div class="intro-copy">
        <p class="section-label">Mercado cambiario venezolano</p>
        <h1>Una lectura clara del dólar de hoy.</h1>
        <p>
          Consulta la referencia oficial, el mercado P2P y la distancia entre
          ambos. Tasas en bolívares por USD o USDT.
        </p>
      </div>
      <div class="headline-rate">
        <span>Referencia actual</span>
        <strong
          >{rates.average.value == null
            ? "—"
            : formatRate(rates.average.value)}</strong
        >
        <small
          >{rates.average.status === "loading"
            ? "Consultando tasa…"
            : rates.average.status === "error"
              ? "Tasa no disponible"
              : rates.average.observedAt
                ? `Dato más antiguo: ${formatTime(rates.average.observedAt)}`
                : "Hora de observación no disponible"}</small
        >
      </div>
    </section>

    <section class="rate-strip" aria-label="Fuentes de tasas actuales">
      {#each ["binance", "bcv", "average"] as const as source}
        <article
          class:binance={source === "binance"}
          class:bcv={source === "bcv"}
          class:average={source === "average"}
        >
          <div class="rate-title">
            <span class="source-dot"></span>
            <h2>
              {source === "binance"
                ? "Binance P2P"
                : source === "bcv"
                  ? "BCV oficial"
                  : "Tasa referencia"}
            </h2>
          </div>
          <p class="rate-unit">
            {source === "binance" ? "USDT/VES" : "USD/VES"}
          </p>
          <p class="rate-value">
            {rates[source].value == null
              ? "—"
              : formatRate(rates[source].value)}
          </p>
          <p class="rate-time">
            {rates[source].status === "loading"
              ? "Consultando…"
              : rates[source].status === "error"
                ? "No disponible"
                : rates[source].observedAt
                  ? `Registrado: ${formatTime(rates[source].observedAt)}`
                  : "Fecha no disponible"}
          </p>
        </article>
      {/each}
    </section>

    <div class="tab-nav" role="tablist" aria-label="Vistas del dashboard">
      {#each tabs as tab}
        <button
          id={`tab-${tab.id}`}
          role="tab"
          aria-controls={`panel-${tab.id}`}
          aria-selected={activeTab === tab.id}
          tabindex={activeTab === tab.id ? 0 : -1}
          class:active={activeTab === tab.id}
          onclick={() => changeTab(tab.id)}
          onkeydown={handleTabKeydown}>{tab.label}</button
        >
      {/each}
    </div>

    {#if activeTab === "summary"}
      <div
        id="panel-summary"
        role="tabpanel"
        aria-labelledby="tab-summary"
        tabindex="0"
        class="panel-layout"
      >
        <div class="panel-main">
          <div class="panel-heading">
            <div>
              <p class="section-label">Vista actual</p>
              <h2>Las tres tasas, lado a lado</h2>
            </div>
            <span class="unit-note">Bolívares por unidad</span>
          </div>
          {#if currentValues > 0}
            <div class="chart-wrap">
              <Chart
                definition={currentDefinition}
                height={350}
                ariaLabel="Comparación de tasas actuales de Binance, BCV y referencia"
              />
            </div>
          {:else}<p class="chart-message" role="status">
              {refreshing
                ? "Consultando tasas…"
                : "No hay tasas actuales disponibles. Prueba con Actualizar tasas."}
            </p>{/if}
        </div>
        <aside class="panel-aside">
          <p class="section-label">Lectura rápida</p>
          <h3>Distancia con el BCV</h3>
          {#if currentSpread}
            <strong class="spread-figure"
              >{percent(currentSpread.percent)}</strong
            >
            <span class="spread-amount"
              >{currentSpread.amount >= 0 ? "+" : ""}{formatRate(
                currentSpread.amount,
              )}</span
            >
            <p>
              Binance P2P frente a la tasa oficial. El porcentaje usa BCV como
              base.
            </p>
          {:else}
            <strong class="spread-figure">—</strong>
            <p>La brecha aparece cuando están disponibles ambas tasas.</p>
          {/if}
          <button class="text-action" onclick={() => changeTab("spread")}
            >Ver evolución de la brecha <span aria-hidden="true">→</span
            ></button
          >
        </aside>
      </div>
    {:else if activeTab === "history"}
      <div
        id="panel-history"
        role="tabpanel"
        aria-labelledby="tab-history"
        tabindex="0"
        class="panel-single"
      >
        <div class="panel-heading">
          <div>
            <p class="section-label">Serie temporal</p>
            <h2>Histórico de tasas</h2>
            <p>
              Una observación por hora en 24 h y por día en los demás rangos.
              Los intervalos sin registros quedan vacíos.
            </p>
          </div>
        </div>
        <div class="panel-controls">
          <div class="range-list" role="group" aria-label="Rango del histórico">
            {#each ranges as range}<button
                aria-pressed={activeRange === range.id}
                class:active={activeRange === range.id}
                onclick={() => changeRange(range.id)}>{range.label}</button
              >{/each}
          </div>
          <button
            class="secondary-button"
            onclick={exportCsv}
            disabled={!history?.dates.length}>Exportar CSV</button
          >
        </div>
        <div class="chart-legend">
          <span><i class="legend-dot bcv-dot"></i>BCV USD/VES</span><span
            ><i class="legend-dot binance-dot"></i>Binance USDT/VES</span
          >
        </div>
        {#if historyStatus === "loading"}<p class="chart-message" role="status">
            Cargando histórico…
          </p>
        {:else if historyStatus === "error"}<p
            class="chart-message error"
            role="alert"
          >
            No se pudo cargar el histórico. Usa Actualizar tasas para intentarlo
            de nuevo.
          </p>
        {:else if !historyValues}<div class="chart-message" role="status">
            <div>
              <p>
                {activeRange === "24h"
                  ? "No hay registros en las últimas 24 horas."
                  : "No hay registros para este período."}
              </p>
              {#if activeRange === "24h"}
                {#if latestSavedSummary}<p>
                    Últimos registros guardados: {latestSavedSummary}
                  </p>{/if}
                <button class="text-action" onclick={() => changeRange("7d")}
                  >Ver 7 días →</button
                >
              {/if}
            </div>
          </div>
        {:else}<div class="chart-wrap wide">
            <Chart
              definition={historyDefinition}
              height={390}
              ariaLabel="Histórico de tasas BCV y Binance en bolívares"
            />
          </div>{/if}
        {#if history?.dates.length}<p class="footnote">
            Cobertura: {history.dates[0]} a {history.dates.at(-1)} UTC. Exportación
            del rango seleccionado.
          </p>{/if}
      </div>
    {:else if activeTab === "spread"}
      <div
        id="panel-spread"
        role="tabpanel"
        aria-labelledby="tab-spread"
        tabindex="0"
        class="panel-single"
      >
        <div class="panel-heading">
          <div>
            <p class="section-label">Comparación histórica</p>
            <h2>Brecha Binance − BCV</h2>
            <p>
              {activeRange === "24h"
                ? "Cada hora compara Binance con la última tasa BCV guardada antes de esa observación, hasta 72 h de antigüedad."
                : "Solo se calcula cuando ambas fuentes tienen una observación válida en el mismo día UTC."}
            </p>
          </div>
          <div class="metric-pair">
            <span>Último intervalo comparable</span><strong
              >{latestSpread?.percent == null
                ? "—"
                : percent(latestSpread.percent)}</strong
            ><small
              >{latestSpread?.amount == null
                ? "Sin datos"
                : `${latestSpread.amount >= 0 ? "+" : ""}${formatRate(latestSpread.amount)}`}</small
            >
            {#if activeRange === "24h" && latestSpread?.bcvObservedAt}<small>
                BCV guardada: {formatTime(latestSpread.bcvObservedAt)}
              </small>{/if}
          </div>
        </div>
        <div class="panel-controls">
          <div class="range-list" role="group" aria-label="Rango de la brecha">
            {#each ranges as range}<button
                aria-pressed={activeRange === range.id}
                class:active={activeRange === range.id}
                onclick={() => changeRange(range.id)}>{range.label}</button
              >{/each}
          </div>
        </div>
        {#if historyStatus === "loading"}<p class="chart-message" role="status">
            Calculando brecha…
          </p>
        {:else if historyStatus === "error"}<p
            class="chart-message error"
            role="alert"
          >
            No se pudo cargar la brecha. Usa Actualizar tasas para intentarlo de
            nuevo.
          </p>
        {:else if pairedPoints.length === 0}<div
            class="chart-message"
            role="status"
          >
            <div>
              <p>
                No hay intervalos con datos de ambas fuentes para este período.
              </p>
              {#if activeRange === "24h"}
                {#if !historyValues && latestSavedSummary}<p>
                    Últimos registros guardados: {latestSavedSummary}
                  </p>{/if}
                <button class="text-action" onclick={() => changeRange("7d")}
                  >Ver 7 días →</button
                >
              {/if}
            </div>
          </div>
        {:else}<div class="chart-wrap wide">
            <Chart
              definition={spreadDefinition}
              height={390}
              ariaLabel="Brecha porcentual entre Binance P2P y BCV"
            />
          </div>{/if}
        <p class="footnote">
          Porcentaje = (Binance − BCV) ÷ BCV × 100. Un valor negativo indica que
          Binance está por debajo del BCV.
        </p>
      </div>
    {:else}
      <div
        id="panel-calculator"
        role="tabpanel"
        aria-labelledby="tab-calculator"
        tabindex="0"
        class="panel-layout calculator-layout"
      >
        <div class="panel-main">
          <p class="section-label">Conversión</p>
          <h2>Calculadora USD / VES</h2>
          <p>Compara cuánto recibirías con cada tasa disponible.</p>
          <div class="calculator-form">
            <div
              class="mode-switch"
              role="group"
              aria-label="Moneda de entrada"
            >
              <button
                class:active={mode === "USD"}
                aria-pressed={mode === "USD"}
                onclick={() => (mode = "USD")}>USD a VES</button
              ><button
                class:active={mode === "VES"}
                aria-pressed={mode === "VES"}
                onclick={() => (mode = "VES")}>VES a USD</button
              >
            </div>
            <label for="amount-input">Monto en {mode}</label>
            <div class="amount-field">
              <span>{mode === "USD" ? "$" : "Bs."}</span><input
                id="amount-input"
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                bind:value={amount}
              /><span>{mode}</span>
            </div>
            <button class="text-action" onclick={() => (amount = "")}
              >Limpiar monto</button
            >
          </div>
        </div>
        <div class="panel-aside calc-results">
          <p class="section-label">Resultados</p>
          {#each ["binance", "bcv", "average"] as const as source}<div
              class="conversion-row"
            >
              <span
                >{source === "binance"
                  ? "Binance P2P"
                  : source === "bcv"
                    ? "BCV oficial"
                    : "Referencia"}</span
              ><strong>{conversion(source)}</strong><small
                >{mode === "USD" ? "VES" : "USD"} · {rates[source].value == null
                  ? "Tasa no disponible"
                  : formatRate(rates[source].value)}</small
              >
            </div>{/each}
        </div>
      </div>
    {/if}
  </main>
  <footer>
    <span>Dolar Pulse VE</span><span
      >Datos abiertos para Venezuela · BCV y Binance P2P</span
    >
  </footer>
</div>
