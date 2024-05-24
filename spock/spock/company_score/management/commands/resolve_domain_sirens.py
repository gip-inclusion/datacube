from django.conf import settings
from django.core.management import BaseCommand

from spock.company_score.google import GoogleAPIClient
from spock.company_score.models import DomainSirenAssociation


class Command(BaseCommand):
    help = "Resolves domain names to SIRENs using Google API."

    def add_arguments(self, parser):
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--debug", dest="debug", action="store_true")

    def handle(self, *, wet_run, debug=False, **options):
        google_client = GoogleAPIClient(api_key=settings.SERPAPI_API_KEY, debug=debug)

        pairings = list(DomainSirenAssociation.objects.filter(siren=None))
        for pairing in pairings:
            try:
                pairing.siren = next(google_client.search_siret(pairing.domain))[:9]
                self.stdout.write(f"> resolved {pairing.domain=} to SIREN {pairing.siren=}")
            except StopIteration:
                continue

        if wet_run:
            DomainSirenAssociation.objects.bulk_update(pairings, ["siren"])
