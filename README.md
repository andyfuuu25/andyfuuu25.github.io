# andyfuuu25.github.io

Personal portfolio site for **Chi Leong Andy Fu** — live at
<https://andyfuuu25.github.io/>.

**All the content lives in [`content/site.toml`](content/site.toml). You never
edit HTML.** Change that file, run the build, push. That's the whole workflow.

---

## How to change things

### The short version

| I want to… | Do this |
|---|---|
| Change any wording | Edit `content/site.toml` |
| Swap the CV | Drop the PDF in `assets/files/`, set `cv = ` to its filename |
| Swap the photo | Drop the image in `assets/img/`, set `portrait = ` to its filename |
| Remove a project | Delete its whole `[[work.projects]]` block |
| Add a project | Copy an existing `[[work.projects]]` block and edit it |
| Reorder projects | Move the blocks — page order follows file order |
| Edit a research note | Edit the markdown in `content/notes/` |
| Add a research note | Add the markdown, then a `[[notes]]` block at the end of `site.toml` |

Then **double-click `build.bat`** (or run `python tools/build.py`), and commit.

### Formatting inside site.toml

Any text field accepts a little markdown:

```
**bold**      *italic*      `code`      [link text](https://example.com)
```

Text in `"""triple quotes"""` can span lines. A blank line inside it starts a
new paragraph. Single line breaks are ignored, so you can wrap text however
you like without changing the output.

### Editing from your phone or any browser

You don't need this computer. GitHub rebuilds the site itself on every push:

1. Open `content/site.toml` on github.com
2. Click the pencil icon, edit, hit **Commit changes**
3. Wait ~1 minute — the Actions tab shows the build, then the site updates

That works for the research notes in `content/notes/` too.

---

## Layout

```
content/
  site.toml              ← ALL page content. This is the file you edit.
  notes/
    summit-therapeutics.md   research note source (markdown)
  source/                originals kept for re-cropping; not published
build.bat                double-click to rebuild
tools/
  build.py               generates the HTML from content/
index.html               GENERATED — do not edit, your changes get overwritten
research/
  summit-therapeutics.html   GENERATED
assets/
  css/style.css          all styling (light + dark palettes)
  js/main.js             theme toggle, scroll-spy, reveal-on-scroll
  img/                   headshot and research exhibits
  files/                 CV and the research note PDF
```

`index.html` and everything under `research/` are build output. Editing them
by hand works until the next build, which silently overwrites your changes —
so put the change in `content/` instead.

### Colours and type

The CSS custom properties at the top of `assets/css/style.css`. The light
palette is on bare `:root`; the dark palette is repeated in a
`prefers-color-scheme` block and a `[data-theme="dark"]` block so the manual
toggle wins in both directions. If you add a colour, define it in all three.

---

## Running it locally

```bash
python tools/build.py        # or double-click build.bat
python -m http.server 8000   # then open http://localhost:8000
```

The build needs Python 3.11+ (for the built-in TOML reader) and the `markdown`
package, which `build.bat` installs for you if it's missing:

```bash
python -m pip install markdown
```

The build refuses to write anything if `site.toml` has a syntax error, and
tells you the line — so a typo can't leave you with a half-broken site. It also
warns if you link to a file that isn't in the repo.

---

## Publishing

```bash
git add -A && git commit -m "Update site" && git push
```

GitHub Actions rebuilds from `content/` and deploys to Pages, usually within a
minute. The workflow is `.github/workflows/static.yml`; you can also re-run a
deploy by hand from the repo's **Actions** tab.
