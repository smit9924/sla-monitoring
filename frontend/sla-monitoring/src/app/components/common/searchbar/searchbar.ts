import { Component, input, output, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

/**
 * Search input that only emits on explicit user action (Enter, the search
 * button, or the clear button) rather than on every keystroke, so callers
 * never need to debounce a query themselves.
 */
@Component({
  selector: 'app-searchbar',
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './searchbar.html',
  styleUrl: './searchbar.scss',
})
export class Searchbar {
  placeholder = input('Search');

  searchChanged = output<string>();

  protected readonly term = signal('');

  protected onTermInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.term.set(target.value);
  }

  protected emitSearch(): void {
    this.searchChanged.emit(this.term().trim());
  }

  protected clear(): void {
    this.term.set('');
    this.searchChanged.emit('');
  }
}
