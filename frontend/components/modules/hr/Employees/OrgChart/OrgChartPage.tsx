'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Search, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { useEmployees } from '@/hooks/hr/useEmployees';
import { OrgChartNode, type OrgChartNodeData } from './OrgChartNode';
import type { Employee } from '@/types/hr';

function buildOrgTree(employees: Employee[]): OrgChartNodeData[] {
  const nodeMap = new Map<string, OrgChartNodeData>();
  const roots: OrgChartNodeData[] = [];

  for (const emp of employees) {
    nodeMap.set(emp.id, {
      id: emp.id,
      firstName: emp.firstName,
      lastName: emp.lastName,
      position: emp.positionId,
      department: emp.departmentId,
      status: emp.status,
      directReports: [],
    });
  }

  for (const emp of employees) {
    const node = nodeMap.get(emp.id);
    if (!node) continue;
    if (emp.managerId && nodeMap.has(emp.managerId)) {
      nodeMap.get(emp.managerId)!.directReports!.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

export function OrgChartPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [zoom, setZoom] = useState(1);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const { data, isLoading } = useEmployees();
  const employees = data?.data ?? [];

  const orgTree = useMemo(() => buildOrgTree(employees), [employees]);

  const handleNodeClick = (id: string) => {
    router.push(`/employees/${id}`);
  };

  const handleToggleExpand = (id: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.1, 2));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.1, 0.3));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push('/employees')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Organization Chart</h1>
            <p className="text-muted-foreground">View the organizational hierarchy</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative w-60">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search employees..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button variant="outline" size="icon" onClick={handleZoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground w-12 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <Button variant="outline" size="icon" onClick={handleZoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={handleResetZoom}>
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : orgTree.length === 0 ? (
        <div className="flex min-h-[400px] items-center justify-center text-muted-foreground">
          No employee data available to build the organization chart.
        </div>
      ) : (
        <div className="overflow-auto rounded-lg border bg-muted/20 p-8">
          <div
            className="flex justify-center transition-transform"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}
          >
            <div className="flex flex-col items-center gap-4">
              {orgTree.map((root) => (
                <OrgChartNode
                  key={root.id}
                  node={root}
                  onNodeClick={handleNodeClick}
                  isExpanded={!expandedNodes.has(root.id)}
                  onToggleExpand={handleToggleExpand}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
