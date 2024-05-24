import datetime

import httpx
import pytest
from django.core.management import call_command
from django.utils import timezone
from pytest_django.asserts import assertQuerySetEqual

from spock.company_score.models import LeMarcheRawTender


def test_sync_le_marche(settings, frozen_time, respx_mock) -> None:
    now = timezone.now()

    assert LeMarcheRawTender.objects.count() == 0
    settings.LE_MARCHE_API_BASE_URL = "https://marche.com"
    settings.LE_MARCHE_API_TOKEN = "token"
    mock = respx_mock.get("https://marche.com/api/datacube/tenders/")
    mock.respond(401)
    with pytest.raises(httpx.HTTPStatusError):
        call_command("sync_le_marche_tenders", wet_run=False)

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

    # Check dry run and wet run
    call_command("sync_le_marche_tenders", wet_run=False)
    assert LeMarcheRawTender.objects.count() == 0
    call_command("sync_le_marche_tenders", wet_run=True)
    assertQuerySetEqual(
        LeMarcheRawTender.objects.all(),
        [{"slug": "slug", "updated_at": now, "data": {"slug": "slug", "payload": "batman"}}],
        transform=lambda x: {"slug": x.slug, "updated_at": x.updated_at, "data": x.data},
    )

    # Modifyn updated_at even if the data is the same
    frozen_time.tick(delta=datetime.timedelta(seconds=10))
    call_command("sync_le_marche_tenders", wet_run=True)
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

    call_command("sync_le_marche_tenders", wet_run=True)
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
    call_command("sync_le_marche_tenders", wet_run=True)
    assert LeMarcheRawTender.objects.get().data == {"slug": "new-slug", "payload": "robin"}
