'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Plus, Download, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ImportDialog } from '@/components/modules/crm/shared/ImportDialog';
import customerService from '@/services/api/customerService';

export function CustomersHeader() {
  const [showImport, setShowImport] = useState(false);

  const handleExport = (format: 'csv' | 'excel') => {
    const url = `/api/v1/customers/customers/export/?format=${format}`;
    window.open(url, '_blank');
  };

  async function handleImport(file: File, updateExisting: boolean) {
    const result = await customerService.importCustomers(file, { updateExisting });
    return result.data;
  }

  return (
    <>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Customers</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowImport(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Import
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleExport('csv')}>Export as CSV</DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleExport('excel')}>
                Export as Excel
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button asChild size="sm">
            <Link href="/customers/new">
              <Plus className="mr-2 h-4 w-4" />
              Add Customer
            </Link>
          </Button>
        </div>
      </div>

      <ImportDialog
        open={showImport}
        onOpenChange={setShowImport}
        entityName="Customers"
        onImport={handleImport}
        fields={[
          { label: 'Customer Type', key: 'customerType', required: true },
          { label: 'First Name', key: 'firstName' },
          { label: 'Last Name', key: 'lastName' },
          { label: 'Company Name', key: 'companyName' },
          { label: 'Display Name', key: 'displayName', required: true },
          { label: 'Email', key: 'email' },
          { label: 'Phone', key: 'phone' },
          { label: 'Mobile', key: 'mobile' },
          { label: 'Tax ID', key: 'taxId' },
        ]}
      />
    </>
  );
}
