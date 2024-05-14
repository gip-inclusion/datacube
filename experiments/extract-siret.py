import sys
from time import sleep

from dc_utils import api_entreprise, csv, google

# delay between every call to Google + SIRENE
# Let's avoid hitting the spam limits, should use a 429 analysis later
SLEEP_TIME_BETWEEN_DOMAINS = 0.1


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


IF_BY_SIRET = {
    siret: [raison_sociale, nb_conventions]
    for siret, raison_sociale, nb_conventions in csv.line_reader(sys.argv[1])
}

IF_BY_SIREN = {
    siret[:9]: [raison_sociale, nb_conventions]
    for siret, raison_sociale, nb_conventions in csv.line_reader(sys.argv[1])
}

raw_marché_data = sorted(csv.line_reader(sys.argv[2]), key=lambda x: x[0])
print(f"> found len={len(raw_marché_data)} email domains")

MARCHE_DATA = {
    domain: nb_demandes
    for domain, _, _, nb_demandes in raw_marché_data
    if domain not in BANNED_DOMAINS
}
print(f"> unique domains len={len(MARCHE_DATA)}")

for marché_domain, marché_nb_demandes in MARCHE_DATA.items():
    print(f"searching for domain={marché_domain}")
    for siret in google.search_siret(marché_domain):
        print(f"# found siret={siret} for domain={marché_domain}")
        company = api_entreprise.get_company(siret)
        if company:
            if_name, if_nb_conventions = "", ""
            if siret in IF_BY_SIRET:
                if_name, if_nb_conventions = IF_BY_SIRET[siret]
            elif company.siren in IF_BY_SIREN:
                if_name, if_nb_conventions = IF_BY_SIREN[company.siren]
            csv.writer.writerow(
                [
                    "CSV",
                    siret,
                    company.siren,
                    company.name,
                    company.city,
                    company.post_code,
                    company.effectifs,
                    if_name,
                    if_nb_conventions,
                    marché_domain,
                    marché_nb_demandes,
                ]
            )
            break
        else:
            print(f"!!! no company found for siret={siret}")
            continue
    else:
        print(f"!!! no google match found for domain={marché_domain}")

    sleep(SLEEP_TIME_BETWEEN_DOMAINS)
