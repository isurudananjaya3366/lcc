'use client';

import { useState } from 'react';
import { ZoomIn, ZoomOut, Maximize2, RefreshCw, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface InvoicePDFPreviewProps {
  invoiceId: string;
  pdfUrl?: string;
  isLoading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
}

export function InvoicePDFPreview({
  invoiceId,
  pdfUrl,
  isLoading,
  error,
  onRetry,
}: InvoicePDFPreviewProps) {
  const [zoom, setZoom] = useState(100);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 50));
  const handleFitWidth = () => setZoom(100);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex min-h-[500px] items-center justify-center pt-6">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            <p className="text-sm text-gray-500">Loading PDF preview...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex min-h-[300px] items-center justify-center pt-6">
          <div className="flex flex-col items-center gap-3 text-center">
            <p className="text-sm text-red-600">Failed to load PDF preview</p>
            {onRetry && (
              <Button variant="outline" size="sm" onClick={onRetry}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Retry
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      {/* Controls */}
      <div className="flex items-center justify-between border-b p-2">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="min-w-[4rem] text-center text-sm">{zoom}%</span>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="ml-1 h-8 text-xs" onClick={handleFitWidth}>
            Fit Width
          </Button>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={() => {
            if (pdfUrl) window.open(pdfUrl, '_blank');
          }}
        >
          <Maximize2 className="h-4 w-4" />
        </Button>
      </div>

      {/* Preview Area */}
      <CardContent className="p-0">
        {pdfUrl ? (
          <div className="overflow-auto" style={{ maxHeight: '600px' }}>
            <iframe
              src={`${pdfUrl}#view=FitH`}
              title={`Invoice ${invoiceId} PDF`}
              className="w-full border-0"
              style={{
                height: '600px',
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top left',
                width: `${10000 / zoom}%`,
              }}
            />
          </div>
        ) : (
          <div className="flex min-h-[400px] items-center justify-center">
            <p className="text-sm text-gray-500">PDF preview not available</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
