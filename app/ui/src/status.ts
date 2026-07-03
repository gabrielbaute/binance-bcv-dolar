import { getById } from "./dom";

const STATUS_LABELS: Record<string, string> = {
  online: "Online",
  loading: "Cargando",
  error: "Error",
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
