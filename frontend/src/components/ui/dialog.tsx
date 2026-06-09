import React from 'react';
import { X } from 'lucide-react';
import { Card } from './card';

interface DialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function Dialog({ open, onClose, title, description, children }: DialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div 
        onClick={onClose}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" 
      />
      
      {/* Content */}
      <Card className="w-full max-w-md border border-slate-700/50 shadow-2xl relative z-10 animate-in fade-in zoom-in-95 duration-200">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-100 transition"
        >
          <X className="h-4 w-4" />
        </button>
        <div className="mb-4">
          <h3 className="text-lg font-bold text-slate-100">{title}</h3>
          {description && <p className="text-xs text-slate-400 mt-1">{description}</p>}
        </div>
        <div>
          {children}
        </div>
      </Card>
    </div>
  );
}
