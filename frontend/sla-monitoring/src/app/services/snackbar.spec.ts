import { TestBed } from '@angular/core/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Snackbar } from './snackbar';
import { GenericSnackbar } from '../components/common/generic-snackbar/generic-snackbar';
import { GenericSnackbarDuration, GenericSnackbarType } from '../types/enums/common';

describe('Snackbar', () => {
  let service: Snackbar;
  let matSnackBar: { openFromComponent: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    matSnackBar = { openFromComponent: vi.fn() };
    TestBed.configureTestingModule({
      providers: [{ provide: MatSnackBar, useValue: matSnackBar }],
    });
    service = TestBed.inject(Snackbar);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should derive panelClass and politeness from the snackbar type before opening', () => {
    service.show('Something went wrong', GenericSnackbarType.ERROR);

    expect(matSnackBar.openFromComponent).toHaveBeenCalledWith(
      GenericSnackbar,
      expect.objectContaining({
        panelClass: 'snackbar-error',
        politeness: 'assertive',
        data: expect.objectContaining({ text: 'Something went wrong', type: 'error' }),
      }),
    );
  });

  it('should default to a medium duration when none is provided', () => {
    service.show('Saved', GenericSnackbarType.SUCCESS);

    const config = matSnackBar.openFromComponent.mock.calls[0][1];
    expect(config.duration).toBe(GenericSnackbarDuration.MEDIUM);
  });
});
