import { Link } from "react-router-dom";

const footerLinks = [
  { label: "About", href: "/about" },
  { label: "Pricing", href: "/pricing" },
  { label: "Docs", href: "/docs" },
  { label: "Contact", href: "/contact" },
  { label: "GitHub", href: "https://github.com/RubyRyn/WorkMate" },
];

export function Footer() {
  return (
    <footer className="border-t border-white/[0.06] px-6 py-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 sm:flex-row">
        <p className="text-xs text-white/30">
          &copy; 2026 WorkMate. Built at SFBU.
        </p>
        <div className="flex gap-6">
          {footerLinks.map((link) =>
            link.href.startsWith("http") ? (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-white/30 transition-colors hover:text-white/60"
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.label}
                to={link.href}
                className="text-xs text-white/30 transition-colors hover:text-white/60"
              >
                {link.label}
              </Link>
            )
          )}
        </div>
      </div>
    </footer>
  );
}
