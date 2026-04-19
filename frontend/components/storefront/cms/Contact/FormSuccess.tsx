import { CheckCircle } from 'lucide-react';

interface FormSuccessProps {
  show: boolean;
}

export function FormSuccess({ show }: FormSuccessProps) {
  if (!show) return null;

  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border bg-green-50 p-8 text-center dark:bg-green-950">
      <CheckCircle className="h-10 w-10 text-green-600 dark:text-green-400" />
      <h3 className="text-lg font-semibold">Thank you!</h3>
      <p className="text-sm text-muted-foreground">
        Your message has been sent successfully. We&apos;ll get back to you as soon as possible.
      </p>
    </div>
  );
}
