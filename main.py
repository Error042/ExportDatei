import click
import os
import json
import csv
import pandas as pd
from datetime import datetime

# The function for handling the transformation process | crfile = create file
def crfile(fp, fn):
    with open(fp) as f:
        j = json.load(f)

    vals = [{**jj["values"], **{"ts": jj["ts"]}} for jj in j["data"]]
    handy_id = j["id"]

    counts = {}
    for v in vals:
        for k in v:
            counts[k] = counts.get(k, 0) + 1

    with open(f"{fn}-{handy_id}.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([c for c in counts])
        for v in vals:
            writer.writerow([v.get(c) for c in counts])
    return f"{fn}-{handy_id}.csv"


def tsrange(dfhead):
    startms = dfhead['ts'].iloc[0]
    endms = dfhead['ts'].iloc[-1]

    startdt = str(datetime.fromtimestamp(startms/1000).isoformat(sep=' '))
    enddt = str(datetime.fromtimestamp(endms/1000).isoformat(sep=' '))

    startdt = startdt[:-3]
    enddt = enddt[:-3]

    string = startdt + ' to: ' + enddt
    return string


@click.command()
@click.argument('path')
@click.option('--fname', type=str, help='This is a test.', default='export')
def main(path, fname):
    click.echo()
    if os.path.isfile(path):
        df = pd.read_csv(crfile(path, fname), sep=';')
        click.echo("Number of rows present: " + str(len(df)))
        click.echo("Timestamp from: " + tsrange(df))

    else:
        files = [g for g in os.listdir(path)]
        for i in files:
            df = pd.read_csv(crfile((path + i), os.path.splitext(i)[0]))
            click.echo("Number of rows present: " + str(len(df)))
            click.echo()


if __name__ == '__main__':
    main()
