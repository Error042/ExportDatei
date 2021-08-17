# this script is used for changing 1 file or a whole folder from a .txt file (.json writing) to a usable .csv file
# also it creates a map of the location_latitude and location_longitude colums in the .csv

import click
import os
import json
import csv
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt


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

    with open(f"files/output/{fn}-{handy_id}.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([c for c in counts])
        for v in vals:
            writer.writerow([v.get(c) for c in counts])
    return f"{fn}-{handy_id}.csv"


# changes the timestemp to daytime for readability in the terminal. Does not change the Value in the .csv file
# tsrange = timestemp range
def tsrange(dfhead):
    startms = dfhead['ts'].iloc[0]
    endms = dfhead['ts'].iloc[-1]

    startdt = str(datetime.fromtimestamp(startms/1000).isoformat(sep=' '))
    enddt = str(datetime.fromtimestamp(endms/1000).isoformat(sep=' '))

    startdt = startdt[:-3]
    enddt = enddt[:-3]

    string = startdt + ' to: ' + enddt
    return string


# counting the entries in a given collum. | coval = count values
def coval(input_df):
    collist = list(input_df)

    for i in collist:
        counter = 0

        for j in input_df[i]:
            if pd.notna(j):
                counter += 1
        click.echo(i + ' - ' + str(counter))


# creates map of the route taken as a .png file in ./files/img/output/ | crmap = create map
def crmap(dataframe,imgname):

    # creating variables to put in the coordinate system (CS) and creating a variable for the database file
    lon = [+ i for i in dataframe['location_longitude'] if pd.notna(i)]
    lat = [+ i for i in dataframe['location_latitude'] if pd.notna(i)]

    # creating the CS with the map.png in the background
    imgdata = plt.imread('./files/img/map/map.png')
    fig, ax = plt.subplots()
    ax.imshow(imgdata, extent=[12.25800, 12.47678, 51.27130, 51.40799])
    ax.set_aspect(1.0/ax.get_data_ratio(), adjustable='box')

    # placing the coordinates in the CS, labeling the axes and saving the .png
    plt.plot(lon, lat, color='red', marker='o')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    fig.savefig('./files/img/output/' + os.path.splitext(imgname)[0], dpi=fig.dpi)

    # if you want to show the final result on a plot do it with: plt.show()
    return 0


# module click used for a console application
@click.command()
@click.argument('path')
@click.option('--fname', type=str, help='Input a file name | Does not affect multiple files at this point', default='export')
# the main function handles the output of the file
def main(path, fname):
    click.echo()

    # creating one file
    if os.path.isfile(path):
        file = crfile(path, fname)
        click.secho(file, fg='green', bold=True)
        df = pd.read_csv('./files/output/' + file, sep=';')
        crmap(df, file) if 'location_latitude' in df.columns else click.secho('No location data in file.', fg='red')
        click.echo("Number of rows present: " + str(len(df)))
        click.echo("Timestamp from: " + tsrange(df))
        coval(df)
        click.echo()

    # using the whole folder
    else:
        files = [g for g in os.listdir(path)]
        for i in files:
            file = crfile((path + i), os.path.splitext(i)[0])
            click.secho(file, fg='green', bold=True)
            df = pd.read_csv('./files/output/' + file, sep=';')
            crmap(df, file) if 'location_latitude' in df.columns else click.secho('No location data in file.', fg='red')
            click.echo("Number of rows present: " + str(len(df)))
            click.echo("Timestamp from: " + tsrange(df))
            coval(df)
            click.echo()


if __name__ == '__main__':
    main()
