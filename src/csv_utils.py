import csv
from ast import literal_eval


def read_csv(file, field, row_number=0):
    reader = csv.DictReader(open(file))
    row = list(reader)[row_number]

    return literal_eval(row[field])


def csv_setup(file, header):
    writer = csv.writer(file)
    writer.writerow(header)

    return writer
