import { motion } from "motion/react";

export function ChatPreview() {
  return (
    <div className="mx-auto mt-8 max-w-md rounded-xl border border-white/[0.08] bg-white/[0.03] p-5 text-left">
      <p className="text-sm text-white/40">
        <span className="mr-1">{"\u{1F4AC}"}</span>
        <span className="text-white/60">
          What did we decide about the pricing model?
        </span>
      </p>

      <div className="my-3 h-px bg-white/[0.05]" />

      <div className="text-sm leading-relaxed text-white/50">
        <span className="font-medium text-purple-500">WorkMate</span> — Based
        on your Q3 Strategy Doc and Product Roadmap, the team agreed on a
        freemium model with...
        <motion.span
          className="ml-0.5 inline-block h-3.5 w-1.5 rounded-sm bg-purple-500 align-middle"
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
        />
      </div>

      <div className="mt-3 flex gap-2">
        <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] text-emerald-500">
          2 sources cited
        </span>
        <span className="rounded bg-purple-500/10 px-2 py-0.5 text-[10px] text-purple-500">
          High confidence
        </span>
      </div>
    </div>
  );
}
