import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { Check } from "lucide-react";

const fadeInUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-60px" },
  transition: { duration: 0.5 },
};

interface Tier {
  name: string;
  price: string;
  unit: string;
  description: string;
  features: string[];
  cta: string;
  highlighted: boolean;
}

const tiers: Tier[] = [
  {
    name: "Free",
    price: "$0",
    unit: "/month",
    description: "For individuals exploring WorkMate",
    features: [
      "1 Notion workspace",
      "50 questions / month",
      "5 file uploads",
      "Source citations",
      "Real-time streaming",
      "Community support",
    ],
    cta: "Get Started Free",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$12",
    unit: "/user/month",
    description: "For teams who need full access",
    features: [
      "Unlimited workspaces",
      "Unlimited questions",
      "Unlimited file uploads",
      "Priority support",
      "Advanced analytics",
      "Conversation export",
    ],
    cta: "Get Started",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    unit: "",
    description: "For organizations with advanced needs",
    features: [
      "Everything in Pro",
      "SSO / SAML",
      "Custom integrations",
      "Dedicated support",
      "SLA guarantee",
      "On-premise deployment",
    ],
    cta: "Contact Us",
    highlighted: false,
  },
];

export function PricingPage() {
  return (
    <>
      <section className="relative px-6 pb-8 pt-20 text-center md:pt-28">
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[300px] w-[500px] -translate-x-1/2 -translate-y-1/2 bg-[radial-gradient(ellipse,rgba(124,58,237,0.05)_0%,transparent_70%)]" />
        <div className="relative z-10">
          <p className="mb-4 text-[10px] uppercase tracking-[3px] text-purple-500">
            Pricing
          </p>
          <h1 className="text-2xl font-bold text-white md:text-3xl">
            Simple, transparent pricing
          </h1>
          <p className="mt-3 text-sm text-white/40">
            Start free. Upgrade as your team grows.
          </p>
        </div>
      </section>

      <section className="px-6 pb-16">
        <div className="mx-auto grid max-w-4xl items-stretch gap-4 lg:grid-cols-3">
          {tiers.map((tier, i) => (
            <motion.div
              key={tier.name}
              className={`relative flex flex-col rounded-xl border p-8 ${
                tier.highlighted
                  ? "border-purple-600/30 bg-purple-600/[0.05]"
                  : "border-white/[0.06] bg-white/[0.02]"
              }`}
              {...fadeInUp}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              {tier.highlighted && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-purple-600 px-4 py-1 text-[10px] font-semibold uppercase tracking-widest text-white">
                  Popular
                </span>
              )}

              <div>
                <p className="text-xs uppercase tracking-widest text-white/40">
                  {tier.name}
                </p>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-white">
                    {tier.price}
                  </span>
                  {tier.unit && (
                    <span className="text-sm text-white/30">{tier.unit}</span>
                  )}
                </div>
                <p className="mt-2 text-xs text-white/35">{tier.description}</p>
              </div>

              <div
                className={`mt-6 flex-1 border-t pt-6 ${
                  tier.highlighted
                    ? "border-purple-600/15"
                    : "border-white/[0.06]"
                }`}
              >
                <ul className="space-y-3">
                  {tier.features.map((f) => (
                    <li
                      key={f}
                      className="flex items-center gap-2 text-xs text-white/50"
                    >
                      <Check className="h-3.5 w-3.5 shrink-0 text-emerald-500" />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-8">
                {tier.name === "Enterprise" ? (
                  <Link
                    to="/contact"
                    className="block rounded-lg border border-white/[0.08] bg-white/[0.04] py-2.5 text-center text-sm text-white/60 transition-colors hover:border-white/[0.15]"
                  >
                    {tier.cta}
                  </Link>
                ) : (
                  <Link
                    to="/login"
                    className={`block rounded-lg py-2.5 text-center text-sm font-medium transition-colors ${
                      tier.highlighted
                        ? "bg-purple-600 text-white hover:bg-purple-700"
                        : "border border-white/[0.08] bg-white/[0.04] text-white/60 hover:border-white/[0.15]"
                    }`}
                  >
                    {tier.cta}
                  </Link>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        <p className="mt-10 text-center text-sm text-white/40">
          Have questions? Check our{" "}
          <Link to="/docs" className="text-purple-500 underline">
            Docs &amp; FAQ
          </Link>{" "}
          page.
        </p>
      </section>
    </>
  );
}
