import React, { type FC } from 'react';

const SkipToContent: FC = () => {
  return (
    <a
      href="#main-content"
      className="absolute left-0 top-0 -translate-y-20 z-50 bg-green-700 text-white px-4 py-2 rounded shadow-lg font-semibold text-sm transition-transform duration-200 focus:translate-y-0 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
    >
      Skip to main content
    </a>
  );
};

export default SkipToContent;
