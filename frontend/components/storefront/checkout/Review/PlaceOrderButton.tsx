'use client';

import { useRouter } from 'next/navigation';
import { Loader2, ShieldCheck } from 'lucide-react';
import { useStoreCheckoutStore, useStoreCartStore } from '@/stores/store';
import {
  submitOrder,
  cartItemsToOrderLines,
  type OrderSubmitPayload,
} from '@/services/storefront/orderService';

interface PlaceOrderButtonProps {
  disabled?: boolean;
}

export const PlaceOrderButton = ({ disabled = false }: PlaceOrderButtonProps) => {
  const router = useRouter();

  const isProcessing = useStoreCheckoutStore((s) => s.isProcessing);
  const setIsProcessing = useStoreCheckoutStore((s) => s.setIsProcessing);
  const setOrderInfo = useStoreCheckoutStore((s) => s.setOrderInfo);

  const contactInfo = useStoreCheckoutStore((s) => s.contactInfo);
  const shippingAddress = useStoreCheckoutStore((s) => s.shippingAddress);
  const shippingMethod = useStoreCheckoutStore((s) => s.shippingMethod);
  const paymentMethod = useStoreCheckoutStore((s) => s.paymentMethod);

  const cartItems = useStoreCartStore((s) => s.items);
  const total = useStoreCartStore((s) => s.getTotal());

  const handlePlaceOrder = async () => {
    if (isProcessing || disabled) return;

    setIsProcessing(true);

    try {
      const payload: OrderSubmitPayload = {
        contactInfo: {
          email: contactInfo.email,
          phone: contactInfo.phone,
          firstName: contactInfo.firstName,
          lastName: contactInfo.lastName,
        },
        shippingAddress: {
          province: shippingAddress.province,
          district: shippingAddress.district,
          city: shippingAddress.city,
          address1: shippingAddress.address1,
          address2: shippingAddress.address2,
          landmark: shippingAddress.landmark,
          postalCode: shippingAddress.postalCode,
        },
        shippingMethodId: shippingMethod?.id ?? '',
        paymentMethod: paymentMethod ?? '',
        items: cartItemsToOrderLines(cartItems),
      };

      const confirmation = await submitOrder(payload);

      setOrderInfo({
        orderId: confirmation.orderId,
        orderNumber: confirmation.orderNumber,
        status: confirmation.status,
      });

      router.push('/checkout/confirmation');
    } catch (err) {
      console.error('Order submission failed:', err);
      setIsProcessing(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handlePlaceOrder}
      disabled={isProcessing || disabled}
      className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-green-600 px-6 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {isProcessing ? (
        <>
          <Loader2 className="h-5 w-5 animate-spin" />
          Processing…
        </>
      ) : (
        <>
          <ShieldCheck className="h-5 w-5" />
          Place Order · ₨{total.toLocaleString()}
        </>
      )}
    </button>
  );
};
