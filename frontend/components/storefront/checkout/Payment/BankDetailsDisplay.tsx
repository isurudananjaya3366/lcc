'use client';

import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface BankAccount {
  bank: string;
  branch: string;
  accountName: string;
  accountNumber: string;
  swiftCode: string;
}

const primaryAccount: BankAccount = {
  bank: 'Commercial Bank of Ceylon',
  branch: 'Colombo Main Branch',
  accountName: 'LankaCommerce Cloud (Pvt) Ltd',
  accountNumber: '8010-12345678',
  swiftCode: 'CCEYLKLX',
};

const alternativeAccounts: BankAccount[] = [
  {
    bank: 'Bank of Ceylon (BOC)',
    branch: 'Head Office',
    accountName: 'LankaCommerce Cloud (Pvt) Ltd',
    accountNumber: '7920-54321098',
    swiftCode: 'BABORLKLX',
  },
  {
    bank: 'Sampath Bank',
    branch: 'Colombo Branch',
    accountName: 'LankaCommerce Cloud (Pvt) Ltd',
    accountNumber: '1060-87654321',
    swiftCode: 'SAPHLKLX',
  },
];

const AccountRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex justify-between text-sm">
    <span className="text-gray-500">{label}</span>
    <span className="font-medium text-gray-900">{value}</span>
  </div>
);

export const BankDetailsDisplay = () => {
  const [copied, setCopied] = useState<string | null>(null);

  const handleCopy = async (accountNumber: string) => {
    try {
      await navigator.clipboard.writeText(accountNumber);
      setCopied(accountNumber);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      // Clipboard API may not be available
    }
  };

  const renderAccount = (account: BankAccount, isPrimary = false) => (
    <div
      key={account.accountNumber}
      className={`rounded-lg border p-3 space-y-2 ${
        isPrimary ? 'border-blue-200 bg-blue-50/50' : 'border-gray-200 bg-gray-50'
      }`}
    >
      <p className="text-sm font-semibold text-gray-900">{account.bank}</p>
      <AccountRow label="Branch" value={account.branch} />
      <AccountRow label="Account Name" value={account.accountName} />
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">Account Number</span>
        <div className="flex items-center gap-1.5">
          <span className="font-mono font-medium text-gray-900">{account.accountNumber}</span>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleCopy(account.accountNumber);
            }}
            className="inline-flex items-center justify-center h-6 w-6 rounded hover:bg-gray-200 transition-colors"
            title="Copy account number"
          >
            {copied === account.accountNumber ? (
              <Check className="h-3.5 w-3.5 text-green-600" />
            ) : (
              <Copy className="h-3.5 w-3.5 text-gray-400" />
            )}
          </button>
        </div>
      </div>
      <AccountRow label="Swift Code" value={account.swiftCode} />
    </div>
  );

  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-gray-700">Bank Account Details</p>
      {renderAccount(primaryAccount, true)}

      <p className="text-xs font-medium text-gray-500 mt-3">Alternative Accounts</p>
      <div className="space-y-2">
        {alternativeAccounts.map((account) => renderAccount(account))}
      </div>

      <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
        <p className="text-xs text-amber-800">
          <span className="font-medium">Important:</span> Please use your Order ID as payment
          reference when making the transfer.
        </p>
      </div>
    </div>
  );
};
