import { MousePointer2, Check } from 'lucide-react';

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <MousePointer2 size={24} className="text-primary" />
        <Check size={14} className="absolute -bottom-1 -right-1 text-primary" />
      </div>
      <span className="font-bold text-xl text-foreground">RollCall</span>
    </div>
  );
} 