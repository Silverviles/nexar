import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Menu, X, Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { to: "/", label: "Home" },
  { to: "/domain", label: "Domain" },
  { to: "/milestones", label: "Milestones" },
  { to: "/documents", label: "Documents" },
  { to: "/presentations", label: "Presentations" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
] as const;

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const shouldBeDark = savedTheme ? savedTheme === "dark" : true; // Defaulting to the new Premium Dark Theme
    setIsDark(shouldBeDark);
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-6 z-50 flex justify-center px-4 transition-all duration-500",
      )}
    >
      <nav
        className={cn(
          "flex items-center justify-between gap-6 px-6 py-2.5 rounded-full transition-all duration-500 border",
          scrolled 
            ? "bg-background/80 backdrop-blur-xl border-border dark:border-white/10 shadow-md dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]" 
            : "bg-transparent border-transparent"
        )}
      >
        <Link to="/" className="flex items-center gap-2 pr-4 border-r border-border dark:border-white/10">
          <span className="font-display text-[15px] font-semibold tracking-wide text-foreground">
            NEXAR
          </span>
        </Link>

        <ul className="hidden items-center gap-1.5 lg:flex">
          {links.map((l) => (
            <li key={l.to}>
              <Link
                to={l.to}
                className="rounded-full px-4 py-2 text-[13px] font-medium text-muted-foreground transition-all duration-300 hover:text-foreground"
                activeProps={{ className: "bg-black/5 dark:bg-white/5 text-foreground shadow-sm" }}
                activeOptions={{ exact: l.to === "/" }}
              >
                {l.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2 lg:ml-2">
          <button
            onClick={() => setIsDark(!isDark)}
            className="rounded-full p-2 text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
            aria-label="Toggle theme"
          >
            {isDark ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
          </button>
          
          <button
            className="rounded-full p-2 text-foreground lg:hidden ml-1 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      {open && (
        <div className="border-t border-border bg-background lg:hidden">
          <ul className="mx-auto max-w-7xl px-4 py-2 sm:px-6">
            {links.map((l) => (
              <li key={l.to}>
                <Link
                  to={l.to}
                  className="block rounded-md px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
                  activeProps={{ className: "!text-foreground bg-muted" }}
                  activeOptions={{ exact: l.to === "/" }}
                  onClick={() => setOpen(false)}
                >
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </header>
  );
}
