import { Link } from "@tanstack/react-router";
import { Github, Mail } from "lucide-react";
import { SOCIAL_LINKS } from "@/config/social.config";

export function Footer() {
  return (
    <footer className="mt-32 border-t border-border bg-surface">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="grid gap-12 md:grid-cols-3">
          <div>
            <Link to="/" className="font-display text-base font-semibold tracking-tight">
              NEXAR
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Quantum Classical Code Router — a research initiative on intelligent hybrid execution.
            </p>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-foreground">Explore</h4>
            <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
              <li><Link to="/domain" className="hover:text-foreground">Domain</Link></li>
              <li><Link to="/milestones" className="hover:text-foreground">Milestones</Link></li>
              <li><Link to="/documents" className="hover:text-foreground">Documents</Link></li>
              <li><Link to="/presentations" className="hover:text-foreground">Presentations</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-foreground">Connect</h4>
            <div className="mt-4 flex gap-2">
              <a href={SOCIAL_LINKS.GITHUB} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="rounded-full border border-border p-2 text-muted-foreground transition-colors hover:border-foreground/40 hover:text-foreground">
                <Github className="h-4 w-4" />
              </a>
              <a href={`mailto:${SOCIAL_LINKS.EMAIL}`} aria-label="Email" className="rounded-full border border-border p-2 text-muted-foreground transition-colors hover:border-foreground/40 hover:text-foreground">
                <Mail className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
        <div className="mt-12 border-t border-border pt-6 text-xs text-muted-foreground">
          © {new Date().getFullYear()} NEXAR Research. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
