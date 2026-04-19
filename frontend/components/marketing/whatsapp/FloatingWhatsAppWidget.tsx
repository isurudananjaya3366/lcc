'use client';

import { useState } from 'react';
import { X, MessageCircle } from 'lucide-react';
import { WhatsAppIcon } from './WhatsAppIcon';
import { getWhatsAppUrl, getWhatsAppStatus } from '@/lib/marketing/whatsapp';

interface FloatingWhatsAppWidgetProps {
  className?: string;
}

export function FloatingWhatsAppWidget({ className = '' }: FloatingWhatsAppWidgetProps) {
  const [expanded, setExpanded] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const status = getWhatsAppStatus();

  return (
    <>
      {/* CSS keyframe animations injected via style tag */}
      <style>{`
        @keyframes wa-bounce-in {
          0% { opacity: 0; transform: scale(0) translateY(20px); }
          60% { transform: scale(1.1) translateY(-4px); }
          80% { transform: scale(0.95) translateY(2px); }
          100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes wa-pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(37,211,102,0.5); }
          50% { box-shadow: 0 0 0 10px rgba(37,211,102,0); }
        }
        @media (prefers-reduced-motion: no-preference) {
          .wa-fab-enter {
            animation: wa-bounce-in 0.5s cubic-bezier(0.36,0.07,0.19,0.97) both;
            animation-delay: 3s;
            opacity: 0;
          }
          .wa-fab-pulse:not(:hover) {
            animation: wa-pulse 2s ease-in-out infinite;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .wa-fab-enter { animation: none; opacity: 1; }
          .wa-fab-pulse { animation: none; }
        }
      `}</style>

      <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
        {expanded && (
          <div className="mb-3 w-72 overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-gray-200">
            {/* Header */}
          <div className="bg-[#075E54] p-4 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/20">
                  <WhatsAppIcon size={20} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Customer Support</p>
                  <div className="flex items-center gap-1">
                    <span className={`h-2 w-2 rounded-full ${status.isOnline ? 'bg-green-400' : 'bg-gray-400'}`} />
                    <span className="text-xs text-green-100">{status.isOnline ? 'Online' : 'Offline'}</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setExpanded(false)} className="rounded-full p-1 hover:bg-white/10" type="button">
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="bg-[#ECE5DD] p-4">
            <div className="rounded-lg bg-white p-3 shadow-sm">
              <p className="text-sm text-gray-700">{status.message}</p>
              <span className="mt-1 block text-right text-[10px] text-gray-400">
                {new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Colombo' })}
              </span>
            </div>
          </div>

          {/* Action */}
          <div className="p-3">
            <a
              href={getWhatsAppUrl('general')}
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-full items-center justify-center gap-2 rounded-full bg-[#25D366] py-2.5 text-sm font-medium text-white transition-colors hover:bg-[#20BD5A]"
            >
              <MessageCircle className="h-4 w-4" />
              Start Chat
            </a>
          </div>
        </div>
      )}

      {/* FAB Button */}
      <div className="relative wa-fab-enter">
        {/* Hover tooltip */}
        {showTooltip && !expanded && (
          <div className="absolute bottom-full right-0 mb-2 whitespace-nowrap rounded-lg bg-gray-900 px-3 py-1.5 text-xs text-white shadow-lg">
            Chat with us on WhatsApp
            <span className="absolute -bottom-1 right-4 h-2 w-2 rotate-45 bg-gray-900" />
          </div>
        )}
        <button
          onClick={() => setExpanded(!expanded)}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          className="wa-fab-pulse flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] text-white shadow-lg transition-transform hover:scale-110 hover:bg-[#20BD5A]"
          type="button"
          title="Chat with us on WhatsApp"
          aria-label="Open WhatsApp chat"
        >
          {expanded ? <X className="h-6 w-6" /> : <WhatsAppIcon size={28} />}
        </button>
      </div>
    </div>
    </>
  );
}
