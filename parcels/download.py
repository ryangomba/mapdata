import os
import csv
import json
import zipfile
import subprocess
import urllib.request

script_dir = os.path.dirname(os.path.realpath(__file__))

# download

print('Downloading...')
url = 'http://egis3.lacounty.gov/dataportal/wp-content/uploads/ShapefilePackages/Parcels_CA_2014.zip'
zip_path = os.path.join(script_dir, 'parcels.zip')
urllib.request.urlretrieve(url, zip_path)

print('Unzipping...')
zip_ref = zipfile.ZipFile(zip_path, 'r')
zip_ref.extractall(script_dir)
zip_ref.close()
os.remove(zip_path)

print ('Moving...')
gdb_download_dir = os.path.join(script_dir, 'Parcels_CA_2014.gdb')
gdb_dir = os.path.join(script_dir, 'gdb')
os.rename(gdb_download_dir, gdb_dir)

# load
# TODO load into PostGIS

# extract

with open('counties.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row['name']
        dirname = name.replace(' ', '-').lower()

        print('Extracting %s...' % name)
        json_dir = os.path.join(script_dir, 'geojson', dirname)
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, 'parcels.geo.json')
        if os.path.exists(json_path): os.remove(json_path)
        call = [
            'ogr2ogr',
            '-f','GeoJSON',
            '-t_srs', 'crs:84',
            json_path,
            'PG:"host=localhost dbname=foo"',
            '-sql', '"select parno, wkb_geometry from ca_parcels_statewide where county = \'%s\'"' % name
        ]
        subprocess.check_call([' '.join(call)], shell=True)

        info = {
            "name": name,
            "downloaded": "2018/02/01",
            "source": "https://egis3.lacounty.gov/dataportal/2015/09/11/california-statewide-parcel-boundaries",
            "id_key": "parno"
        }
        info_path = os.path.join(json_dir, 'info.json')
        with open(info_path, 'w') as infofile:
            json.dump(info, infofile, indent=4)
