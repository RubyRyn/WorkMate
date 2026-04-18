import { motion } from "motion/react";
import { Github, Linkedin } from "lucide-react";

const fadeInUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-60px" },
  transition: { duration: 0.5 },
};

const team = [
  {
    name: "Emmanuel Owusu",
    initials: "EO",
    role: "DevOps Engineer",
    bio: "Cloud infrastructure, CI/CD pipelines, Docker containerization",
    github: "#",
    linkedin: "#",
  },
  {
    name: "Jubaida Tasnim",
    initials: "JT",
    role: "Full Stack Developer",
    bio: "React UI, FastAPI endpoints, real-time streaming, source citations",
    github: "#",
    linkedin: "#",
  },
  {
    name: "Rutvik Katkoriya",
    initials: "RK",
    role: "Data Engineer",
    bio: "ETL pipeline, Notion ingestion, retrieval system, metadata engineering",
    github: "#",
    linkedin: "#",
  },
  {
    name: "Nila Ko",
    initials: "NK",
    role: "AI Engineer",
    bio: "RAG pipeline, prompt engineering, embeddings, evaluation",
    github: "#",
    linkedin: "#",
  },
];

const techGrid = [
  {
    label: "Frontend",
    color: "text-purple-500",
    items: ["React + TypeScript", "Vite", "Tailwind CSS + shadcn/ui", "Motion"],
  },
  {
    label: "Backend",
    color: "text-purple-500",
    items: ["FastAPI (Python)", "Google OAuth 2.0", "SSE Streaming", "LangChain"],
  },
  {
    label: "AI & Data",
    color: "text-purple-500",
    items: ["Gemini 2.5 Flash", "ChromaDB + BM25", "Voyage AI Re-ranker", "PostgreSQL"],
  },
  { label: "Cloudflare", color: "text-amber-500", items: ["Pages (Frontend CDN)"] },
  { label: "AWS", color: "text-blue-500", items: ["EKS + Secrets Manager"] },
  {
    label: "IBM LinuxONE",
    color: "text-emerald-500",
    items: ["ChromaDB + PostgreSQL"],
  },
];

export function AboutPage() {
  return (
    <>
      <section className="relative px-6 pb-12 pt-20 text-center md:pt-28">
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[300px] w-[500px] -translate-x-1/2 -translate-y-1/2 bg-[radial-gradient(ellipse,rgba(124,58,237,0.05)_0%,transparent_70%)]" />
        <div className="relative z-10 mx-auto max-w-xl">
          <p className="mb-4 text-[10px] uppercase tracking-[3px] text-purple-500">
            About WorkMate
          </p>
          <h1 className="text-2xl font-bold leading-snug text-white md:text-3xl">
            We believe your team&apos;s knowledge shouldn&apos;t be buried in
            documents.
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-white/40">
            WorkMate was born from a simple frustration: teams store critical
            knowledge in Notion, but finding specific answers means digging
            through pages manually. We built an AI assistant that retrieves,
            reasons over, and cites your workspace documents — so your team can
            focus on decisions, not searching.
          </p>
        </div>
      </section>

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      <section className="px-6 py-16">
        <motion.div className="mb-10 text-center" {...fadeInUp}>
          <p className="mb-3 text-[10px] uppercase tracking-[3px] text-purple-500">
            The Team
          </p>
          <h2 className="text-xl font-bold text-white md:text-2xl">
            Built by engineers who care about knowledge access
          </h2>
          <p className="mt-2 text-xs text-white/35">
            San Francisco Bay University — CS Capstone, Spring 2026
          </p>
        </motion.div>
        <div className="mx-auto grid max-w-4xl gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {team.map((m, i) => (
            <motion.div
              key={m.name}
              className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-6 text-center"
              {...fadeInUp}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div className="mx-auto mb-4 flex h-[72px] w-[72px] items-center justify-center rounded-full border border-purple-600/20 bg-purple-600/10 text-xl text-white/30">
                {m.initials}
              </div>
              <h3 className="text-sm font-semibold text-white">{m.name}</h3>
              <p className="mt-1 text-[11px] text-purple-500">{m.role}</p>
              <p className="mt-2 text-[11px] leading-relaxed text-white/35">
                {m.bio}
              </p>
              <div className="mt-3 flex justify-center gap-3">
                <a
                  href={m.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white/30 transition-colors hover:text-white/60"
                >
                  <Github className="h-3.5 w-3.5" />
                </a>
                <a
                  href={m.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white/30 transition-colors hover:text-white/60"
                >
                  <Linkedin className="h-3.5 w-3.5" />
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      <section className="px-6 py-16">
        <motion.div className="mb-10 text-center" {...fadeInUp}>
          <p className="mb-3 text-[10px] uppercase tracking-[3px] text-purple-500">
            Tech Stack
          </p>
          <h2 className="text-xl font-bold text-white md:text-2xl">
            What powers WorkMate
          </h2>
        </motion.div>
        <div className="mx-auto grid max-w-3xl gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {techGrid.map((g, i) => (
            <motion.div
              key={g.label}
              className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-5"
              {...fadeInUp}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <p className={`mb-2 text-[10px] uppercase tracking-widest ${g.color}`}>
                {g.label}
              </p>
              <div className="text-xs leading-[2] text-white/50">
                {g.items.map((item) => (
                  <div key={item}>{item}</div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </>
  );
}
