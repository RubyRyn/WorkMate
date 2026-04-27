import { motion } from "motion/react";
import { Link } from "react-router-dom";

const fadeInUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-60px" },
  transition: { duration: 0.5 },
};

export function DemoPage() {
  return (
    <>
      {/* Header */}
      <section className="px-6 pb-8 pt-20 text-center md:pt-28">
        <p className="mb-4 text-[10px] uppercase tracking-[3px] text-purple-500">
          Demo
        </p>
        <h1 className="text-2xl font-bold text-white md:text-3xl">
          See WorkMate in action
        </h1>
        <p className="mt-3 text-sm text-white/40">
          Watch how WorkMate connects to your Notion workspace and answers
          questions with sourced citations.
        </p>
      </section>

      {/* Video */}
      <motion.section className="px-6 pb-16" {...fadeInUp}>
        <div className="mx-auto max-w-4xl overflow-hidden rounded-xl border border-white/[0.08] bg-white/[0.02]">
          <div className="relative w-full" style={{ paddingBottom: "56.25%" }}>
            <iframe
              className="absolute inset-0 h-full w-full"
              src="https://www.youtube.com/embed/gFEkT7CEuBk?modestbranding=1&rel=0"
              title="WorkMate Demo"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        </div>
      </motion.section>

      {/* CTA */}
      <motion.section
        className="relative px-6 pb-16 text-center"
        {...fadeInUp}
      >
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[200px] w-[400px] -translate-x-1/2 -translate-y-1/2 bg-[radial-gradient(ellipse,rgba(124,58,237,0.06)_0%,transparent_70%)]" />
        <div className="relative z-10">
          <h2 className="text-xl font-bold text-white">Ready to try it?</h2>
          <p className="mt-2 text-sm text-white/40">
            Connect your Notion workspace and start getting answers.
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
