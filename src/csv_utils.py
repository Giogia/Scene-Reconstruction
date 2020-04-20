import csv
from ast import literal_eval


def read_csv(file, field=None, row_number=0):
    reader = csv.reader(open(file))

    data = []
    for row in reader:
        data.append([literal_eval(elem) for elem in row])

    return data


def csv_setup(file, header=None):

    writer = csv.writer(file)

    if header is not None:
        writer.writerow(header)

    return writer
