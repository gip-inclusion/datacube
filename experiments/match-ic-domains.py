import sys

from dc_utils import csv, google, recherche_entreprise

BANNED_DOMAINS = [
    "bbox.fr",
    "cegetel.net",
    "free.fr",
    "gmail.com",
    "gmx.fr",
    "googlemail.com",
    "hotmail.com",
    "hotmail.fr",
    "icloud.com",
    "laposte.net",
    "live.fr",
    "msn.com",
    "neuf.fr",
    "numericable.fr",
    "orange.fr",
    "outlook.com",
    "outloook.fr",
    "outlook.fr",
    "sfr.fr",
    "wanadoo.fr",
    "yahoo.com",
    "yahoo.fr",
    "yandex.com",
    "yopmail.com",
]


raw_ic_data = list(csv.line_reader(sys.argv[1]))
print(f"> found len={len(raw_ic_data)} email domains")

EMAIL_DOMAINS = {
    domain: ["", "", False] for _, domain in raw_ic_data if domain not in BANNED_DOMAINS
}
print(f"> unique valid domains len={len(EMAIL_DOMAINS)}")

for domain in EMAIL_DOMAINS:
    print(f"searching for domain={domain}")
    for siret in google.search_siret(domain):
        print(f"# found siret={siret} for domain={domain}")
        company = recherche_entreprise.fetch_company(siret)
        if company:
            is_valid = (
                company["date_fermeture"] is None
                and company["nombre_etablissements_ouverts"] != 0
            )
            EMAIL_DOMAINS[domain] = [siret, company["nom_raison_sociale"], is_valid]
            break
        else:
            print(f"!!! no company found for siret={siret}")
            continue
    else:
        print(f"!!! no google match found for domain={domain}")

print(EMAIL_DOMAINS)

for row in raw_ic_data:
    domain = row[1]
    if domain in EMAIL_DOMAINS:
        csv.writer.writerow(["CSV"] + row + EMAIL_DOMAINS[row[1]])
    else:
        csv.writer.writerow(["CSV"] + row + ["", "", False])
