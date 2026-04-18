'use client';

import { useFormContext } from 'react-hook-form';

interface FormFieldErrorProps {
  fieldName: string;
}

export const FormFieldError = ({ fieldName }: FormFieldErrorProps) => {
  const {
    formState: { errors },
  } = useFormContext();

  const error = errors[fieldName];

  if (!error?.message) return null;

  return (
    <p className="text-sm text-red-500 mt-1" role="alert">
      {error.message as string}
    </p>
  );
};
