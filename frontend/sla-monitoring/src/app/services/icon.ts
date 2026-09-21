import { inject, Injectable } from '@angular/core';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';
import { IconList } from '../data/icon-list';

/**
 * Registers every icon in `IconList` as a named SVG icon so it can be used
 * anywhere via `<mat-icon svgIcon="...">`. Instantiate once, eagerly, on app
 * startup (see `provideAppInitializer` in `app.config.ts`) rather than
 * lazily on first use, so icons are ready before any UI renders.
 */
@Injectable({
  providedIn: 'root',
})
export class Icon {
  private readonly matIconRegistry = inject(MatIconRegistry);
  private readonly sanitizer = inject(DomSanitizer);

  constructor() {
    this.registerIcons();
  }

  private registerIcons(): void {
    for (const icon of IconList) {
      this.matIconRegistry.addSvgIcon(
        icon.name,
        this.sanitizer.bypassSecurityTrustResourceUrl(icon.src),
      );
    }
  }
}
