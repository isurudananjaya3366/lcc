'use client';

// ================================================================
// Font Preview – Preview a font on sample text
// ================================================================

interface FontPreviewProps {
  fontFamily: string;
  fontType: 'heading' | 'body';
  sampleText?: string;
  showInfo?: boolean;
  className?: string;
}

const DEFAULT_HEADING = 'The Quick Brown Fox';
const DEFAULT_BODY =
  'This is how your body text will appear. Choose a font that is comfortable to read for longer periods of content.';

export function FontPreview({
  fontFamily,
  fontType,
  sampleText,
  showInfo = true,
  className,
}: FontPreviewProps) {
  const isHeading = fontType === 'heading';

  return (
    <div className={`rounded-lg border border-gray-200 bg-white p-4 ${className ?? ''}`}>
      {showInfo && (
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
          {isHeading ? 'Heading Preview' : 'Body Preview'}
        </p>
      )}

      <div style={{ fontFamily }}>
        {isHeading ? (
          <div className="space-y-1">
            <p className="text-2xl font-bold">{sampleText ?? DEFAULT_HEADING}</p>
            <p className="text-lg font-semibold">Section Title</p>
            <p className="text-base font-semibold">Subsection</p>
          </div>
        ) : (
          <p className="text-sm leading-relaxed">{sampleText ?? DEFAULT_BODY}</p>
        )}
      </div>
    </div>
  );
}
