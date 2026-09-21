import { TestBed } from '@angular/core/testing';
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from '@angular/material/snack-bar';
import { GenericSnackbar } from './generic-snackbar';
import { GenericSnackbarConfigData } from '../../../types/models/common/generic-snackbar/generic-snackbar-config-data';
import { GenericSnackbarType } from '../../../types/enums/common';

describe('GenericSnackbar', () => {
  it('should expose the injected snackbar data', () => {
    const data = new GenericSnackbarConfigData({
      text: 'Saved successfully',
      type: GenericSnackbarType.SUCCESS,
    });
    TestBed.configureTestingModule({
      providers: [
        { provide: MatSnackBarRef, useValue: { dismiss: vi.fn() } },
        { provide: MAT_SNACK_BAR_DATA, useValue: data },
      ],
    });

    const fixture = TestBed.createComponent(GenericSnackbar);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('.snackbar-text')?.textContent?.trim()).toBe(
      'Saved successfully',
    );
  });

  it('should dismiss the snackbar ref when dismiss() is called', () => {
    const dismiss = vi.fn();
    const data = new GenericSnackbarConfigData({ text: 'Hi', showCloseButton: true });
    TestBed.configureTestingModule({
      providers: [
        { provide: MatSnackBarRef, useValue: { dismiss } },
        { provide: MAT_SNACK_BAR_DATA, useValue: data },
      ],
    });

    const fixture = TestBed.createComponent(GenericSnackbar);
    fixture.detectChanges();
    (fixture.componentInstance as unknown as { dismiss: () => void }).dismiss();

    expect(dismiss).toHaveBeenCalled();
  });
});
