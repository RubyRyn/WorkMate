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
          <button className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-purple-700 dark:text-purple-300 bg-purple-100 dark:bg-purple-900/50 rounded-full hover:bg-purple-200 dark:hover:bg-purple-900/80 transition-colors ml-1 align-super cursor-pointer">
            {number}
          </button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-3">
          <div className="flex items-start gap-2">
            <FileText className="w-4 h-4 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-slate-900 dark:text-slate-100 mb-1">{source}</p>
              <p className="text-xs text-slate-600 dark:text-slate-400 italic">"{excerpt}"</p>
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
