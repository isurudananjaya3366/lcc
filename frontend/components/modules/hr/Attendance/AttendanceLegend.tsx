'use client';

const legendItems = [
  { status: 'Present', color: 'bg-green-500' },
  { status: 'Absent', color: 'bg-red-500' },
  { status: 'Late', color: 'bg-yellow-500' },
  { status: 'Half Day', color: 'bg-orange-500' },
  { status: 'On Leave', color: 'bg-blue-500' },
  { status: 'Weekend', color: 'bg-gray-300' },
];

export function AttendanceLegend() {
  return (
    <div className="flex flex-wrap gap-4">
      {legendItems.map((item) => (
        <div key={item.status} className="flex items-center gap-1.5">
          <div className={`h-3 w-3 rounded-full ${item.color}`} />
          <span className="text-xs text-muted-foreground">{item.status}</span>
        </div>
      ))}
    </div>
  );
}
