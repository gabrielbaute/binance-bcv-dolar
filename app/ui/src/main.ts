import { ExchangeRateApp } from "./app";

declare global {
  interface Window {
    exchangeRateApp?: ExchangeRateApp;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new ExchangeRateApp();
  window.exchangeRateApp = app;
  void app.init();
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    void navigator.serviceWorker
      .register("/static/js/sw.js", { updateViaCache: "none" })
      .catch((error) => {
      console.error("Service worker registration failed", error);
    });
  });
}
