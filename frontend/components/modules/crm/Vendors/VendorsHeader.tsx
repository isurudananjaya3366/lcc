'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Plus, Download, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ImportDialog } from '@/components/modules/crm/shared/ImportDialog';
import { ExportButton } from '@/components/modules/crm/shared/ExportButton';
import vendorService from '@/services/api/vendorService';

export function VendorsHeader() {
  const [showImport, setShowImport] = useState(false);

  async function handleImport(file: File, updateExisting: boolean) {
    const result = await vendorService.importVendors(file, { updateExisting });
    return result.data;
  }

  return (
    <>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Vendors</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowImport(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Import
          </Button>
          <ExportButton entityName="Vendors" onExport={() => vendorService.exportVendors()} />
          <Button asChild>
            <Link href="/vendors/new">
              <Plus className="h-4 w-4 mr-2" />
              Add Vendor
            </Link>
          </Button>
        </div>
      </div>

      <ImportDialog
        open={showImport}
        onOpenChange={setShowImport}
        entityName="Vendors"
        onImport={handleImport}
        fields={[
          { label: 'Company Name', key: 'companyName', required: true },
          { label: 'Vendor Type', key: 'vendorType', required: true },
          { label: 'Category', key: 'category' },
          { label: 'Contact Name', key: 'contactName' },
          { label: 'Email', key: 'email' },
          { label: 'Phone', key: 'phone' },
          { label: 'Website', key: 'website' },
          { label: 'Payment Terms', key: 'paymentTerms' },
        ]}
      />
    </>
  );
}
