import csv
from collections import defaultdict

from django.core.management import BaseCommand

from spock.company_score.models import IFRawConvention


def line_reader(f):
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for line in reader:
        yield line


# FIXME(vperron) : Very naive for now.
class Command(BaseCommand):
    help = "Reads IF conventions from a CSV file. Later, get them from an API."

    def add_arguments(self, parser):
        parser.add_argument("input_csv", type=open)

    def handle(self, input_csv, **options):
        # Clear the conventions first.
        IFRawConvention.objects.all().delete()

        conventions_by_siren = defaultdict(int)
        for siret, _, nb_conventions in line_reader(input_csv):
            conventions_by_siren[siret[:9]] += int(nb_conventions)

        conventions = []
        for siren, nb_conventions in conventions_by_siren.items():
            conventions.append(IFRawConvention(siren=siren, nb_conventions=nb_conventions))
        IFRawConvention.objects.bulk_create(conventions)
