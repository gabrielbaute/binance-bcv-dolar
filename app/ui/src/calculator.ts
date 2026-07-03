import { getById, queryAll } from "./dom";
import { formatAmount, formatRate } from "./formatters";
import { CurrencyMode, CurrentRates } from "./types";

export class Calculator {
  private mode: CurrencyMode = "USD";
  private rates: CurrentRates = { binance: 0, bcv: 0, average: 0 };

  constructor() {
    this.bindEvents();
    this.setMode("USD");
  }

  setRates(rates: CurrentRates): void {
    this.rates = rates;
    this.updateRateLabels();
    this.calculate();
  }

  updateRateLabels(): void {
    getById("binance-rate-calc").textContent = formatRate(this.rates.binance);
    getById("bcv-rate-calc").textContent = formatRate(this.rates.bcv);
    getById("average-rate-calc").textContent = formatRate(this.rates.average);
  }

  clear(): void {
    const amountInput = getById<HTMLInputElement>("amount-input");
    amountInput.value = "";
    this.setResults(0, 0, 0);
  }

  private bindEvents(): void {
    getById("toggle-usd").addEventListener("click", () => this.setMode("USD"));
    getById("toggle-ves").addEventListener("click", () => this.setMode("VES"));
    getById("amount-input").addEventListener("input", () => this.calculate());
    getById("clear-calc").addEventListener("click", () => this.clear());
  }

  private setMode(mode: CurrencyMode): void {
    this.mode = mode;

    queryAll<HTMLElement>(".currency-btn").forEach((button) => {
      button.classList.toggle("active", button.dataset.currency === mode);
    });

    getById("input-symbol").textContent = mode === "USD" ? "$" : "Bs.";
    getById("input-currency").textContent = mode;

    const targetCurrency = mode === "USD" ? "VES" : "USD";
    const targetSymbol = targetCurrency === "USD" ? "$" : "Bs.";

    getById("binance-symbol").textContent = targetSymbol;
    getById("bcv-symbol").textContent = targetSymbol;
    getById("average-symbol").textContent = targetSymbol;

    getById("binance-currency").textContent = targetCurrency;
    getById("bcv-currency").textContent = targetCurrency;
    getById("average-currency").textContent = targetCurrency;

    this.calculate();
  }

  private calculate(): void {
    const amount = Number.parseFloat(getById<HTMLInputElement>("amount-input").value) || 0;

    if (amount <= 0) {
      this.setResults(0, 0, 0);
      return;
    }

    const convert = (rate: number): number => {
      if (!Number.isFinite(rate) || rate <= 0) {
        return 0;
      }

      return this.mode === "USD" ? amount * rate : amount / rate;
    };

    this.setResults(convert(this.rates.binance), convert(this.rates.bcv), convert(this.rates.average));
  }

  private setResults(binance: number, bcv: number, average: number): void {
    getById("binance-result").textContent = formatAmount(binance);
    getById("bcv-result").textContent = formatAmount(bcv);
    getById("average-result").textContent = formatAmount(average);
  }
}
