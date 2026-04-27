import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { useAuth } from "@/app/contexts/AuthContext";
import { Sheet, SheetContent, SheetTrigger } from "@/app/components/ui/sheet";

const navLinks = [
  { label: "About", href: "/about" },
  { label: "Pricing", href: "/pricing" },
  { label: "Docs", href: "/docs" },
  { label: "Demo", href: "/demo" },
  { label: "Contact", href: "/contact" },
];

export function Navbar() {
  const { user } = useAuth();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#0a0a14]/80 backdrop-blur-lg border-b border-white/[0.06]"
          : "bg-transparent"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <img src="/workmate-logo.png" alt="WorkMate" className="h-8" />
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={`text-sm transition-colors ${
                location.pathname === link.href
                  ? "text-purple-500"
                  : "text-white/50 hover:text-white/80"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {user ? (
            <Link
              to="/app"
              className="rounded-lg bg-purple-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700"
            >
              Go to App
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm text-white/50 transition-colors hover:text-white/80"
              >
                Sign In
              </Link>
              <Link
                to="/login"
                className="rounded-lg bg-purple-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700"
              >
                Get Started
              </Link>
            </>
          )}
        </div>

        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild className="md:hidden">
            <button className="text-white/60">
              <Menu className="h-6 w-6" />
            </button>
          </SheetTrigger>
          <SheetContent side="right" className="bg-[#0a0a14] border-white/[0.06] w-64">
            <div className="flex flex-col gap-4 pt-8">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={`text-sm ${
                    location.pathname === link.href
                      ? "text-purple-500"
                      : "text-white/50"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              <div className="mt-4 border-t border-white/[0.06] pt-4">
                {user ? (
                  <Link
                    to="/app"
                    onClick={() => setMobileOpen(false)}
                    className="block rounded-lg bg-purple-600 px-4 py-2 text-center text-sm font-medium text-white"
                  >
                    Go to App
                  </Link>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setMobileOpen(false)}
                      className="block text-sm text-white/50 mb-3"
                    >
                      Sign In
                    </Link>
                    <Link
                      to="/login"
                      onClick={() => setMobileOpen(false)}
                      className="block rounded-lg bg-purple-600 px-4 py-2 text-center text-sm font-medium text-white"
                    >
                      Get Started
                    </Link>
                  </>
                )}
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </nav>
  );
}
