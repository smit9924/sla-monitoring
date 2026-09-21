import { TestBed } from '@angular/core/testing';
import { Searchbar } from './searchbar';

describe('Searchbar', () => {
  function createComponent() {
    const fixture = TestBed.createComponent(Searchbar);
    fixture.detectChanges();
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    return { component: fixture.componentInstance, fixture, input };
  }

  it('should not emit while typing', () => {
    const { component, fixture, input } = createComponent();
    const spy = vi.fn();
    component.searchChanged.subscribe(spy);

    input.value = 'invoice';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(spy).not.toHaveBeenCalled();
  });

  it('should emit the trimmed term on Enter', () => {
    const { component, fixture, input } = createComponent();
    const spy = vi.fn();
    component.searchChanged.subscribe(spy);

    input.value = '  invoice  ';
    input.dispatchEvent(new Event('input'));
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
    fixture.detectChanges();

    expect(spy).toHaveBeenCalledWith('invoice');
  });

  it('should emit the term when the search button is clicked', () => {
    const { component, fixture, input } = createComponent();
    const spy = vi.fn();
    component.searchChanged.subscribe(spy);

    input.value = 'invoice';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const searchButton = fixture.nativeElement.querySelector(
      'button[aria-label="Search"]',
    ) as HTMLButtonElement;
    searchButton.click();

    expect(spy).toHaveBeenCalledWith('invoice');
  });

  it('should clear the term and emit an empty string', () => {
    const { component, fixture, input } = createComponent();
    const spy = vi.fn();
    component.searchChanged.subscribe(spy);

    input.value = 'invoice';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const clearButton = fixture.nativeElement.querySelector(
      'button[aria-label="Clear search"]',
    ) as HTMLButtonElement;
    clearButton.click();
    fixture.detectChanges();

    expect(input.value).toBe('');
    expect(spy).toHaveBeenCalledWith('');
    expect(fixture.nativeElement.querySelector('button[aria-label="Clear search"]')).toBeNull();
  });
});
