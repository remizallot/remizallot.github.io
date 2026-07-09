# CV (LaTeX)

A self-contained, self-compilable academic CV, styled to match the
website (same teal accent, clean modern layout). Content is sourced
from the same facts already verified on the live site (`_pages/about.md`,
`_pages/funding.md`, `_publications/`, `_teaching/`, `_talks/`).

## Compiling

Requires only a standard TeX Live or MacTeX install -- nothing extra
to download. From this directory:

```sh
pdflatex cv.tex
biber cv
pdflatex cv.tex
pdflatex cv.tex
```

(Three passes plus `biber` is the standard cycle needed for
`biblatex` to resolve and number the publication list correctly --
the first two passes will warn about an "empty bibliography" and
"undefined references"; that's expected and resolves by the final
pass.)

This produces `cv.pdf`.

## Files

- `cv.tex` -- the CV itself. Edit this directly for wording/section changes.
- `publications.bib` -- a real BibTeX database of all 29 publications,
  auto-generated from `_publications/*.md` (see script below). Machine-
  readable and importable into any reference manager, independent of the CV.
- `.gitignore` -- ignores LaTeX build byproducts (`.aux`, `.bbl`, `.log`, etc).

## Keeping publications.bib in sync

If new publications are added to `_publications/`, regenerate the bib
file rather than hand-editing it (source of truth is the Jekyll site).
From the repo root:

```python
python3 << 'EOF'
import re, glob, html

entries = []
for path in sorted(glob.glob("_publications/*.md")):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    fm = content.split("---")[1]
    def get(field):
        m = re.search(rf'^{field}\s*:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
        return m.group(1) if m else None
    title = html.unescape(get("title") or "").strip()
    date = get("date")
    year = date[:4] if date else "n.d."
    venue = html.unescape((get("venue") or "").strip("'\""))
    citation = html.unescape((get("citation") or "").strip("'\""))
    m = re.match(r'^(.*?)\.\s*"(.*)"\.\s*(.*?),\s*(\d{4})\.?$', citation)
    authors_raw = m.group(1).strip() if m else citation.split('. "')[0].strip()
    authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
    truncated = len(authors) == 10  # Google Scholar caps author lists at 10
    entries.append({"title": title, "year": year, "venue": venue, "authors": authors, "truncated": truncated})

entries.sort(key=lambda e: (e["year"], e["title"]), reverse=True)

def bibkey(e):
    surname = re.sub(r'[^A-Za-z]', '', e["authors"][0].split()[-1]) if e["authors"] else "unknown"
    firstword = re.sub(r'[^A-Za-z]', '', e["title"].split()[0]) if e["title"] else "x"
    return f"{surname}{e['year']}{firstword}".lower()

used, lines = {}, ["% Auto-generated from _publications/*.md -- source of truth is the Jekyll site.\n"]
for e in entries:
    key = bibkey(e)
    used[key] = used.get(key, -1) + 1
    if used[key]: key = f"{key}{used[key]}"
    author_field = " and ".join(e["authors"]) + (" and others" if e["truncated"] else "")
    lines.append(f'@article{{{key},\n  author  = {{{author_field}}},\n  title   = {{{e["title"].replace("&", r"\&")}}},\n  journal = {{{e["venue"] or "n.d."}}},\n  year    = {{{e["year"]}}},\n}}\n')

with open("cv/publications.bib", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
EOF
```

After regenerating, re-check for any titles containing raw `&`, Greek
letters, or other LaTeX-special characters (the script escapes `&`
automatically, but new entries with e.g. Greek letters need manual
`$\beta$`-style math-mode escaping -- see the existing β-lactone entry
for the pattern) and re-verify the PhD thesis entry is still typed as
`@phdthesis`, not `@article` (the script always emits `@article`).

## Design notes

- Engine: `pdflatex` (not `xelatex`) with the `tgheros` package for the
  sans-serif font -- this loads TeX Gyre Heros through LaTeX's own font
  system rather than searching installed OS fonts, so it compiles
  identically on any machine with TeX Live/MacTeX, with zero extra
  font installation.
- `hyperref` sets real PDF metadata (title/author/subject/keywords) via
  `pdfusetitle`, so the file is properly indexable/searchable, not just
  visually laid out.
- Accent colour (`#0F766E`) matches the website's teal theme.
