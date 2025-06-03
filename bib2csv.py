import sys
from bibtexparser.bparser import BibTexParser
import pandas as pd

if len(sys.argv) != 3:
    print("Usage: python script.py <input_file (BIB)> <output_file (CSV)>")
    sys.exit(1)
input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, encoding='utf-8') as bibfile:
    parser = BibTexParser()
    bib_database = parser.parse_file(bibfile)

# Extraer los datos
datos = []
for entry in bib_database.entries:
    datos.append({
        # remove { and }
        "title": entry["title"].replace("{", "").replace("}", "") if "title" in entry else "",
        "author": entry.get("author", "").split(" and ")[0],  # Solo el primer autor
        "publication": entry.get("journal", entry.get("booktitle", entry.get("archivePrefix", ""))),
        "year": entry.get("year", ""),
        "publisher": entry.get("publisher", ""),
    })
    # check if the entry has a DOI
    if "doi" in entry:
        datos[-1]["doi"] = entry["doi"]
    # check arxiv ID
    if entry.get("archivePrefix") != "":
        if datos[-1]["publication"] == "":
            datos[-1]["publication"] = "arXiv"
            datos[-1]["arxiv_id"] = entry.get("ID", "")

df = pd.DataFrame(datos)
df.to_csv(output_file, index=False)
