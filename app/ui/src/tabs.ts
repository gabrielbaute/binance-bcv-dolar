import { queryAll } from "./dom";

export class Tabs {
  private active = "history";
  private readonly tabButtons = queryAll<HTMLElement>(".tab-button");

  constructor(private readonly onChange?: (tabName: string) => void) {
    this.bindEvents();
    this.switchTo("history");
  }

  switchTo(tabName: string): void {
    this.active = tabName;

    this.tabButtons.forEach((button) => {
      const isActive = button.dataset.tab === tabName;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-selected", String(isActive));
      button.tabIndex = isActive ? 0 : -1;
    });

    queryAll<HTMLElement>(".tab-pane").forEach((pane) => {
      const isActive = pane.id === `${tabName}-tab`;
      pane.classList.toggle("active", isActive);
      pane.toggleAttribute("hidden", !isActive);
    });

    this.onChange?.(tabName);
  }

  private bindEvents(): void {
    this.tabButtons.forEach((button) => {
      button.addEventListener("click", (event) => {
        const target = (event.target as HTMLElement).closest<HTMLElement>(".tab-button");
        const tabName = target?.dataset.tab;
        if (!tabName) {
          return;
        }

        this.switchTo(tabName);
      });

      button.addEventListener("keydown", (event) => this.handleKeydown(event));
    });
  }

  private handleKeydown(event: KeyboardEvent): void {
    const currentButton = event.currentTarget as HTMLElement;
    const currentIndex = this.tabButtons.indexOf(currentButton);

    if (currentIndex < 0) {
      return;
    }

    if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
      event.preventDefault();
      const direction = event.key === "ArrowRight" ? 1 : -1;
      const nextIndex = (currentIndex + direction + this.tabButtons.length) % this.tabButtons.length;
      this.tabButtons[nextIndex].focus();
      const nextTab = this.tabButtons[nextIndex].dataset.tab;
      if (nextTab) {
        this.switchTo(nextTab);
      }
      return;
    }

    if (event.key === "Home") {
      event.preventDefault();
      this.tabButtons[0].focus();
      const firstTab = this.tabButtons[0].dataset.tab;
      if (firstTab) {
        this.switchTo(firstTab);
      }
      return;
    }

    if (event.key === "End") {
      event.preventDefault();
      const last = this.tabButtons[this.tabButtons.length - 1];
      last.focus();
      const lastTab = last.dataset.tab;
      if (lastTab) {
        this.switchTo(lastTab);
      }
    }
  }
}
