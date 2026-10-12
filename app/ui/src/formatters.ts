export function formatRate(rate: number): string {
  if (!Number.isFinite(rate)) {
    return "--";
  }

  const amount = new Intl.NumberFormat("es-VE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Math.abs(rate));
  return `${rate < 0 ? "-" : ""}Bs. ${amount}`;
}

export function formatAmount(amount: number): string {
  if (!Number.isFinite(amount)) {
    return "0.00";
  }

  return new Intl.NumberFormat("es-VE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatTime(timestamp?: string): string {
  if (!timestamp) {
    return "--";
  }

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "--";
  }

  return new Intl.DateTimeFormat("es-VE", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatChartDate(dateString: string): string {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return dateString;
  }

  return new Intl.DateTimeFormat("es-VE", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(date);
}
