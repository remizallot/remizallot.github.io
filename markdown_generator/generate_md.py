import os
from pybtex.database.input import bibtex
import html
import re
from time import strptime

# Configuration
BIB_FILE = 'pubs.bib'  # Path to your BibTeX file
OUTPUT_DIR = '../_publications'  # Directory where the markdown files will be saved

# HTML escape table
html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)

def parse_bibtex(file_path):
    parser = bibtex.Parser()
    return parser.parse_file(file_path)

def generate_markdown(entry, pub_date, url_slug):
    b = entry.fields

    # Build Citation
    citation = ""
    for author in entry.persons["author"]:
        citation += f"{author.first_names[0]} {author.last_names[0]}, "
    citation += f"\"{html_escape(b['title'].replace('{', '').replace('}', '').replace('\\', ''))}.\" "
    venue = b['journal'].replace('{', '').replace('}', '').replace('\\', '')
    citation += f"{html_escape(venue)}, {b['year']}."

    # YAML front matter
    md = f"---\ntitle: \"{html_escape(b['title'].replace('{', '').replace('}', '').replace('\\', ''))}\"\n"
    md += f"collection: publications\n"
    md += f"permalink: /publication/{pub_date}-{url_slug}\n"
    if 'note' in b and len(b['note']) > 5:
        md += f"excerpt: '{html_escape(b['note'])}'\n"
    md += f"date: {pub_date}\n"
    md += f"venue: '{html_escape(venue)}'\n"
    md += f"citation: '{html_escape(citation)}'\n"
    md += "---\n"

    # Markdown content
    if 'note' in b and len(b['note']) > 5:
        md += f"{html_escape(b['note'])}\n\n"
    md += f"Use [Google Scholar](https://scholar.google.com/scholar?q={html.escape(b['title'].replace(' ', '+'))}){:target=\"_blank\"} for full citation\n"

    return md

def main():
    bibdata = parse_bibtex(BIB_FILE)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for bib_id in bibdata.entries:
        entry = bibdata.entries[bib_id]
        b = entry.fields

        try:
            pub_year = b['year']
            pub_month = b.get('month', '01')
            pub_day = b.get('day', '01')

            if len(pub_month) < 3:
                pub_month = f"0{pub_month}"
            elif pub_month not in range(12):
                tmnth = strptime(pub_month[:3], '%b').tm_mon
                pub_month = f"{tmnth:02d}"

            pub_date = f"{pub_year}-{pub_month}-{pub_day}"

            clean_title = b['title'].replace('{', '').replace('}', '').replace('\\', '').replace(' ', '-')
            url_slug = re.sub(r'\\[.*\\]|[^a-zA-Z0-9_-]', '', clean_title).replace('--', '-')
            md_filename = f"{pub_date}-{url_slug}.md"

            md_content = generate_markdown(entry, pub_date, url_slug)

            with open(os.path.join(OUTPUT_DIR, md_filename), 'w', encoding='utf-8') as f:
                f.write(md_content)

            print(f"SUCCESSFULLY PARSED {bib_id}: \"{b['title'][:60]}\"...")

        except KeyError as e:
            print(f"WARNING: Missing expected field {e} from entry {bib_id}: \"{b['title'][:30]}\"...")

if __name__ == "__main__":
    main()
