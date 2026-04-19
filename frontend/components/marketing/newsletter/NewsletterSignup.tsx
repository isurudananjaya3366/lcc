'use client';

import { useState } from 'react';
import { Mail, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useNewsletterSubscribe } from '@/hooks/marketing/useNewsletter';

interface NewsletterSignupProps {
  variant?: 'inline' | 'card' | 'footer';
  source?: string;
  className?: string;
}

export function NewsletterSignup({ variant = 'inline', source = 'website', className = '' }: NewsletterSignupProps) {
  const [email, setEmail] = useState('');
  const { mutate: subscribe, isPending, isSuccess, isError, error } = useNewsletterSubscribe();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    subscribe({ email: email.trim(), source });
  };

  if (isSuccess) {
    return (
      <div className={`flex items-center gap-2 text-green-600 ${className}`}>
        <CheckCircle className="h-5 w-5" />
        <span className="text-sm font-medium">Check your email to confirm your subscription!</span>
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={`rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 p-8 text-white ${className}`}>
        <Mail className="mx-auto mb-4 h-10 w-10" />
        <h3 className="text-center text-xl font-bold">Stay in the Loop</h3>
        <p className="mt-2 text-center text-sm text-blue-100">
          Get exclusive deals, new arrivals & flash sale alerts
        </p>
        <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-2 sm:flex-row">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="flex-1 rounded-lg px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
            required
            disabled={isPending}
          />
          <button
            type="submit"
            disabled={isPending}
            className="rounded-lg bg-white px-6 py-2.5 text-sm font-semibold text-blue-600 hover:bg-blue-50 disabled:opacity-50"
          >
            {isPending ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Subscribe'}
          </button>
        </form>
        {isError && (
          <p className="mt-2 flex items-center gap-1 text-xs text-red-200">
            <AlertCircle className="h-3 w-3" /> {error.message}
          </p>
        )}
      </div>
    );
  }

  if (variant === 'footer') {
    return (
      <div className={className}>
        <h4 className="text-sm font-semibold text-gray-200">Newsletter</h4>
        <p className="mt-1 text-xs text-gray-400">Subscribe for exclusive deals</p>
        <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="flex-1 rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            required
            disabled={isPending}
          />
          <button
            type="submit"
            disabled={isPending}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mail className="h-4 w-4" />}
          </button>
        </form>
        {isError && <p className="mt-1 text-xs text-red-400">{error.message}</p>}
      </div>
    );
  }

  // inline variant
  return (
    <form onSubmit={handleSubmit} className={`flex gap-2 ${className}`}>
      <div className="relative flex-1">
        <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email for deals"
          className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          required
          disabled={isPending}
        />
      </div>
      <button
        type="submit"
        disabled={isPending}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Subscribe'}
      </button>
      {isError && (
        <p className="text-xs text-red-500">{error.message}</p>
      )}
    </form>
  );
}
