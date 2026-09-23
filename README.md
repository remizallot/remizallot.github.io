# remizallot.github.io

Personal academic site of Rémi Zallot, Senior Lecturer (Associate Professor) in
Biochemistry at Manchester Metropolitan University.
Live at **[remizallot.com](https://remizallot.com)**.

Jekyll, built from a fork of [Academic Pages](https://academicpages.github.io) (itself a
fork of [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/)). GitHub Pages
publishes it from the `master` branch; the custom domain lives in `CNAME`. Pushing to
`master` rebuilds the site within a minute or two — there is no PR flow.

## Local preview

The repository ships a Docker setup, which is the least fiddly option:

```bash
docker compose up
```

The site is then at <http://localhost:4000>. `_config_docker.yml` overrides `url` to an
empty string, so internal links resolve against localhost instead of sending you to the
live site — that override is why previewing through Docker works properly.

Without Docker, using the `Gemfile`:

```bash
bundle install
bundle exec jekyll serve -l -H localhost
```

This needs a reasonably current Ruby — the container uses 3.2. The Ruby that ships with
macOS (2.6) is too old to install these gems, which is the usual reason this route fails
where `docker compose up` succeeds. Note also that serving this way uses `_config.yml`
alone, so `url` still points at the live domain and internal links will navigate off your
local copy; add `--config _config.yml,_config_docker.yml` to get the relative-link
behaviour the Docker setup has by default.

A build is not strictly required for a text-only change, but do check that the YAML front
matter parses: an unescaped apostrophe in a single-quoted `title` or `citation` breaks the
whole build, and GitHub Pages fails quietly when it happens.

## Repository layout

| Path | Contents |
| --- | --- |
| `_publications/` | One file per paper. Rendered on `/publications/`. |
| `_posts/` | News items. Rendered on `/year-archive/` and in the homepage feed. |
| `_talks/`, `_teaching/`, `_portfolio/` | Other collections. `_portfolio/` is the "Tools" tab. |
| `_pages/` | Standalone pages: `about.md` (the homepage), `collaborators.md`, `cv.md`, `funding.md`, `join.md`, … |
| `_data/navigation.yml` | Top navigation. |
| `_data/career.yml` | Career stages pinned on the talk map. |
| **`cv/`** | **LaTeX source for the CV — see [The CV](#the-cv) below.** |
| `files/pdf/CV-Zallot-Remi.pdf` | The published CV, served by `/cv/`. A copy of `cv/cv.pdf`. |
| `markdown_generator/` | Legacy scripts that once produced collection files from spreadsheets. No longer used; entries are hand-written. |

## The CV

**The CV is not a hand-maintained binary — it is built from LaTeX source in
[`cv/`](cv/), which is version-controlled here.** Full instructions are in
[`cv/README.md`](cv/README.md); in short:

- `cv/cv.tex` — the CV itself. Edit this for wording and section changes.
- `cv/publications.bib` — a BibTeX database generated from `_publications/*.md`. The site
  is the source of truth, so regenerate it with the script in `cv/README.md` rather than
  editing it by hand.
- `cv/cv.pdf` — the compiled output.

To rebuild after adding a publication:

```bash
# 1. regenerate cv/publications.bib  (script in cv/README.md, run from the repo root)
# 2. compile
cd cv
pdflatex cv.tex && biber cv && pdflatex cv.tex && pdflatex cv.tex
# 3. publish the result where /cv/ serves it
cp cv.pdf ../files/pdf/CV-Zallot-Remi.pdf
```

Two fixups the generator drops every time it regenerates `publications.bib`, and which
must be reapplied afterwards:

- the PhD thesis entry must be `@phdthesis` with no `journal` field (the script always
  emits `@article`, leaving a bogus `journal = {n.d.}`);
- Greek letters need math mode — `$\beta$-lactone`, not `β-lactone`.
- multi-word surnames must be written surname-first so BibTeX splits them correctly —
  `San Francisco, Brian`, `El Yacoubi, Basma`.

Compiling needs only a standard TeX Live or MacTeX install.

## Adding a publication

Three steps, all in one commit — an entry without a news post is easy to miss.

**1. `_publications/YYYY-MM-DD-Title-With-Hyphens.md`**

```yaml
---
title: "Sentence case, exactly as published"
collection: publication
category: manuscripts        # or: books, conferences
permalink: /publication/YYYY-MM-DD-Title-With-Hyphens   # == the filename, minus .md
excerpt: 'DOI: 10.xxxx/yyyy'
date: YYYY-MM-DD
venue: 'Full journal name'
citation: 'Author One, Author Two, … &quot;Title.&quot; Venue, Volume(Issue), article number, Year.'
number: 1
---
DOI: [10.xxxx/yyyy](https://doi.org/10.xxxx/yyyy)
```

Conventions that are easy to get wrong:

- `permalink` must match the filename. The slug strips punctuation and accents:
  `β-lactone` became `lactone`.
- `citation` is a YAML string that ends up in HTML, so quotes are written `&quot;` and a
  literal `&` is `&amp;`. Author names keep their accents (`Rémi Zallot`).
- Older entries carry a `YYYY-01-01` date because the old generator only had the year.
  New entries use the real publication date; sorting is by `date`, newest first.
- `number` counts **down from newest**: the newest paper is `number: 1` and every existing
  entry shifts by one. Nothing renders it, but the sequence is kept intact.

**2. `_posts/YYYY-MM-DD-short-slug.md`** — a news item announcing it:

```yaml
---
title: 'Sentence case, no trailing period'
date: YYYY-MM-DD
permalink: /posts/YYYY/MM/short-slug/
tags:
  - news
  - publications
---
```

**3. Rebuild the CV** ([above](#the-cv)), and check whether anything else moved —
`_pages/about.md` carries the current affiliation and roles, and `_pages/collaborators.md`
lists collaborators by name and institution. A new co-author is not automatically a
collaborator.

## Writing style for news posts

First person, as Rémi. Plain and factual, no press-release register. A post about a paper
usually states what came out and where (linking the title to its `/publication/…` page
rather than straight to the DOI), says what the finding is in two or three sentences a
biochemist outside the subfield can follow, says what Rémi's own contribution was —
usually the bioinformatics — and ends with the DOI link.

Species names are italicised (`*Mycobacterium tuberculosis*`, then `*M. tuberculosis*`);
this works in post titles too, because the theme renders Markdown in titles everywhere
they appear. Gene names are lowercase italic, protein names roman (`rv2531c` / `Rv2531c`).
British spelling throughout: "characterised", "organisation", "analyse".

## Page layouts

The collection index pages — News, Publications, Talks, Teaching and Tools — use compact
list layouts rather than the template's card/tile style:

| Include | Used by |
| --- | --- |
| `_includes/compact-list-style.html` | Shared styling for all five pages. Colours come from the theme's CSS variables, so light and dark both follow the site toggle. |
| `_includes/archive-single-publication.html` | Publications, as a numbered bibliography. |
| `_includes/archive-single-compact.html` | Talks, Teaching and Tools. |

The template's original `_includes/archive-single.html` is still used by `single.html`,
`talk.html` and the taxonomy and category/tag archive pages, so it is deliberately kept.

## Credits

Forked from [Academic Pages](https://github.com/academicpages/academicpages.github.io),
which is © 2016 Michael Rose and released under the MIT License (see `LICENSE`).
