import { TestBed } from '@angular/core/testing';
import { MatIconRegistry } from '@angular/material/icon';
import { Icon } from './icon';
import { IconList } from '../data/icon-list';

describe('Icon', () => {
  it('should register every icon from IconList on creation', () => {
    TestBed.configureTestingModule({});
    const registry = TestBed.inject(MatIconRegistry);
    const addSvgIconSpy = vi.spyOn(registry, 'addSvgIcon');

    TestBed.inject(Icon);

    expect(addSvgIconSpy).toHaveBeenCalledTimes(IconList.length);
    for (const icon of IconList) {
      expect(addSvgIconSpy).toHaveBeenCalledWith(icon.name, expect.anything());
    }
  });
});
