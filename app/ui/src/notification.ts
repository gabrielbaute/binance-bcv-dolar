export type NotificationType = "success" | "error" | "info";

export function showNotification(message: string, type: NotificationType = "info"): void {
  document.querySelectorAll(".notification").forEach((notification) => notification.remove());

  const notification = document.createElement("div");
  notification.className = `notification ${type}`;
  notification.textContent = message;
  document.body.appendChild(notification);

  window.setTimeout(() => {
    notification.remove();
  }, 4500);
}
