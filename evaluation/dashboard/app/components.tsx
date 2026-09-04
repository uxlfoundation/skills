import type { ReactNode } from "react";

type PageChromeProps = {
  prefix?: string;
  active?: "overview" | "skills" | "evaluations" | "platforms" | "methodology";
};

const navItems = [
  ["overview", "Overview", ""],
  ["skills", "Skills", "skills/"],
  ["evaluations", "Evaluations", "evaluations/"],
  ["platforms", "Platforms", "platforms/"],
  ["methodology", "Methodology", "methodology/"],
] as const;

export function SiteHeader({ prefix = "", active = "overview" }: PageChromeProps) {
  return (
    <nav className="site-nav" aria-label="Primary navigation">
      <a className="brand" href={prefix || "#top"} aria-label="UXL Skills Evaluator home">
        {/* The official SVG is tiny and must keep its relative GitHub Pages path. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={`${prefix}uxl-foundation-icon-color.svg`} alt="" aria-hidden="true" />
        <span className="brand-name">UXL Skills Evaluator</span>
      </a>
      <div className="nav-links">
        {navItems.map(([key, label, path]) => (
          <a
            href={`${prefix}${path}`}
            className={active === key ? "active" : undefined}
            aria-current={active === key ? "page" : undefined}
            key={key}
          >
            {label}
          </a>
        ))}
        <a className="source-link" href="https://github.com/uxlfoundation/skills">Source ↗</a>
      </div>
      <details className="mobile-menu">
        <summary>Menu</summary>
        <div>
          {navItems.map(([key, label, path]) => (
            <a href={`${prefix}${path}`} aria-current={active === key ? "page" : undefined} key={key}>{label}</a>
          ))}
          <a href="https://github.com/uxlfoundation/skills">Source ↗</a>
        </div>
      </details>
    </nav>
  );
}

export function SiteFooter({ prefix = "" }: { prefix?: string }) {
  return (
    <footer>
      <div className="brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={`${prefix}uxl-foundation-icon-color.svg`} alt="" aria-hidden="true" />
        <span className="brand-name">UXL Skills Evaluator</span>
      </div>
      <p>
        Public portfolio scorecard. <a href={`${prefix}decks/uxl-skills-maintainer-overview.pdf`}>Maintainer overview</a>
        {" · "}<a href={`${prefix}decks/uxl-specialized-target-onboarding.pdf`}>Target onboarding</a>
      </p>
      <a href="#top">Back to top ↑</a>
    </footer>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return <p className="eyebrow"><span aria-hidden="true" />{children}</p>;
}

export function StatusPill({ children, tone = "neutral" }: { children: ReactNode; tone?: "good" | "watch" | "neutral" | "planned" }) {
  return <span className={`status-pill ${tone}`}>{children}</span>;
}

export function PageIntro({ label, title, children }: { label: string; title: ReactNode; children: ReactNode }) {
  return (
    <header className="page-intro" id="top">
      <Eyebrow>{label}</Eyebrow>
      <h1>{title}</h1>
      <p>{children}</p>
    </header>
  );
}
