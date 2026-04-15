import type { POSSale } from '../types';

interface ReceiptContentProps {
  sale: POSSale;
}

export function ReceiptContent({ sale }: ReceiptContentProps) {
  const fmt = (n: number) => n.toLocaleString('en-LK', { minimumFractionDigits: 2 });

  return (
    <div className="space-y-3 text-xs text-gray-800 dark:text-gray-200">
      {/* Store Header */}
      <div className="text-center">
        <p className="text-sm font-bold uppercase">LankaCommerce</p>
        <p className="text-[10px] text-gray-500">Sri Lanka</p>
      </div>

      <hr className="border-dashed border-gray-300 dark:border-gray-700" />

      {/* Transaction Details */}
      <div className="space-y-0.5">
        <p>Receipt #: {sale.referenceNumber}</p>
        <p>Date: {new Date(sale.completedAt ?? sale.createdAt).toLocaleString()}</p>
        {sale.customer && <p>Customer: {sale.customer.name}</p>}
      </div>

      <hr className="border-dashed border-gray-300 dark:border-gray-700" />

      {/* Items */}
      <div className="space-y-1">
        {sale.items.map((item) => (
          <div key={item.id}>
            <div className="flex justify-between">
              <span className="flex-1">
                {item.productName}
                {item.variantName && ` (${item.variantName})`}
              </span>
              <span className="ml-2 tabular-nums">{fmt(item.lineTotal)}</span>
            </div>
            <p className="text-[10px] text-gray-400">
              {item.quantity} x {fmt(item.unitPrice)}
            </p>
          </div>
        ))}
      </div>

      <hr className="border-dashed border-gray-300 dark:border-gray-700" />

      {/* Totals */}
      <div className="space-y-0.5">
        <div className="flex justify-between">
          <span>Subtotal</span>
          <span className="tabular-nums">{fmt(sale.subtotal)}</span>
        </div>
        {sale.discountAmount > 0 && (
          <div className="flex justify-between text-green-600">
            <span>Discount</span>
            <span className="tabular-nums">-{fmt(sale.discountAmount)}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span>Tax</span>
          <span className="tabular-nums">{fmt(sale.taxAmount)}</span>
        </div>
        <div className="flex justify-between border-t border-gray-300 pt-0.5 text-sm font-bold dark:border-gray-600">
          <span>TOTAL</span>
          <span className="tabular-nums">₨ {fmt(sale.grandTotal)}</span>
        </div>
      </div>

      <hr className="border-dashed border-gray-300 dark:border-gray-700" />

      {/* Payment Details */}
      <div className="space-y-0.5">
        <p className="font-medium">Payment:</p>
        {sale.payments.map((p) => (
          <div key={p.id} className="flex justify-between">
            <span className="capitalize">{p.method.replace('_', ' ')}</span>
            <span className="tabular-nums">{fmt(p.amount)}</span>
          </div>
        ))}
        {sale.payments.some((p) => p.changeDue && p.changeDue > 0) && (
          <div className="flex justify-between">
            <span>Change</span>
            <span className="tabular-nums">
              {fmt(sale.payments.reduce((s, p) => s + (p.changeDue ?? 0), 0))}
            </span>
          </div>
        )}
      </div>

      <hr className="border-dashed border-gray-300 dark:border-gray-700" />

      {/* Footer */}
      <div className="text-center text-[10px] text-gray-400">
        <p>Thank you for your purchase!</p>
        <p>Return policy: 7 days with receipt</p>
      </div>
    </div>
  );
}
