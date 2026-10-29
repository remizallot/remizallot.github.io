---
title: "CD-HIT in Google Colab"
excerpt: "Run CD-HIT sequence clustering in the browser, with no installation: an alternative to the CD-HIT web server."
collection: portfolio
date: 2026-10-20
---
The CD-HIT web server has been unavailable since 2022, which left many users without an easy way to cluster sequences and remove redundancy. As an alternative, I wrote a Google Colab notebook that builds [CD-HIT](https://github.com/weizhongli/cdhit) from source and runs it on your own sequences, entirely in the browser.

All parameters are form fields with explanatory notes, so a saved copy of the notebook records exactly what was run. Each run also writes a provenance file with the CD-HIT version, the full command line, an input checksum and a timestamp. The notes also explain two options that are often confused, `-s` (minimum length ratio) and `-aS` (alignment coverage of the shorter sequence).

[Open in Colab](https://colab.research.google.com/github/remizallot/cdhit-colab/blob/main/CD-HIT_Colab.ipynb) · [GitHub](https://github.com/remizallot/cdhit-colab) · Zenodo: [10.5281/zenodo.23503573](https://doi.org/10.5281/zenodo.23503573)
