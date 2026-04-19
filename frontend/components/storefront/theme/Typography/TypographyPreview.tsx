'use client';

// ================================================================
// Typography Preview – Full preview section (headings + paragraphs)
// ================================================================

interface TypographyPreviewProps {
  headingFont: string;
  bodyFont: string;
  headingWeight?: number;
  bodyWeight?: number;
  fontSize?: number;
  lineHeight?: number;
  className?: string;
}

export function TypographyPreview({
  headingFont,
  bodyFont,
  headingWeight = 700,
  bodyWeight = 400,
  fontSize = 16,
  lineHeight = 1.5,
  className,
}: TypographyPreviewProps) {
  const headingStyle = { fontFamily: headingFont, fontWeight: headingWeight };
  const bodyStyle = {
    fontFamily: bodyFont,
    fontWeight: bodyWeight,
    fontSize: `${fontSize}px`,
    lineHeight,
  };

  return (
    <div className={`space-y-4 rounded-lg border border-gray-200 bg-white p-6 ${className ?? ''}`}>
      <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
        Typography Preview
      </p>

      {/* Heading samples */}
      <div className="space-y-2">
        <h1 className="text-4xl" style={headingStyle}>
          Heading One
        </h1>
        <h2 className="text-3xl" style={headingStyle}>
          Heading Two
        </h2>
        <h3 className="text-2xl" style={headingStyle}>
          Heading Three
        </h3>
      </div>

      {/* Body samples */}
      <div className="space-y-3" style={bodyStyle}>
        <p>
          This is a sample paragraph demonstrating how your body text will appear on the storefront.
          Good typography enhances readability and creates a professional impression for your
          customers.
        </p>
        <p>
          The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.
          1234567890 — $19.99
        </p>
      </div>

      {/* Small text */}
      <p
        className="text-gray-500"
        style={{
          fontFamily: bodyFont,
          fontWeight: bodyWeight,
          fontSize: `${fontSize * 0.875}px`,
          lineHeight,
        }}
      >
        Small helper text, captions, and fine print appear at this size.
      </p>
    </div>
  );
}
