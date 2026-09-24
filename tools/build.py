"""Build the portfolio site from content/site.toml.

    python tools/build.py

Generates index.html and every page listed under [[notes]]. Nothing else in
the repo is written to, and the generated files are safe to commit.

Only dependency: `markdown`, and only if there are research notes to render.
Everything else is standard library.
"""

from __future__ import annotations

import html
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
SITE_TOML = CONTENT / "site.toml"
NOTES_DIR = CONTENT / "notes"


# ---------------------------------------------------------------- helpers ---

class BuildError(Exception):
    """A problem in the content file, reported without a traceback."""


def e(text: str) -> str:
    """Escape text for HTML."""
    return html.escape(str(text), quote=True)


_INLINE = (
    # (pattern, replacement) applied AFTER escaping, so the HTML we emit here
    # is the only HTML that survives.
    (re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+|[^)\s]+)\)"),
     r'<a href="\2">\1</a>'),
    (re.compile(r"\*\*(.+?)\*\*", re.S), r"<strong>\1</strong>"),
    (re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", re.S), r"<em>\1</em>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
)


def md(text: str | None) -> str:
    """Render the small inline-markdown subset allowed in site.toml."""
    if not text:
        return ""
    out = e(" ".join(str(text).split()))
    for pattern, repl in _INLINE:
        out = pattern.sub(repl, out)
    return out


def paras(text: str | None) -> str:
    """Render blank-line-separated text as <p> blocks."""
    if not text:
        return ""
    blocks = [b for b in re.split(r"\n\s*\n", str(text).strip()) if b.strip()]
    return "\n".join(f"<p>{md(b)}</p>" for b in blocks)


def indent(markup: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line
                     for line in markup.splitlines())


def require(mapping: dict, key: str, where: str):
    if key not in mapping:
        raise BuildError(f"[{where}] is missing the required key '{key}' in content/site.toml")
    return mapping[key]


# ------------------------------------------------------------------ icons ---

ICONS = {
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM2.4 21h5.16V9.5H2.4V21zM9.5 9.5h4.95v1.57h.07c.69-1.24 2.38-2.55 4.9-2.55 5.24 0 6.2 3.24 6.2 7.45V21h-5.15v-4.9c0-1.17-.02-2.68-1.7-2.68-1.7 0-1.96 1.28-1.96 2.6V21H9.5V9.5z"/></svg>',
    "github": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.86 10.92c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.54-3.88-1.54-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.03 1.77 2.71 1.26 3.37.96.1-.75.4-1.26.73-1.55-2.56-.29-5.25-1.28-5.25-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.12 3.05.74.81 1.18 1.84 1.18 3.1 0 4.43-2.69 5.4-5.26 5.69.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5z"/></svg>',
    "file": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 18v-6M9 15l3 3 3-3"/></svg>',
}

THEME_TOGGLE = '''<button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle colour theme">
  <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
</button>'''

THEME_SCRIPT = """<script>
  // Applied before paint so the correct theme is up on the first frame.
  (function () {
    try {
      var saved = localStorage.getItem('theme');
      if (saved === 'light' || saved === 'dark') {
        document.documentElement.setAttribute('data-theme', saved);
      }
    } catch (e) {}
  })();
</script>"""

FAVICON = ('<link rel="icon" href="data:image/svg+xml,'
           '<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22>'
           '<text y=%22.9em%22 font-size=%2290%22 font-family=%22Georgia,serif%22>AF</text></svg>">')


# ------------------------------------------------------------ image sizes ---

def image_size(path: Path) -> tuple[int, int] | None:
    """Read pixel dimensions straight from a PNG or JPEG header.

    Standard library only, so the CI build needs no image package.
    Returns None if the file is missing or not a format we can read.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None

    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return (int.from_bytes(data[16:20], "big"),
                int.from_bytes(data[20:24], "big"))

    if data[:2] == b"\xff\xd8":                        # JPEG
        i, n = 2, len(data)
        while i + 9 < n:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker == 0xFF:                         # fill byte
                i += 1
                continue
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2                                 # standalone marker
                continue
            length = int.from_bytes(data[i + 2:i + 4], "big")
            if length < 2:
                break
            # SOFn frame headers carry the dimensions; DHT/JPG/DAC do not.
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return (int.from_bytes(data[i + 7:i + 9], "big"),
                        int.from_bytes(data[i + 5:i + 7], "big"))
            i += 2 + length
    return None


def size_attrs(rel_src: str, base: Path) -> str:
    """width/height attributes so the browser reserves the right box before the
    image arrives, which stops the page jumping as exhibits load in."""
    dims = image_size((base / rel_src).resolve())
    return f' width="{dims[0]}" height="{dims[1]}"' if dims else ""


# ------------------------------------------------------------- components ---

def render_tags(items) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{md(t)}</li>" for t in items)
    return f'<ul class="tags">{lis}</ul>'


def render_points(items, css_class: str) -> str:
    if not items:
        return ""
    lis = "\n".join(f"  <li>{md(p)}</li>" for p in items)
    return f'<ul class="{css_class}">\n{lis}\n</ul>'


def render_links(links) -> str:
    if not links:
        return ""
    anchors = "\n".join(
        f'  <a href="{e(l["href"])}"{external(l["href"])}>{md(l["label"])}</a>'
        for l in links
    )
    return f'<div class="card__links">\n{anchors}\n</div>'


def external(href: str) -> str:
    """Open off-site links in a new tab; keep in-site links in place."""
    return ' target="_blank" rel="noopener"' if href.startswith("http") else ""


def render_figures(figures) -> str:
    if not figures:
        return ""
    items = "\n".join(
        f'''  <figure class="card__figure">
    <img src="{e(f["src"])}"{size_attrs(f["src"], REPO)} loading="lazy" alt="{e(f.get("alt", ""))}">
    <figcaption>{md(f.get("caption", ""))}</figcaption>
  </figure>'''
        for f in figures
    )
    css = "figure-pair" if len(figures) > 1 else "figure-single"
    return f'<div class="{css}">\n{items}\n</div>'


def render_project(p: dict, i: int) -> str:
    title = require(p, "title", f"work.projects #{i}")
    url = p.get("url")
    heading = (f'<a href="{e(url)}"{external(url)}>{md(title)}</a>'
               if url else md(title))
    kind = f'<span class="card__kind">{md(p["kind"])}</span>' if p.get("kind") else ""

    parts = [
        '<div class="card__head">',
        f'  <h3 class="card__title">{heading}</h3>',
        f"  {kind}" if kind else "",
        "</div>",
    ]
    if p.get("summary"):
        parts.append(f'<div class="card__body">{paras(p["summary"])}</div>')
    for block in (render_points(p.get("points"), "card__points"),
                  render_figures(p.get("figures")),
                  render_tags(p.get("tags")),
                  render_links(p.get("links"))):
        if block:
            parts.append(block)

    body = "\n".join(x for x in parts if x)
    return f'<article class="card reveal">\n{indent(body, 2)}\n</article>'


def render_timeline(items, where: str) -> str:
    rows = []
    for i, it in enumerate(items, 1):
        role = md(require(it, "role", f"{where} #{i}"))
        org = f' <span class="timeline__org">· {md(it["org"])}</span>' if it.get("org") else ""
        dt = f'<span class="timeline__date">{md(it["date"])}</span>' if it.get("date") else ""
        body = "\n".join(x for x in [
            '<div class="timeline__head">',
            f'  <h3 class="timeline__role">{role}{org}</h3>',
            f"  {dt}" if dt else "",
            "</div>",
            render_points(it.get("points"), "timeline__points"),
        ] if x)
        rows.append(f'<li class="timeline__item reveal">\n{indent(body, 2)}\n</li>')
    return '<ol class="timeline">\n' + indent("\n".join(rows), 2) + "\n</ol>"


def render_section_head(cfg: dict) -> str:
    bits = ['<div class="section__head reveal">']
    if cfg.get("label"):
        bits.append(f'  <span class="section__label">{md(cfg["label"])}</span>')
    if cfg.get("title"):
        bits.append(f'  <h2 class="section__title">{md(cfg["title"])}</h2>')
    if cfg.get("intro"):
        bits.append(f'  <p class="section__intro">{md(cfg["intro"])}</p>')
    bits.append("</div>")
    return "\n".join(bits)


def render_actions(site: dict, prefix: str = "") -> str:
    buttons = [
        ("btn btn--primary", f'mailto:{site["email"]}', ICONS["mail"], "Email me", ""),
        ("btn", site["linkedin"], ICONS["linkedin"], "LinkedIn", ' target="_blank" rel="noopener"'),
        ("btn", site["github"], ICONS["github"], "GitHub", ' target="_blank" rel="noopener"'),
        ("btn", prefix + site["cv"], ICONS["file"], "CV", ' target="_blank" rel="noopener"'),
    ]
    out = "\n".join(
        f'  <a class="{cls}" href="{e(href)}"{attrs}>\n    {icon}\n    {label}\n  </a>'
        for cls, href, icon, label, attrs in buttons
    )
    return f'<div class="actions">\n{out}\n</div>'


# ------------------------------------------------------------- index page ---

def build_index(cfg: dict) -> str:
    site = cfg["site"]
    hero = cfg.get("hero", {})

    sections = []

    # Selected work
    work = cfg.get("work")
    if work and work.get("projects"):
        cards = "\n\n".join(render_project(p, i)
                            for i, p in enumerate(work["projects"], 1))
        sections.append(f'''<section class="section" id="work">
  <div class="wrap">
{indent(render_section_head(work), 4)}
    <div class="projects">

{indent(cards, 6)}

    </div>
  </div>
</section>''')

    # Timeline sections
    for key, anchor in (("experience", "experience"), ("competitions", "competitions")):
        block = cfg.get(key)
        if block and block.get("items"):
            sections.append(f'''<section class="section" id="{anchor}">
  <div class="wrap">
{indent(render_section_head(block), 4)}
{indent(render_timeline(block["items"], key), 4)}
  </div>
</section>''')

    # Skills
    skills = cfg.get("skills")
    if skills and skills.get("groups"):
        groups = "\n".join(
            f'''<div class="skill-group reveal">
  <h3>{md(g["name"])}</h3>
  {render_tags(g.get("items"))}
</div>''' for g in skills["groups"])
        sections.append(f'''<section class="section" id="skills">
  <div class="wrap">
{indent(render_section_head(skills), 4)}
    <div class="skills">
{indent(groups, 6)}
    </div>
  </div>
</section>''')

    # Education
    edu = cfg.get("education")
    if edu and edu.get("items"):
        items = "\n".join(
            f'''<li class="edu__item reveal">
  <div>
    <h3 class="edu__school">{md(it["school"])}
      <span class="edu__degree">{md(it.get("detail", ""))}</span>
    </h3>
  </div>
  <span class="edu__date">{md(it.get("date", ""))}</span>
</li>''' for it in edu["items"])
        sections.append(f'''<section class="section" id="education">
  <div class="wrap">
{indent(render_section_head(edu), 4)}
    <ul class="edu">
{indent(items, 6)}
    </ul>
  </div>
</section>''')

    # Contact
    contact = cfg.get("contact", {})
    contact_actions = "\n".join([
        '<div class="actions">',
        f'  <a class="btn btn--primary" href="mailto:{e(site["email"])}">{e(site["email"])}</a>',
        f'  <a class="btn" href="{e(site["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>',
        f'  <a class="btn" href="{e(site["github"])}" target="_blank" rel="noopener">GitHub</a>',
        f'  <a class="btn" href="{e(site["cv"])}" target="_blank" rel="noopener">Download CV</a>',
        "</div>",
    ])
    sections.append(f'''<section class="contact" id="contact">
  <div class="wrap">
    <span class="section__label">{md(contact.get("label", "Contact"))}</span>
    <h2 class="section__title">{md(contact.get("title", "Get in touch"))}</h2>
    {paras(contact.get("body"))}
{indent(contact_actions, 4)}
  </div>
</section>''')

    body = "\n\n".join(sections)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(site["page_title"])}</title>
<meta name="description" content="{e(site["description"])}">
<meta name="author" content="{e(site["name"])}">

<meta property="og:type" content="website">
<meta property="og:title" content="{e(site["page_title"])}">
<meta property="og:description" content="{e(site["description"])}">
<meta property="og:url" content="{e(site["url"])}">
<meta property="og:image" content="{e(site["url"].rstrip("/") + "/" + site["portrait"])}">
<meta name="twitter:card" content="summary">

<link rel="canonical" href="{e(site["url"])}">
<link rel="stylesheet" href="assets/css/style.css">
{FAVICON}
{THEME_SCRIPT}
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<header class="nav" id="nav">
  <div class="wrap nav__inner">
    <a class="nav__brand" href="#top">{md(site["short_name"]).replace(" ", "&nbsp;")}</a>
    <nav aria-label="Primary">
      <ul class="nav__links">
        <li><a href="#work">Work</a></li>
        <li class="is-optional"><a href="#experience">Experience</a></li>
        <li class="is-optional"><a href="#skills">Skills</a></li>
        <li><a href="#contact">Contact</a></li>
        <li>
{indent(THEME_TOGGLE, 10)}
        </li>
      </ul>
    </nav>
  </div>
</header>

<main id="main">

  <section class="hero" id="top">
    <div class="wrap hero__grid">
      <div>
        <span class="hero__eyebrow">{md(site.get("location", ""))}</span>
        <h1 class="hero__name">{md(site["name"])}</h1>
        <p class="hero__tagline">{md(hero.get("tagline", ""))}</p>
        <div class="hero__bio">{paras(hero.get("bio"))}</div>
{indent(render_actions(site), 8)}
      </div>
      <img class="hero__portrait" src="{e(site["portrait"])}" width="800" height="800"
           alt="Portrait of {e(site["name"])}">
    </div>
  </section>

{indent(body, 2)}

</main>

<footer class="footer wrap">
  <span>© <span id="year">{date.today().year}</span> {md(site["name"])}</span>
  <span>Built by hand. Hosted on GitHub Pages.</span>
</footer>

<script src="assets/js/main.js"></script>
</body>
</html>
'''


# -------------------------------------------------------------- note pages ---

def build_note(cfg: dict, note: dict, i: int) -> tuple[Path, str]:
    try:
        import markdown as markdown_lib
    except ModuleNotFoundError:
        raise BuildError(
            "Rendering research notes needs the 'markdown' package.\n"
            "  Install it with:  python -m pip install markdown\n"
            "  (build.bat does this for you.)"
        )

    site = cfg["site"]
    source = NOTES_DIR / require(note, "source", f"notes #{i}")
    if not source.exists():
        raise BuildError(f"[[notes]] #{i} points at a file that does not exist: {source}")

    out_rel = require(note, "output", f"notes #{i}")
    depth = len(Path(out_rel).parent.parts)        # how far up to reach the repo root
    up = "../" * depth

    body = markdown_lib.markdown(
        source.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "attr_list", "sane_lists"],
        output_format="html5",
    )

    # Point image tags at the web copies named in [notes.images].
    out_dir = (REPO / out_rel).parent
    for original, replacement in (note.get("images") or {}).items():
        body = body.replace(
            f'src="{original}"',
            f'src="{replacement}"{size_attrs(replacement, out_dir)}',
        )
    body = body.replace("<img ", '<img loading="lazy" ')
    body = re.sub(r"<p>(<img [^>]*>)</p>", r"<figure>\1</figure>", body)
    # Every table gets its own horizontal scroll container.
    body = body.replace("<table>", '<div class="table-scroll"><table>')
    body = body.replace("</table>", "</table></div>")

    title = require(note, "title", f"notes #{i}")
    desc = note.get("description", site["description"])

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} — {e(site["short_name"])}</title>
<meta name="description" content="{e(desc)}">
<meta name="author" content="{e(site["name"])}">

<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(site["url"].rstrip("/") + "/" + out_rel)}">

<link rel="canonical" href="{e(site["url"].rstrip("/") + "/" + out_rel)}">
<link rel="stylesheet" href="{up}assets/css/style.css">
{FAVICON}
{THEME_SCRIPT}
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<header class="nav" id="nav">
  <div class="wrap nav__inner">
    <a class="nav__brand" href="{up}index.html">{md(site["short_name"]).replace(" ", "&nbsp;")}</a>
    <nav aria-label="Primary">
      <ul class="nav__links">
        <li><a href="{up}index.html#work">Work</a></li>
        <li class="is-optional"><a href="{up}index.html#experience">Experience</a></li>
        <li><a href="{up}index.html#contact">Contact</a></li>
        <li>
{indent(THEME_TOGGLE, 10)}
        </li>
      </ul>
    </nav>
  </div>
</header>

<main id="main" class="note">
  <div class="wrap">
    <a class="note__back" href="{up}index.html#work">Back to work</a>
    <article class="prose">
{indent(body, 6)}
    </article>
  </div>
</main>

<footer class="footer wrap">
  <span>© <span id="year">{date.today().year}</span> {md(site["name"])}</span>
  <span><a href="{up}index.html">{e(site["url"].replace("https://", "").rstrip("/"))}</a></span>
</footer>

<script src="{up}assets/js/main.js"></script>
</body>
</html>
'''
    return REPO / out_rel, page


# -------------------------------------------------------------------- main ---

def main() -> int:
    if not SITE_TOML.exists():
        print(f"ERROR: content file not found: {SITE_TOML}", file=sys.stderr)
        return 1

    try:
        with SITE_TOML.open("rb") as fh:
            cfg = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        print("ERROR: content/site.toml could not be parsed.\n"
              f"       {exc}\n"
              "       Check quotes and brackets near the line above.", file=sys.stderr)
        return 1

    try:
        for key in ("name", "short_name", "page_title", "description", "url",
                    "email", "linkedin", "github", "cv", "portrait"):
            require(cfg.get("site", {}), key, "site")

        written = []

        index = REPO / "index.html"
        index.write_text(build_index(cfg), encoding="utf-8")
        written.append(index)

        for i, note in enumerate(cfg.get("notes", []), 1):
            path, page = build_note(cfg, note, i)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(page, encoding="utf-8")
            written.append(path)
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for path in written:
        print(f"  wrote {path.relative_to(REPO).as_posix()} "
              f"({path.stat().st_size // 1024} KB)")

    # Warn about links pointing at files that aren't there.
    missing = []
    for rel in [cfg["site"]["cv"], cfg["site"]["portrait"]]:
        if not (REPO / rel).exists():
            missing.append(rel)
    for project in cfg.get("work", {}).get("projects", []):
        for link in project.get("links", []):
            href = link["href"]
            if not href.startswith(("http", "mailto:", "#")) and not (REPO / href).exists():
                missing.append(href)
        for fig in project.get("figures", []):
            if not (REPO / fig["src"]).exists():
                missing.append(fig["src"])
    if missing:
        print("\n  WARNING: these files are linked but missing from the repo:",
              file=sys.stderr)
        for m in dict.fromkeys(missing):
            print(f"    - {m}", file=sys.stderr)

    print("\nBuild complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
