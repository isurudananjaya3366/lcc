'use client';

import { QuickButton } from './QuickButton';
import type { QuickButton as QBType } from '../types';

interface QuickButtonGridProps {
  buttons: QBType[];
  onButtonClick: (button: QBType) => void;
}

export function QuickButtonGrid({ buttons, onButtonClick }: QuickButtonGridProps) {
  if (buttons.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-400 dark:text-gray-500">
        No quick access buttons configured
      </p>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-2 md:grid-cols-4 lg:grid-cols-6">
      {buttons.map((button) => (
        <QuickButton key={button.id} button={button} onClick={onButtonClick} />
      ))}
    </div>
  );
}
