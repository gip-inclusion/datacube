import httpx
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from furl import furl

from spock.company_score.models import DomainSirenAssociation, LeMarcheRawTender


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


class LeMarcheClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def fetch_tenders(self):
        f = furl(self.base_url)
        f.path = f.path / "api" / "datacube" / "tenders/"
        f.add({"limit": 1000, "order_by": "-created_at"})
        next_url = f.url
        tenders = []
        while next_url:
            response = httpx.get(next_url, headers={"Authorization": f"Token {self.token}"})
            response.raise_for_status()
            tenders += response.json()["results"]
            next_url = response.json()["next"]
        return tenders


def get_domain(tender_data):
    try:
        # NOTE(vperron): I know this does not respect the RFC.
        # Let's hope it is good enough for now.
        raw_domain = tender_data["author_email"].split("@")[1]
        if raw_domain:
            if raw_domain not in BANNED_DOMAINS:
                domain, _ = DomainSirenAssociation.objects.get_or_create(domain=raw_domain)
                return domain
    except KeyError:
        print(f"! {tender_data=} had no author_email")
    except IndexError:
        print(f"! {tender_data["author_email"]=} had no domain")
    return None


class Command(BaseCommand):
    help = "Synchronizes data from Le Marche Datacube Tenders API to our system"

    def handle(self, **options):
        le_marche_client = LeMarcheClient(
            base_url=settings.LE_MARCHE_API_BASE_URL,
            token=settings.LE_MARCHE_API_TOKEN,
        )

        marche_api_data = le_marche_client.fetch_tenders()
        marche_db_objects = LeMarcheRawTender.objects.all()

        api_slugs = set(item["slug"] for item in marche_api_data)
        db_slugs = set(marche_db_objects.values_list("slug", flat=True))
        removed_in_api = db_slugs - api_slugs

        now = timezone.now()
        tenders = []
        for tender_data in marche_api_data:
            domain = get_domain(tender_data)
            tender = LeMarcheRawTender(
                slug=tender_data["slug"],
                data=tender_data,
                domain=domain,
                updated_at=now,
            )
            tenders.append(tender)

        LeMarcheRawTender.objects.bulk_create(
            tenders,
            update_conflicts=True,
            update_fields=("data", "updated_at"),
            unique_fields=("slug",),
        )
        self.stdout.write(f"len={len(tenders)} Marche Tender entries have been created or updated.")
        LeMarcheRawTender.objects.filter(slug__in=removed_in_api).delete()
        self.stdout.write(f"len={len(removed_in_api)} Marche Tender entries have deleted")
