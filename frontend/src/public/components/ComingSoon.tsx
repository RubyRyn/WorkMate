import { Link } from "react-router-dom";
import type { LucideIcon } from "lucide-react";

interface ComingSoonProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export function ComingSoon({ icon: Icon, title, description }: ComingSoonProps) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-6 text-center">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-purple-600/[0.08] border border-purple-600/20">
        <Icon className="h-7 w-7 text-purple-500" />
      </div>
      <h1 className="text-2xl font-bold text-white">{title}</h1>
      <p className="mt-2 text-sm text-white/40">{description}</p>
      <Link
        to="/"
        className="mt-6 text-sm text-purple-500 transition-colors hover:text-purple-400"
      >
        &larr; Back to Home
      </Link>
    </div>
  );
}
