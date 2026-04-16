import React, { type FC } from 'react';

const FooterPlaceholder: FC = () => {
  if (process.env.NODE_ENV !== 'development') {
    return (
      <footer className="bg-gray-900 text-gray-400" role="contentinfo">
        <div className="container mx-auto px-4 py-6 text-center text-sm">
          &copy; {new Date().getFullYear()} LankaCommerce Cloud. All rights reserved.
        </div>
      </footer>
    );
  }

  return (
    <footer
      className="bg-gray-800 border-t-2 border-dashed border-gray-600 text-gray-300 py-12 text-center min-h-[120px]"
      role="contentinfo"
    >
      <p className="text-lg font-medium">Footer Component (Coming Soon)</p>
      <p className="text-sm text-gray-500 mt-2">
        Will be implemented in Group E — Footer Components
      </p>
    </footer>
  );
};

export default FooterPlaceholder;
