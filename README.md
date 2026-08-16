# andyfuuu25.github.io

Personal portfolio site for **Chi Leong Andy Fu** — live at
<https://andyfuuu25.github.io/>.

Static HTML, CSS and vanilla JavaScript. No build step, no framework, no
dependencies. The only tooling is a one-off script that renders a markdown
research note into a styled page.

## Layout

```
index.html                        single-page portfolio
research/
  summit-therapeutics.html        generated — do not edit by hand
assets/
  css/style.css                   all styling (light + dark palettes)
  js/main.js                      theme toggle, scroll-spy, reveal-on-scroll
  img/                            headshot and research exhibits
  files/Andy_Fu_CV.pdf            downloadable CV
tools/
  build_note.py                   markdown research note -> research/*.html
```

## Editing

**Content** — everything on the landing page lives in `index.html`. Project
entries are `<article class="card">` blocks; experience entries are
`<li class="timeline__item">` blocks. Copy an existing one and edit it.

**Colours and type** — the CSS custom properties at the top of
`assets/css/style.css`. The light palette is defined on bare `:root`; the dark
palette is repeated in a `prefers-color-scheme` block and a
`[data-theme="dark"]` block so the manual toggle wins in both directions. If
you add a colour, define it in all three places.

**CV** — replace `assets/files/Andy_Fu_CV.pdf` with the new file, keeping the
filename, and nothing else needs to change.

**The research note** — the source of truth is the markdown file on the
Desktop, not the generated HTML. Edit the markdown, then:

```bash
python tools/build_note.py
```

That requires the `markdown` package (`pip install markdown`). The script
rewrites image paths to the optimized copies in `assets/img/` and wraps every
table in a horizontal scroll container.

## Local preview

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>. Opening `index.html` directly as a `file://`
URL works too, but a local server matches how GitHub Pages serves it.

## Deploying

The site is served from the `main` branch root. Push, and GitHub Pages
redeploys within about a minute:

```bash
git add -A && git commit -m "Update site" && git push
```
