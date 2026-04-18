'use client';

import { Button } from '@/components/ui/button';

export function SocialLoginSection() {
  return (
    <div className="space-y-4">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Button variant="outline" disabled title="Coming soon" type="button">
          Google
        </Button>
        <Button variant="outline" disabled title="Coming soon" type="button">
          Facebook
        </Button>
      </div>
    </div>
  );
}
