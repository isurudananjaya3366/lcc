interface ItemNameProps {
  name: string;
  variant?: string;
  sku?: string;
}

export function ItemName({ name, variant, sku }: ItemNameProps) {
  return (
    <div title={variant ? `${name} — ${variant}` : name}>
      <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">{name}</p>
      {variant && <p className="truncate text-xs text-gray-500 dark:text-gray-400">{variant}</p>}
      {sku && <p className="truncate text-[10px] text-gray-400 dark:text-gray-500">{sku}</p>}
    </div>
  );
}
