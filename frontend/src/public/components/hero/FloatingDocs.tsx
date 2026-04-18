import { motion } from "motion/react";

const docs = [
  { label: "Q3 Strategy", emoji: "\u{1F4C4}", x: "5%", y: "8%", rotate: -2 },
  { label: "Sprint Board", emoji: "\u{1F4CA}", x: "75%", y: "12%", rotate: 1.5 },
  { label: "Meeting Notes", emoji: "\u{1F4DD}", x: "8%", y: "70%", rotate: 1 },
  { label: "Roadmap", emoji: "\u{1F5C2}\uFE0F", x: "72%", y: "75%", rotate: -1 },
];

export function FloatingDocs() {
  return (
    <>
      {docs.map((doc, i) => (
        <motion.div
          key={doc.label}
          className="absolute hidden rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-xs text-white/25 backdrop-blur-sm md:block"
          style={{ left: doc.x, top: doc.y, rotate: doc.rotate }}
          animate={{ y: [0, -8, 0] }}
          transition={{
            duration: 4 + i * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <span className="opacity-50">{doc.emoji}</span> {doc.label}
        </motion.div>
      ))}
    </>
  );
}
