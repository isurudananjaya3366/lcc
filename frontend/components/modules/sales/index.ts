/**
 * Sales Module — Component Index
 *
 * Re-exports all sub-module components for convenient importing:
 *   import { OrdersList, InvoiceDetail, RecordPaymentModal } from '@/components/modules/sales';
 */

// ── Orders ─────────────────────────────────────────────────────
export {
  OrdersList,
  OrdersHeader,
  OrderSummaryCards,
  OrderFilters,
  OrdersTable,
  orderTableColumns,
  OrderDetail,
  NewOrderForm,
  OrderStatusBadge,
  OrderActionsCell,
} from './Orders';

// ── Invoices ───────────────────────────────────────────────────
export {
  InvoicesList,
  InvoiceDetail,
  InvoicesHeader,
  InvoiceSummaryCards,
  InvoiceFilters,
  InvoicesTable,
  InvoiceTableColumns,
  getInvoiceColumns,
  InvoiceStatusBadge,
  InvoiceActionsCell,
  InvoiceHeaderSection,
  InvoicePDFPreview,
  DownloadPDFButton,
  PrintInvoiceButton,
  SendInvoiceModal,
  PaymentHistory,
} from './Invoices';

// ── Quotes ─────────────────────────────────────────────────────
export {
  QuotesList,
  QuoteDetail,
  NewQuoteForm,
  QuotesHeader,
  QuoteStatusBadge,
  QuoteFilters,
  QuotesTable,
  getQuoteColumns,
  QuoteDetailsHeader,
  ConversionModal,
} from './Quotes';

// ── Payments ───────────────────────────────────────────────────
export {
  RecordPaymentModal,
  PaymentMethodSelect,
  AmountInput,
  ReferenceNumberInput,
  PaymentDatePicker,
  PaymentNotesField,
} from './Payments';

// ── Shipping ───────────────────────────────────────────────────
export { ShippingLabelModal, CarrierSelection, TrackingInput, PrintLabelButton } from './Shipping';
