import { Link } from "react-router-dom";
import { motion } from "motion/react";
import {
  Search,
  Zap,
  Quote,
  LayoutGrid,
  FileUp,
  ShieldCheck,
} from "lucide-react";
import { HeroSection } from "../components/hero/HeroSection";

const features = [
  {
    icon: Search,
    title: "Hybrid RAG Search",
    desc: "BM25 keyword + vector similarity + AI re-ranking. Finds exactly what you need.",
  },
  {
    icon: Zap,
    title: "Real-time Streaming",
    desc: "Answers stream in live via SSE. No waiting for full responses \u2014 see results instantly.",
  },
  {
    icon: Quote,
    title: "Source Citations",
    desc: "Every answer cites its sources with confidence scores. Trust but verify.",
  },
  {
    icon: LayoutGrid,
    title: "Notion Integration",
    desc: "One-click OAuth connect. Pages, databases, and blocks auto-ingested and indexed.",
  },
  {
    icon: FileUp,
    title: "File Uploads",
    desc: "Upload PDFs, text files, and markdown. Chunked and embedded alongside your Notion docs.",
  },
  {
    icon: ShieldCheck,
    title: "Workspace Isolation",
    desc: "Multi-tenant by design. Your data stays yours \u2014 queries scoped to your workspaces only.",
  },
];

const techStack = [
  "Google Gemini",
  "Notion API",
  "ChromaDB",
  "FastAPI",
  "React",
];

const steps = [
  {
    num: 1,
    title: "Connect Notion",
    desc: "OAuth in one click. We auto-index your pages, databases, and blocks.",
  },
  {
    num: 2,
    title: "Ask a Question",
    desc: "Type naturally. WorkMate searches across all your connected documents.",
  },
  {
    num: 3,
    title: "Get Sourced Answers",
    desc: "Streamed responses with citations, confidence scores, and source links.",
  },
];

const fadeInUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-60px" },
  transition: { duration: 0.5 },
};

export function LandingPage() {
  return (
    <>
      <HeroSection />

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent" />

      <motion.section className="py-8 text-center" {...fadeInUp}>
        <p className="mb-4 text-[11px] uppercase tracking-widest text-white/30">
          Built with
        </p>
        <div className="flex flex-wrap items-center justify-center gap-8 text-xs text-white/25 md:gap-12">
          {techStack.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
      </motion.section>

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      <section className="px-6 py-16 md:py-24">
        <motion.div className="mb-10 text-center" {...fadeInUp}>
          <p className="mb-3 text-[10px] uppercase tracking-[3px] text-purple-500">
            Features
          </p>
          <h2 className="text-xl font-bold text-white md:text-2xl">
            Everything you need to unlock
            <br />
            your team&apos;s knowledge
          </h2>
        </motion.div>
        <div className="mx-auto grid max-w-5xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-6 transition-colors hover:border-white/[0.12]"
              {...fadeInUp}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-purple-600/20 bg-purple-600/[0.08]">
                <f.icon className="h-5 w-5 text-purple-500" />
              </div>
              <h3 className="mb-1.5 text-sm font-semibold text-white">
                {f.title}
              </h3>
              <p className="text-xs leading-relaxed text-white/40">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      <section id="how-it-works" className="px-6 py-16 md:py-24">
        <motion.div className="mb-10 text-center" {...fadeInUp}>
          <p className="mb-3 text-[10px] uppercase tracking-[3px] text-purple-500">
            How It Works
          </p>
          <h2 className="text-xl font-bold text-white md:text-2xl">
            Three steps to instant answers
          </h2>
        </motion.div>
        <div className="mx-auto flex max-w-3xl flex-col items-start gap-8 md:flex-row md:items-center md:gap-6">
          {steps.map((s, i) => (
            <motion.div
              key={s.num}
              className="flex flex-1 flex-col items-center text-center"
              {...fadeInUp}
              transition={{ duration: 0.5, delay: i * 0.15 }}
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-purple-600/30 bg-purple-600/10 text-lg font-bold text-purple-500">
                {s.num}
              </div>
              <h3 className="mb-1 text-sm font-semibold text-white">
                {s.title}
              </h3>
              <p className="text-xs leading-relaxed text-white/40">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      <motion.section
        className="relative px-6 py-16 text-center md:py-24"
        {...fadeInUp}
      >
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[200px] w-[400px] -translate-x-1/2 -translate-y-1/2 bg-[radial-gradient(ellipse,rgba(124,58,237,0.06)_0%,transparent_70%)]" />
        <div className="relative z-10">
          <h2 className="text-2xl font-bold text-white">
            Ready to try WorkMate?
          </h2>
          <p className="mt-3 text-sm text-white/40">
            Connect your Notion workspace and start getting answers in minutes.
          </p>
          <Link
            to="/login"
            className="mt-6 inline-block rounded-lg bg-purple-600 px-8 py-3 text-sm font-medium text-white transition-colors hover:bg-purple-700"
          >
            Get Started Free
          </Link>
        </div>
      </motion.section>
    </>
  );
}
