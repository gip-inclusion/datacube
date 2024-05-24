import httpx
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from furl import furl
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed
from tenacity.wait import wait_base

from spock.company_score.models import DomainSirenAssociation, IFRawConvention, ScoredCompany


class retry_if_http_429_error(retry_if_exception):
    def __init__(self):
        def is_http_429_error(exception):
            return isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code == 429

        super().__init__(predicate=is_http_429_error)


class wait_for_retry_after_header(wait_base):
    def __init__(self, fallback):
        self.fallback = fallback

    def __call__(self, retry_state):
        exc = retry_state.outcome.exception()
        if isinstance(exc, httpx.HTTPStatusError):
            retry_after = exc.response.headers.get("Retry-After")
            try:
                return int(retry_after)
            except (TypeError, ValueError):
                pass
        return self.fallback(retry_state)


@retry(
    retry=retry_if_http_429_error(),
    wait=wait_for_retry_after_header(fallback=wait_fixed(1)),
    stop=stop_after_attempt(3),
)
def fetch_company(siren):
    f = furl(settings.API_ENTREPRISE_BASE_URL)
    f.path /= "search"
    f.add({"q": siren})
    response = httpx.get(f.url)
    response.raise_for_status()
    data = response.json()

    if data["total_results"] == 0:
        # FIXME(vperron): Ce cas devrait etre enregistré dans les erreurs sur le modèle ?
        print(f"! api_entreprise {siren=} not found")
        return None
    elif data["total_results"] > 1:
        # Never happened.
        print(f"! api_entreprise {siren=} found multiple results")
        return None

    return data["results"][0]


class Command(BaseCommand):
    help = "Resolves SIREN to Company objects using API Enteprise"

    def add_arguments(self, parser):
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")

    def handle(self, *, wet_run, **options):
        now = timezone.now()
        marche_sirens = (
            DomainSirenAssociation.objects.exclude(siren=None)
            .exclude(siren="")
            .values_list("siren", flat=True)
            .distinct()
        )
        if_sirens = IFRawConvention.objects.all().values_list("siren", flat=True).distinct()
        sirens = set(marche_sirens) | set(if_sirens)
        known_sirens = set(ScoredCompany.objects.values_list("siren", flat=True))
        unknown_sirens = set(sirens) - known_sirens
        companies_to_create = []
        for siren in unknown_sirens:
            company_data = fetch_company(siren)
            if not company_data:
                continue

            self.stdout.write(f"> {siren=} resolved to name={company_data['nom_complet']}")
            companies_to_create.append(
                ScoredCompany(
                    siren=siren,
                    api_entreprise_data=company_data,
                    nom_complet=company_data["nom_complet"],
                    last_api_entreprise_at=now,
                )
            )

        if wet_run:
            ScoredCompany.objects.bulk_create(companies_to_create)

        # Now, resolve back the companies to their original objects
        pairings = list(DomainSirenAssociation.objects.filter(company=None))
        for pairing in pairings:
            company = ScoredCompany.objects.filter(siren=pairing.siren).first()
            if company:
                pairing.company = company
        if wet_run:
            DomainSirenAssociation.objects.bulk_update(pairings, ["company"])

        if_conventions = list(IFRawConvention.objects.filter(company=None))
        for convention in if_conventions:
            company = ScoredCompany.objects.filter(siren=convention.siren).first()
            if company:
                convention.company = company
        if wet_run:
            IFRawConvention.objects.bulk_update(if_conventions, ["company"])
