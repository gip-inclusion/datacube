import os
import logging
from dataclasses import dataclass

import requests


logger = logging.getLogger(__name__)


@dataclass
class Etablissement:
    name: str
    siren: str
    address_line_1: str
    address_line_2: str
    post_code: str
    city: str
    effectifs: int
    is_head_office: bool
    is_closed: bool


def _get_token():
    r = requests.post(
        f"{os.environ.get('API_INSEE_BASE_URL')}/token",
        data={"grant_type": "client_credentials"},
        auth=(
            os.environ.get("API_INSEE_CLIENT_ID"),
            os.environ.get("API_INSEE_CLIENT_SECRET"),
        ),
    )
    r.raise_for_status()
    access_token = r.json()["access_token"]
    return access_token


def _etablissement_get_or_error(token, siret):
    token = _get_token()
    if not token:
        return None

    url = f"{os.environ.get('API_INSEE_BASE_URL')}/entreprises/sirene/siret/{siret}"
    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    r.raise_for_status()

    data = r.json()["etablissement"]
    siren = data["siren"]
    name = data["uniteLegale"]["denominationUniteLegale"]
    address = data["adresseEtablissement"]
    address_parts = [
        address["numeroVoieEtablissement"],
        address["typeVoieEtablissement"],
        address["libelleVoieEtablissement"],
    ]
    post_code = address["codePostalEtablissement"]
    city = address["libelleCommuneEtablissement"]
    effectifs = data["trancheEffectifsEtablissement"]
    establishments_status = data["periodesEtablissement"][0][
        "etatAdministratifEtablissement"
    ]
    is_head_office = data["etablissementSiege"]

    etablissement = Etablissement(
        siren=siren,
        name=name,
        address_line_1=" ".join(filter(None, address_parts)) or None,
        address_line_2=address.get("complementAdresseEtablissement"),
        post_code=post_code,
        city=city,
        effectifs=effectifs,
        is_closed=(establishments_status == "F"),
        is_head_office=is_head_office,
    )

    return etablissement


def get_company(siret):
    token = _get_token()
    try:
        return _etablissement_get_or_error(token, siret)
    except requests.exceptions.HTTPError:
        return None
