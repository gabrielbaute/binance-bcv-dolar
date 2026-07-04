import { getById } from "./dom";
import { FreshnessStatus } from "./types";

const STATUS_LABELS: Record<string, string> = {
  online: "Online",
  loading: "Cargando",
  error: "Error",
};

const FRESHNESS_LABELS: Record<FreshnessStatus, string> = {
  live: "En vivo",
  recent: "Reciente",
  stale: "Desfasado",
};

export function updateStatus(elementId: string, status: "online" | "loading" | "error"): void {
  const element = getById<HTMLElement>(elementId);
  element.className = `status-indicator ${status}`;

  if (status === "loading") {
    element.innerHTML = '<span class="spinner"></span> Cargando';
    return;
  }

  element.textContent = STATUS_LABELS[status] ?? "Desconocido";
}

export function updateFreshness(elementId: string, status: FreshnessStatus): void {
  const element = getById<HTMLElement>(elementId);
  element.className = `freshness-badge ${status}`;
  element.textContent = FRESHNESS_LABELS[status];
}
