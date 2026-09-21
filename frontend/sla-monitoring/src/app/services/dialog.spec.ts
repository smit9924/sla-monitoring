import { TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { Dialog } from './dialog';
import { GenericDialog } from '../components/common/generic-dialog/generic-dialog';
import { GenericDialogButtonType } from '../types/enums/common';

describe('Dialog', () => {
  let service: Dialog;
  let matDialog: { open: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    matDialog = { open: vi.fn().mockReturnValue('ref') };
    TestBed.configureTestingModule({
      providers: [{ provide: MatDialog, useValue: matDialog }],
    });
    service = TestBed.inject(Dialog);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should open a single Ok button dialog with the given title and message', () => {
    service.openOkDialog('Network Error', 'Please check your connection.');

    expect(matDialog.open).toHaveBeenCalledWith(
      GenericDialog,
      expect.objectContaining({
        data: expect.objectContaining({
          title: 'Network Error',
          contentText: 'Please check your connection.',
          buttons: [expect.objectContaining({ label: 'Ok', type: GenericDialogButtonType.FILLED })],
        }),
      }),
    );
  });

  it('should open a confirm dialog with Cancel resolving false and Confirm resolving true', () => {
    service.openConfirmDialog('Delete item', 'This cannot be undone.');

    const config = matDialog.open.mock.calls[0][1];
    expect(config.data.buttons).toEqual([
      expect.objectContaining({ label: 'Cancel', closeValue: false }),
      expect.objectContaining({ label: 'Confirm', closeValue: true }),
    ]);
  });
});
