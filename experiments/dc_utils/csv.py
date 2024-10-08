import csv
import sys


def line_reader(filename):
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for line in reader:
            yield line


writer = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)

dict_writer = csv.DictWriter(sys.stdout, quoting=csv.QUOTE_NONNUMERIC, fieldnames=None)
