interface SpecTableRowProps {
  label: string;
  value: string;
  isEven: boolean;
}

export function SpecTableRow({ label, value, isEven }: SpecTableRowProps) {
  return (
    <tr className={isEven ? 'bg-gray-50' : 'bg-white'}>
      <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900 w-1/3">
        {label}
      </td>
      <td className="px-4 py-3 text-sm text-gray-700">{value}</td>
    </tr>
  );
}
