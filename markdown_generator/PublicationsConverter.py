#!/usr/bin/env python
# coding: utf-8

import requests
from pybtex.database.input import bibtex
import pybtex.database.input.bibtex
from time import strptime
import string
import html
import os
import re
import pandas as pd

# ORCID to BibTeX conversion
orcid = '0000-0002-7317-1578'  # Fill your ORCID here
bib_filename = 'orcid_works.bib'

def fetch_orcid_works(orcid):
    response = requests.get(f'https://pub.orcid.org/v3.0/{orcid}/works',
                            headers={"Accept": "application/orcid+json"})
    record = response.json()
    put_codes = [work['work-summary'][0]['put-code'] for work in record['group']]
    return put_codes

def fetch_citations(orcid, put_codes):
    citations = []
    for put_code in put_codes:
        response = requests.get(f'https://pub.orcid.org/v3.0/{orcid}/work/{put_code}',
                                headers={"Accept": "application/orcid+json"})
        work = response.json()
        if work['citation'] is not None:
            citations.append(work['citation']['citation-value'])
    return citations

def save_citations_to_bib(citations, filename):
    with open(filename, 'w') as bibfile:
        for citation in citations:
            bibfile.write(citation + '\n')

# Check if the .bib file exists
if not os.path.exists(bib_filename):
    # Fetch ORCID works and save to BibTeX
    put_codes = fetch_orcid_works(orcid)
    citations = fetch_citations(orcid, put_codes)
    save_citations_to_bib(citations, bib_filename)
else:
    print(f'Using existing {bib_filename} file.')

# BibTeX to Markdown conversion
publist = {
    "proceeding": {
        "file": bib_filename,
        "venuekey": "booktitle",
        "venue-pretext": "In the proceedings of ",
        "collection": {"name": "publications",
                       "permalink": "/publication/"}
    },
    "journal": {
        "file": bib_filename,
        "venuekey": "journal",
        "venue-pretext": "",
        "collection": {"name": "publications",
                       "permalink": "/publication/"}
    }
}

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)

def process_bibtex(publist):
    for pubsource in publist:
        parser = bibtex.Parser()
        bibdata = parser.parse_file(publist[pubsource]["file"])

        # Handle duplicate entries
        entry_counts = {}
        for bib_id in list(bibdata.entries.keys()):
            if bib_id in entry_counts:
                entry_counts[bib_id] += 1
                new_bib_id = f"{bib_id}{chr(97 + entry_counts[bib_id] - 1)}"
                bibdata.entries[new_bib_id] = bibdata.entries.pop(bib_id)
                bib_id = new_bib_id
            else:
                entry_counts[bib_id] = 1

        # loop through the individual references in a given bibtex file
        for bib_id in bibdata.entries:
            # reset default date
            pub_year = "1900"
            pub_month = "01"
            pub_day = "01"

            b = bibdata.entries[bib_id].fields

            try:
                pub_year = f'{b["year"]}'

                # todo: this hack for month and day needs some cleanup
                if "month" in b.keys():
                    if len(b["month"]) < 3:
                        pub_month = "0" + b["month"]
                        pub_month = pub_month[-2:]
                    elif b["month"] not in range(12):
                        tmnth = strptime(b["month"][:3], '%b').tm_mon
                        pub_month = "{:02d}".format(tmnth)
                    else:
                        pub_month = str(b["month"])
                if "day" in b.keys():
                    pub_day = str(b["day"])

                pub_date = pub_year + "-" + pub_month + "-" + pub_day

                # strip out {} as needed (some bibtex entries that maintain formatting)
                clean_title = b["title"].replace("{", "").replace("}", "").replace("\\", "").replace(" ", "-")

                url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
                url_slug = url_slug.replace("--", "-")

                md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--", "-")
                html_filename = (str(pub_date) + "-" + url_slug).replace("--", "-")

                # Check if the file already exists
                if os.path.exists("../_publications/" + md_filename):
                    print(f'File {md_filename} already exists. Skipping.')
                    continue

                # Build Citation from text
                citation = ""

                # citation authors - todo - add highlighting for primary author?
                for author in bibdata.entries[bib_id].persons["author"]:
                    citation = citation + " " + author.first_names[0] + " " + author.last_names[0] + ", "

                # citation title
                citation = citation + "\"" + html_escape(b["title"].replace("{", "").replace("}", "").replace("\\", "")) + ".\""

                # add venue logic depending on citation type
                venue = publist[pubsource]["venue-pretext"] + b[publist[pubsource]["venuekey"]].replace("{", "").replace("}", "").replace("\\", "")

                citation = citation + " " + html_escape(venue)
                citation = citation + ", " + pub_year + "."

                ## YAML variables
                md = "---\ntitle: \"" + html_escape(b["title"].replace("{", "").replace("}", "").replace("\\", "")) + '"\n'

                md += """collection: """ + publist[pubsource]["collection"]["name"]

                md += """\npermalink: """ + publist[pubsource]["collection"]["permalink"] + html_filename

                note = False
                if "note" in b.keys():
                    if len(str(b["note"])) > 5:
                        md += "\nexcerpt: '" + html_escape(b["note"]) + "'"
                        note = True

                md += "\ndate: " + str(pub_date)

                md += "\nvenue: '" + html_escape(venue) + "'"

                url = False
                if "url" in b.keys():
                    if len(str(b["url"])) > 5:
                        md += "\npaperurl: '" + b["url"] + "'"
                        url = True

                md += "\ncitation: '" + html_escape(citation) + "'"

                md += "\n---"

                ## Markdown description for individual page
                if note:
                    md += "\n" + html_escape(b["note"]) + "\n"

                if url:
                    md += "\n[Access paper here](" + b["url"] + "){:target=\"_blank\"}\n"
                else:
                    md += "\nUse [Google Scholar](https://scholar.google.com/scholar?q=" + html.escape(clean_title.replace("-", "+")) + "){:target=\"_blank\"} for full citation"

                md_filename = os.path.basename(md_filename)

                with open("../_publications/" + md_filename, 'w', encoding="utf-8") as f:
                    f.write(md)
                print(f'SUCCESSFULLY PARSED {bib_id}: \"', b["title"][:60], "..." * (len(b['title']) > 60), "\"")
            # field may not exist for a reference
            except KeyError as e:
                print(f'WARNING Missing Expected Field {e} from entry {bib_id}: \"', b["title"][:30], "..." * (len(b['title']) > 30), "\"")
                continue
            except pybtex.database.BibliographyDataError as e:
                print(f'WARNING {e}')
                continue

# Process BibTeX files
process_bibtex(publist)

# TSV to Markdown conversion
publications = pd.read_csv("publications.tsv", sep="\t", header=0)

for row, item in publications.iterrows():
    md_filename = str(item.pub_date) + "-" + item.url_slug + ".md"
    html_filename = str(item.pub_date) + "-" + item.url_slug
    year = item.pub_date[:4]

    # Check if the file already exists
    if os.path.exists("../_publications/" + md_filename):
        print(f'File {md_filename} already exists. Skipping.')
        continue

    ## YAML variables
    md = "---\ntitle: \"" + item.title + '"\n'

    md += """collection: publications"""

    md += """\npermalink: /publication/""" + html_filename

    if len(str(item.excerpt)) > 5:
        md += "\nexcerpt: '" + html_escape(item.excerpt) + "'"

    md += "\ndate: " + str(item.pub_date)

    md += "\nvenue: '" + html_escape(item.venue) + "'"

    if len(str(item.paper_url)) > 5:
        md += "\npaperurl: '" + item.paper_url + "'"

    md += "\ncitation: '" + html_escape(item.citation) + "'"

    md += "\n---"

    ## Markdown description for individual page
    if len(str(item.paper_url)) > 5:
        md += "\n\n<a href='" + item.paper_url + "'>Download paper here</a>\n"

    if len(str(item.excerpt)) > 5:
        md += "\n" + html_escape(item.excerpt) + "\n"

    md += "\nRecommended citation: " + item.citation

    md_filename = os.path.basename(md_filename)

    with open("../_publications/" + md_filename, 'w') as f:
        f.write(md)
