import { MessageCircle } from 'lucide-react';

export function WhatsAppContact() {
  return (
    <a
      href="https://wa.me/94771234567"
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-3 rounded-lg border bg-green-50 p-4 text-green-700 hover:bg-green-100 transition-colors dark:bg-green-950 dark:text-green-300 dark:hover:bg-green-900"
    >
      <MessageCircle className="h-6 w-6 shrink-0" />
      <div>
        <p className="font-semibold">Chat on WhatsApp</p>
        <p className="text-sm opacity-80">+94 77 123 4567</p>
      </div>
    </a>
  );
}
