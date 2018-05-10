import os
import csv
import zipfile
import subprocess
import urllib.request

script_dir = os.path.dirname(os.path.realpath(__file__))

shps_dir = os.path.join(script_dir, 'shp')
if not os.path.exists(shps_dir):
    os.mkdir(shps_dir)

with open('counties.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id = row['id']
        name = row['name']
        dirname = name.replace(' ', '-').lower()

        print('Downloading %s...' % name)
        url = 'https://www2.census.gov/geo/tiger/TIGER2017/ROADS/tl_2017_%s_roads.zip' % id
        zip_path = os.path.join(shps_dir, dirname + '.zip')
        urllib.request.urlretrieve(url, zip_path)

        print('Unzipping %s...' % name)
        shp_dir = os.path.join(shps_dir, dirname)
        zip_ref = zipfile.ZipFile(zip_path, 'r')
        zip_ref.extractall(shp_dir)
        zip_ref.close()
        os.remove(zip_path)

        print('Extracting %s...' % name)
        shp_path = os.path.join(shp_dir, list(filter(lambda path: path.endswith('.shp'), os.listdir(shp_dir)))[0])
        json_dir = os.path.join(script_dir, 'geojson', dirname)
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, 'streets.geo.json')
        if os.path.exists(json_path): os.remove(json_path)
        subprocess.check_call([
            'ogr2ogr',
            '-f', 'GeoJSON',
            '-t_srs', 'crs:84',
            json_path,
            shp_path
        ])
