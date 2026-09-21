import { TestBed } from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { GenericDialog } from './generic-dialog';
import { GenericDialogConfigData } from '../../../types/models/common/generic-dialog/generic-dialog-config-data';
import { GenericDialogButtonType } from '../../../types/enums/common';

describe('GenericDialog', () => {
  let dialogRef: { close: ReturnType<typeof vi.fn> };

  function createComponent(data: GenericDialogConfigData): GenericDialog {
    dialogRef = { close: vi.fn() };
    TestBed.configureTestingModule({
      providers: [
        { provide: MatDialogRef, useValue: dialogRef },
        { provide: MAT_DIALOG_DATA, useValue: data },
      ],
    });
    const fixture = TestBed.createComponent(GenericDialog);
    fixture.detectChanges();
    return fixture.componentInstance;
  }

  it('should populate title, contentText, and buttons from the injected dialog data', () => {
    const data = new GenericDialogConfigData({
      title: 'Network Error',
      contentText: 'Please check your connection.',
      buttons: [{ label: 'Ok', type: GenericDialogButtonType.FILLED, closeOnClick: true }],
    });

    const component = createComponent(data);

    expect(component.title).toBe('Network Error');
    expect(component.contentText).toBe('Please check your connection.');
    expect(component.buttons).toEqual(data.buttons);
  });

  it('should close the dialog with closeValue when a closeOnClick button is clicked', () => {
    const data = new GenericDialogConfigData({
      buttons: [
        {
          label: 'Confirm',
          type: GenericDialogButtonType.FILLED,
          closeOnClick: true,
          closeValue: true,
        },
      ],
    });
    const component = createComponent(data);

    (component as unknown as { onButtonClick: (b: unknown) => void }).onButtonClick(
      data.buttons[0],
    );

    expect(dialogRef.close).toHaveBeenCalledWith(true);
  });

  it('should invoke the button callback without closing when closeOnClick is false', () => {
    const callback = vi.fn();
    const data = new GenericDialogConfigData({
      buttons: [
        { label: 'Details', type: GenericDialogButtonType.LINK, closeOnClick: false, callback },
      ],
    });
    const component = createComponent(data);

    (component as unknown as { onButtonClick: (b: unknown) => void }).onButtonClick(
      data.buttons[0],
    );

    expect(callback).toHaveBeenCalled();
    expect(dialogRef.close).not.toHaveBeenCalled();
  });
});
