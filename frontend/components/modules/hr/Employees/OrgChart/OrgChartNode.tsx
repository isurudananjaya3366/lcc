'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { EmployeeAvatar } from '../EmployeeAvatar';
import { cn } from '@/lib/utils';

export interface OrgChartNodeData {
  id: string;
  firstName: string;
  lastName: string;
  position: string;
  department: string;
  status: string;
  directReports?: OrgChartNodeData[];
}

interface OrgChartNodeProps {
  node: OrgChartNodeData;
  onNodeClick?: (id: string) => void;
  isExpanded?: boolean;
  onToggleExpand?: (id: string) => void;
}

export function OrgChartNode({
  node,
  onNodeClick,
  isExpanded = true,
  onToggleExpand,
}: OrgChartNodeProps) {
  const hasChildren = node.directReports && node.directReports.length > 0;

  return (
    <div className="flex flex-col items-center">
      <Card
        className={cn(
          'w-48 cursor-pointer transition-shadow hover:shadow-md',
          'border-2 border-transparent hover:border-primary/30'
        )}
        onClick={() => onNodeClick?.(node.id)}
      >
        <CardContent className="flex flex-col items-center gap-2 p-4">
          <EmployeeAvatar firstName={node.firstName} lastName={node.lastName} size="md" />
          <div className="text-center">
            <p className="text-sm font-semibold">
              {node.firstName} {node.lastName}
            </p>
            <p className="text-xs text-muted-foreground">{node.position}</p>
            <p className="text-xs text-muted-foreground">{node.department}</p>
          </div>
          <Badge variant={node.status === 'ACTIVE' ? 'default' : 'secondary'} className="text-xs">
            {node.status.replace('_', ' ')}
          </Badge>
        </CardContent>
      </Card>

      {hasChildren && (
        <>
          <button
            className="mt-2 mb-2 h-6 w-6 rounded-full border bg-background text-xs font-medium hover:bg-muted"
            onClick={(e) => {
              e.stopPropagation();
              onToggleExpand?.(node.id);
            }}
          >
            {isExpanded ? '−' : '+'}
          </button>

          {isExpanded && (
            <>
              <div className="h-4 w-px bg-border" />
              <div className="flex gap-6">
                {node.directReports!.map((child) => (
                  <div key={child.id} className="flex flex-col items-center">
                    <div className="h-4 w-px bg-border" />
                    <OrgChartNode
                      node={child}
                      onNodeClick={onNodeClick}
                      isExpanded={isExpanded}
                      onToggleExpand={onToggleExpand}
                    />
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
