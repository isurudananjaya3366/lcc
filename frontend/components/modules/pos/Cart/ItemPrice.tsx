interface ItemPriceProps {
  lineTotal: number;
  unitPrice: number;
  quantity: number;
  discountAmount?: number;
}

export function ItemPrice({ lineTotal, unitPrice, quantity, discountAmount = 0 }: ItemPriceProps) {
  return (
    <div className="shrink-0 text-right">
      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
        ₨ {lineTotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
      </p>
      {quantity > 1 && (
        <p className="text-[10px] text-gray-400">
          {quantity} × ₨ {unitPrice.toLocaleString('en-LK')}
        </p>
      )}
      {discountAmount > 0 && (
        <p className="text-[10px] text-green-600">
          -₨ {discountAmount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </p>
      )}
    </div>
  );
}
