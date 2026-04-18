import { Link } from "react-router-dom";
import { FloatingDocs } from "./FloatingDocs";
import { ChatPreview } from "./ChatPreview";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden px-6 pb-16 pt-20 text-center md:pt-28 md:pb-24">
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(ellipse,rgba(124,58,237,0.07)_0%,transparent_70%)]" />

      <FloatingDocs />

      <div className="relative z-10 mx-auto max-w-xl">
        <p className="mb-4 text-[10px] font-medium uppercase tracking-[3px] text-purple-500">
          AI-Powered Knowledge Assistant
        </p>
        <h1 className="text-3xl font-bold leading-tight tracking-tight text-white md:text-5xl">
          Your Notion workspace,
          <br />
          <span className="text-purple-500">answered instantly.</span>
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-white/40 md:text-base">
          Ask questions across all your documents. Get sourced answers in
          real-time.
        </p>

        <ChatPreview />

        <div className="mt-8 flex items-center justify-center gap-3">
          <Link
            to="/login"
            className="rounded-lg bg-purple-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-purple-700"
          >
            Get Started Free
          </Link>
          <a
            href="#how-it-works"
            className="rounded-lg border border-white/10 px-6 py-3 text-sm text-white/50 transition-colors hover:border-white/20 hover:text-white/70"
          >
            See How It Works
          </a>
        </div>
      </div>
    </section>
  );
}
