import { RichTextDisplay } from './RichTextDisplay';

interface DescriptionTabProps {
  description: string;
}

export function DescriptionTab({ description }: DescriptionTabProps) {
  if (!description) {
    return (
      <p className="text-sm text-gray-500 italic">No description available for this product.</p>
    );
  }

  return <RichTextDisplay html={description} />;
}
