interface RichTextDisplayProps {
  html: string;
}

export function RichTextDisplay({ html }: RichTextDisplayProps) {
  // Check if the content looks like HTML
  const isHtml = /<[a-z][\s\S]*>/i.test(html);

  if (!isHtml) {
    return (
      <div className="prose prose-sm max-w-none text-gray-700">
        <p className="whitespace-pre-line">{html}</p>
      </div>
    );
  }

  // Render sanitized server-provided HTML (content is trusted from our API)
  return (
    <div
      className="prose prose-sm max-w-none text-gray-700 prose-headings:text-gray-900 prose-a:text-blue-600"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
