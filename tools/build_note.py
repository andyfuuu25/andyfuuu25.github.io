"""Render the Summit Therapeutics markdown note into research/summit-therapeutics.html.

Run from anywhere:  python tools/build_note.py
Re-run whenever the source note changes.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parent.parent
SOURCE = Path(r"C:\Users\andyf\OneDrive\Desktop\SMMT Report Files\SMMT_Initiation_Note.md")
OUTPUT = REPO / "research" / "summit-therapeutics.html"

# Source filename -> the optimized copy that lives in the repo.
IMAGE_MAP = {
    "exhibit1_os_hazard_ratio.png": "../assets/img/smmt-exhibit1.jpg",
    "exhibit2_os_hazard_ratio.png": "../assets/img/smmt-exhibit1.jpg",
    "exhibit2_value_bridge.png": "../assets/img/smmt-exhibit2.jpg",
}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Andy Fu</title>
<meta name="description" content="{description}">
<meta name="author" content="Chi Leong Andy Fu">
<meta name="robots" content="index, follow">

<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="https://andyfuuu25.github.io/research/summit-therapeutics.html">

<link rel="canonical" href="https://andyfuuu25.github.io/research/summit-therapeutics.html">
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22 font-family=%22Georgia,serif%22>AF</text></svg>">
<script>
  (function () {{
    try {{
      var saved = localStorage.getItem('theme');
      if (saved === 'light' || saved === 'dark') {{
        document.documentElement.setAttribute('data-theme', saved);
      }}
    }} catch (e) {{}}
  }})();
</script>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<header class="nav" id="nav">
  <div class="wrap nav__inner">
    <a class="nav__brand" href="../index.html">Andy&nbsp;Fu</a>
    <nav aria-label="Primary">
      <ul class="nav__links">
        <li><a href="../index.html#work">Work</a></li>
        <li class="is-optional"><a href="../index.html#experience">Experience</a></li>
        <li><a href="../index.html#contact">Contact</a></li>
        <li>
          <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle colour theme">
            <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
          </button>
        </li>
      </ul>
    </nav>
  </div>
</header>

<main id="main" class="note">
  <div class="wrap">
    <a class="note__back" href="../index.html#work">Back to work</a>
    <article class="prose">
{body}
    </article>
  </div>
</main>

<footer class="footer wrap">
  <span>© <span id="year">2026</span> Chi Leong Andy Fu</span>
  <span><a href="../index.html">andyfuuu25.github.io</a></span>
</footer>

<script src="../assets/js/main.js"></script>
</body>
</html>
"""


def wrap_tables(text: str) -> str:
    """Give every table its own horizontal scroll container."""
    return text.replace("<table>", '<div class="table-scroll"><table>').replace(
        "</table>", "</table></div>"
    )


def rewrite_images(text: str) -> str:
    for original, replacement in IMAGE_MAP.items():
        text = text.replace(f'src="{original}"', f'src="{replacement}"')
    # Lazy-load exhibits and drop the bare <p> wrapper markdown leaves around them.
    text = text.replace("<img ", '<img loading="lazy" ')
    text = re.sub(r"<p>(<img [^>]*>)</p>", r"<figure>\1</figure>", text)
    return text


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Source note not found: {SOURCE}")

    raw = SOURCE.read_text(encoding="utf-8")
    raw = raw.replace("[Your name]", "Chi Leong Andy Fu")

    body = markdown.markdown(
        raw,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists"],
        output_format="html5",
    )
    body = wrap_tables(body)
    body = rewrite_images(body)
    body = "\n".join("      " + line for line in body.splitlines())

    title = "Summit Therapeutics (NASDAQ: SMMT) — Initiation of Coverage"
    description = (
        "An initiation note on Summit Therapeutics: disclosed Phase III programmes valued "
        "bottom-up by rNPV at $1.75 per share, and an honest account of the gap to consensus."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        PAGE.format(
            title=html.escape(title, quote=True),
            description=html.escape(description, quote=True),
            body=body,
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(REPO)} ({OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
