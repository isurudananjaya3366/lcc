import { MapPin, Phone, Mail, Clock, MessageCircle } from 'lucide-react';

export function ContactInfo() {
  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-card p-6 space-y-5">
        <h2 className="text-lg font-semibold">Get in Touch</h2>

        <div className="flex items-start gap-3">
          <MapPin className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">Address</p>
            <p className="text-sm text-muted-foreground">
              42 Galle Road, Colombo 03, Sri Lanka
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Phone className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">Phone</p>
            <p className="text-sm text-muted-foreground">+94 11 234 5678</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Mail className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">Email</p>
            <p className="text-sm text-muted-foreground">info@store.lk</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Clock className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">Business Hours</p>
            <p className="text-sm text-muted-foreground">Mon–Sat 9:00 AM – 6:00 PM</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <MessageCircle className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">WhatsApp</p>
            <a
              href="https://wa.me/94771234567"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              +94 77 123 4567
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
