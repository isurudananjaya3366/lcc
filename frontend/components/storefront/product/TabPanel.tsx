interface TabPanelProps {
  children: React.ReactNode;
  isActive: boolean;
}

export function TabPanel({ children, isActive }: TabPanelProps) {
  if (!isActive) return null;

  return (
    <div role="tabpanel" className="py-6">
      {children}
    </div>
  );
}
