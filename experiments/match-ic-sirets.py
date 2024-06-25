import sys

from dc_utils import csv, recherche_entreprise

raw_ic_data = list(csv.line_reader(sys.argv[1]))
print(f"> found len={len(raw_ic_data)} lines")

for row in raw_ic_data:
    sirets = row[1].split(" ")
    valid_sirets = ""
    print(f"# {row[1]=}")
    for siret in sirets:
        if len(siret) != 14:
            continue

        print(f"searching for siret={siret}")
        company = recherche_entreprise.fetch_company(siret)
        if company:
            if (
                company["date_fermeture"] is not None
                or company["nombre_etablissements_ouverts"] == 0
            ):
                print(f"! company is closed for siret={siret}")
                continue
            try:
                if company["siege"]["siret"] == siret:
                    valid_sirets += f"{siret} "
                    print(f">>> found siret={siret}")
                    continue
            except KeyError:
                continue

            for etablissement in company["matching_etablissements"]:
                if etablissement["siret"] == siret:
                    try:
                        valid_sirets += f"{siret} "
                        print(f">>> found siret={siret}")
                        break
                    except KeyError:
                        continue
    csv.writer.writerow(
        [
            "CSV",
            row[0],
            row[1],
            valid_sirets.strip(),
        ]
    )
