import datetime
from io import StringIO

import httpx
import pytest
from django.core.management import call_command
from django.utils import timezone
from pytest_django.asserts import assertQuerySetEqual

from spock.company_score.models import DomainSirenAssociation, LeMarcheRawTender


def test_sync_if_conventions():
    # FIXME(vperron) / Untested as it is a CSV import for now. Test it when it's the API.
    pass


def test_sync_le_marche(settings, frozen_time, respx_mock) -> None:
    now = timezone.now()

    assert LeMarcheRawTender.objects.count() == 0
    settings.LE_MARCHE_API_BASE_URL = "https://marche.com"
    settings.LE_MARCHE_API_TOKEN = "token"
    mock = respx_mock.get("https://marche.com/api/datacube/tenders/")
    mock.respond(401)
    with pytest.raises(httpx.HTTPStatusError):
        call_command("sync_le_marche_tenders")

    mock.respond(
        200,
        json={
            "results": [
                {
                    "slug": "slug",
                    "payload": "batman",
                }
            ],
            "next": None,
        },
    )

    call_command("sync_le_marche_tenders")
    assertQuerySetEqual(
        LeMarcheRawTender.objects.all(),
        [{"slug": "slug", "updated_at": now, "data": {"slug": "slug", "payload": "batman"}}],
        transform=lambda x: {"slug": x.slug, "updated_at": x.updated_at, "data": x.data},
    )

    # Modifyn updated_at even if the data is the same
    frozen_time.tick(delta=datetime.timedelta(seconds=10))
    call_command("sync_le_marche_tenders")
    tender = LeMarcheRawTender.objects.get()
    assert tender.updated_at == now + datetime.timedelta(seconds=10)
    assert tender.data == {"slug": "slug", "payload": "batman"}

    # Update and addition
    mock.respond(
        200,
        json={
            "results": [
                {
                    "slug": "slug",
                    "payload": "the-joker",
                },
                {
                    "slug": "new-slug",
                    "payload": "robin",
                },
            ],
            "next": None,
        },
    )

    call_command("sync_le_marche_tenders")
    assert LeMarcheRawTender.objects.get(slug="slug").data == {"slug": "slug", "payload": "the-joker"}
    assert LeMarcheRawTender.objects.get(slug="new-slug").data == {"slug": "new-slug", "payload": "robin"}

    # Only Robin stays
    mock.respond(
        200,
        json={
            "results": [
                {
                    "slug": "new-slug",
                    "payload": "robin",
                },
            ],
            "next": None,
        },
    )
    call_command("sync_le_marche_tenders")
    assert LeMarcheRawTender.objects.get().data == {"slug": "new-slug", "payload": "robin"}


def test_resolve_domain_sirens(monkeypatch) -> None:
    # The Google API Client itself is untested.
    # Why ? Thin wrapper around SERPApi, and is still subject to change if
    # we decide to try something else.
    from spock.company_score.management.commands import resolve_domain_sirens

    out = StringIO()

    class FakeGoogleApiClient:
        def __init__(self, api_key, debug):
            pass

        def search_siret(self, domain):
            if domain == "cool.com":
                yield "123456789"

    monkeypatch.setattr(resolve_domain_sirens, "GoogleAPIClient", FakeGoogleApiClient)
    pairing = DomainSirenAssociation(domain="not-found.com", siren=None)
    pairing.save()
    call_command("resolve_domain_sirens", wet_run=True, stdout=out)
    pairing.refresh_from_db()
    assert pairing.siren is None
    assert out.getvalue() == ""

    pairing = DomainSirenAssociation(domain="cool.com", siren=None)
    pairing.save()

    call_command("resolve_domain_sirens", wet_run=True, stdout=out)
    pairing.refresh_from_db()
    assert pairing.siren == "123456789"

    assert out.getvalue() == "> resolved pairing.domain='cool.com' to SIREN pairing.siren='123456789'\n"


def test_resolve_siren_companies(monkeypatch) -> None:
    # TODO
    pass


def test_score_companies(monkeypatch) -> None:
    # TODO
    pass
