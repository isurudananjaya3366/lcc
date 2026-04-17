interface RelatedProductsHeaderProps {
  title: string;
}

export function RelatedProductsHeader({ title }: RelatedProductsHeaderProps) {
  return (
    <h2 className="mb-6 text-xl font-bold text-gray-900">{title}</h2>
  );
}
