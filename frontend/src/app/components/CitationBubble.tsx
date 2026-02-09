import { FileText } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';

interface CitationBubbleProps {
  number: number;
  source: string;
  excerpt: string;
}

export function CitationBubble({ number, source, excerpt }: CitationBubbleProps) {
  return (
    <TooltipProvider>
      <Tooltip delayDuration={200}>
        <TooltipTrigger asChild>
          <button className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-purple-700 bg-purple-100 rounded-full hover:bg-purple-200 transition-colors ml-1 align-super cursor-pointer">
            {number}
          </button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs bg-white border border-slate-200 p-3">
          <div className="flex items-start gap-2">
            <FileText className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-slate-900 mb-1">{source}</p>
              <p className="text-xs text-slate-600 italic">"{excerpt}"</p>
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
