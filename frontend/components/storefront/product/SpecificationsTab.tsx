import { SpecTableRow } from './SpecTableRow';

interface SpecificationsTabProps {
  specifications?: Record<string, string>;
}

export function SpecificationsTab({ specifications }: SpecificationsTabProps) {
  if (!specifications || Object.keys(specifications).length === 0) {
    return (
      <p className="text-sm text-gray-500 italic">No specifications available for this product.</p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <tbody className="divide-y divide-gray-200">
          {Object.entries(specifications).map(([key, value], index) => (
            <SpecTableRow key={key} label={key} value={value} isEven={index % 2 === 0} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
