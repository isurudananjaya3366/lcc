interface ProductTitleProps {
  name: string;
}

export function ProductTitle({ name }: ProductTitleProps) {
  return (
    <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
      {name}
    </h1>
  );
}
