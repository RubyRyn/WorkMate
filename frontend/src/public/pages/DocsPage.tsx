import { motion } from "motion/react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/app/components/ui/accordion";

const fadeInUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-60px" },
  transition: { duration: 0.5 },
};

const gettingStarted = [
  {
    title: "Sign in with Google",
    desc: 'Click "Get Started" and authenticate with your Google account. No passwords to remember.',
  },
  {
    title: "Connect your Notion workspace",
    desc: "Go to Settings and click \u201CConnect Notion.\u201D You\u2019ll authorize WorkMate to read your workspace pages and databases. Documents are automatically ingested and indexed.",
  },
  {
    title: "Start asking questions",
    desc: "Type a question in the chat. WorkMate searches your connected documents using hybrid search, then streams an answer with source citations and confidence scores.",
  },
  {
    title: "Upload additional files (optional)",
    desc: "Drag and drop PDFs, text files, or markdown into the chat. They\u2019ll be chunked, embedded, and searchable alongside your Notion content.",
  },
];

const faqItems = [
  {
    q: "What data does WorkMate access from my Notion?",
    a: "WorkMate reads pages, databases, and blocks from workspaces you explicitly authorize via OAuth. We never access workspaces you haven\u2019t connected. All tokens are encrypted at rest using Fernet encryption.",
  },
  {
    q: "Can other users see my documents?",
    a: "No. WorkMate is multi-tenant with workspace isolation. Your RAG queries are scoped to your connected workspace IDs only. Other users cannot access or search your documents.",
  },
  {
    q: "What file types can I upload?",
    a: "PDF, plain text (.txt), and Markdown (.md) files. Uploaded files are chunked using LangChain and embedded alongside your Notion content for unified search.",
  },
  {
    q: "How accurate are the answers?",
    a: "WorkMate uses a hybrid search pipeline (BM25 + vector similarity) with Voyage AI re-ranking to find the most relevant chunks. Every answer includes confidence scores and source citations so you can verify. The LLM runs at temperature 0.0 for deterministic, consistent outputs.",
  },
  {
    q: "How do I sync new Notion changes?",
    a: 'Go to Settings \u2192 Connected Workspaces and click the "Sync" button next to your workspace. WorkMate will re-ingest all pages and update the vector database.',
  },
  {
    q: "Is my data secure?",
    a: "Yes. Notion OAuth tokens are encrypted with Fernet. API keys are stored in AWS Secrets Manager. All traffic uses HTTPS. The database runs on IBM LinuxONE with workspace-scoped access controls.",
  },
];

export function DocsPage() {
  return (
    <>
      <section className="px-6 pb-8 pt-20 text-center md:pt-28">
        <p className="mb-4 text-[10px] uppercase tracking-[3px] text-purple-500">
          Documentation
        </p>
        <h1 className="text-2xl font-bold text-white md:text-3xl">
          Get up and running
        </h1>
        <p className="mt-3 text-sm text-white/40">
          Everything you need to connect your workspace and start asking
          questions.
        </p>
      </section>

      <section className="px-6 pb-12">
        <div className="mx-auto max-w-2xl">
          <p className="mb-6 text-[10px] uppercase tracking-widest text-purple-500">
            Getting Started
          </p>
          <div className="space-y-6">
            {gettingStarted.map((step, i) => (
              <motion.div
                key={step.title}
                className="flex gap-4"
                {...fadeInUp}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-purple-600/25 bg-purple-600/10 text-sm font-semibold text-purple-500">
                  {i + 1}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">
                    {step.title}
                  </h3>
                  <p className="mt-1 text-xs leading-relaxed text-white/40">
                    {step.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <div className="mx-6 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      <section className="px-6 py-12">
        <div className="mx-auto max-w-2xl">
          <p className="mb-6 text-[10px] uppercase tracking-widest text-purple-500">
            Frequently Asked Questions
          </p>
          <Accordion type="single" collapsible className="space-y-2">
            {faqItems.map((item, i) => (
              <AccordionItem
                key={i}
                value={`faq-${i}`}
                className="rounded-lg border border-white/[0.08] px-5 data-[state=open]:border-white/[0.12]"
              >
                <AccordionTrigger className="py-4 text-left text-sm font-medium text-white/70 hover:text-white hover:no-underline">
                  {item.q}
                </AccordionTrigger>
                <AccordionContent className="pb-4 text-xs leading-relaxed text-white/40">
                  {item.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>
    </>
  );
}
