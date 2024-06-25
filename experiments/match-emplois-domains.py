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


raw_emplois_emails = list(csv.line_reader(sys.argv[1]))
print(f"> found len={len(raw_emplois_emails)} emails")

domains = set(row[0].split("@")[1] for row in raw_emplois_emails)
print(f"> found len={len(domains)} unique domains")

EMAIL_DOMAINS = {
    domain: ["", "", False] for domain in domains if domain not in BANNED_DOMAINS
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
            csv.writer.writerow(
                ["CSV"] + [domain] + [siret, company["nom_raison_sociale"], is_valid]
            )
            break
        else:
            print(f"!!! no company found for siret={siret}")
            continue
    else:
        print(f"!!! no google match found for domain={domain}")
