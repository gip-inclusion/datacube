from django.core.management import BaseCommand

from spock.company_score.models import ScoredCompany


class Command(BaseCommand):
    help = "Computes a denormalized Score for every ScoredCompany."

    def add_arguments(self, parser):
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")

    def handle(self, *, wet_run, debug=False, **options):
        companies = list(ScoredCompany.objects.all())
        for company in companies:
            company.tender_count = company.get_tender_count()
            company.tender_amount = company.get_tender_amount()
            company.conventions_count = company.get_conventions_count()
            company.score = company.get_score()

        if wet_run:
            ScoredCompany.objects.bulk_update(
                companies, ["tender_count", "tender_amount", "conventions_count", "score"], batch_size=1000
            )
