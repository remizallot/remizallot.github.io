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

def generate_markdown(entry, pub_date, url_slug, i):
    b = entry.fields

    # Build Citation
    authors = [f"**{a.first_names[0]} {a.last_names[0]}**" for a in entry.persons.get("author", [])]
    citation = ", ".join(authors)
    citation += f". \"{html_escape(b.get('title', '').replace('{', '').replace('}', '').replace('\\', ''))}.\" "
    venue = html_escape(b.get('journal', '').replace('{', '').replace('}', '').replace('\\', ''))
    citation += f"{venue}, {b.get('year', '')}."

    # YAML front matter
    md = f"---\n"
    md += f"title: \"{html_escape(b.get('title', '').replace('{', '').replace('}', '').replace('\\', ''))}\"\n"
    md += f"collection: publication\n"
    md += f"category: manuscripts\n"
    md += f"permalink: /publication/{pub_date}-{url_slug}\n"
    if 'note' in b and len(b['note']) > 5:
        md += f"excerpt: '{html_escape(b['note'])}'\n"
    md += f"date: {pub_date}\n"
    md += f"venue: '{venue}'\n"
    md += f"citation: '{html_escape(citation)}'\n"
    md += f"---\n"

    # Number before title in markdown content (to be visible on the page)
    number_title = f"**[{i}]** {b.get('title', '')}"

    # Markdown content (adding the number to the visible content)
    md_content = f"# {number_title}\n\n"  # Insert number before title

    # If there's an excerpt or note, we display it
    if 'note' in b and len(b['note']) > 5:
        md_content += f"{html_escape(b['note'])}\n\n"
        md_content += f'Use [Google Scholar](https://scholar.google.com/scholar?q={html.escape(b["title"].replace(" ", "+"))}) for full citation\n'

    return md + md_content

def main():
    bibdata = parse_bibtex(BIB_FILE)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    entries_with_date = []
    for bib_id, entry in bibdata.entries.items():
        b = entry.fields
        try:
            pub_year = b['year']
            pub_month = b.get('month', '01')
            pub_day = b.get('day', '01')

            if pub_month.isdigit():
                pub_month = f"{int(pub_month):02d}"
            else:
                try:
                    pub_month = f"{strptime(pub_month[:3], '%b').tm_mon:02d}"
                except ValueError:
                    pub_month = "01"

            pub_date = f"{pub_year}-{pub_month}-{pub_day}"

            entries_with_date.append((bib_id, entry, pub_date))

        except KeyError as e:
            print(f"WARNING: Missing expected field {e} from entry {bib_id}: \"{b.get('title', '')[:30]}\"...")

    # Sort entries by publication date (most recent first)
    entries_with_date.sort(key=lambda x: x[2], reverse=True)

    # Generate markdown files with numbering and bold author names
    for i, (bib_id, entry, pub_date) in enumerate(entries_with_date, start=1):
        b = entry.fields
        clean_title = b.get('title', '').replace('{', '').replace('}', '').replace('\\', '').replace(' ', '-')
        url_slug = re.sub(r'[^a-zA-Z0-9_-]', '', clean_title).replace('--', '-')
        md_filename = f"{pub_date}-{url_slug}.md"

        print(f"Generating file for {bib_id}: {pub_date} -> {md_filename}")

        md_content = generate_markdown(entry, pub_date, url_slug, i)

        try:
            with open(os.path.join(OUTPUT_DIR, md_filename), 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"SUCCESSFULLY PARSED {bib_id}: \"{b.get('title', '')[:60]}\" with number {i}...")
        except Exception as e:
            print(f"ERROR writing to file {md_filename}: {e}")

if __name__ == "__main__":
    main()
