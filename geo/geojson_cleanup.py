# ogr2ogr -s_srs 'EPSG:31700' -t_srs 'WGS84' -simplify 50 -f geojson geojson-layers/sci-2011.geojson shapes/sci-spa-2011/sci.shp
# ogr2ogr -s_srs 'EPSG:31700' -t_srs 'WGS84' -simplify 50 -f geojson geojson-layers/spa-2011.geojson shapes/sci-spa-2011/spa.shp

Q=10**6
def quantize(coord):
  for i, v in enumerate(coord):
    if isinstance(v, list):
      quantize(v)
    else:
      coord[i] = float(int(v*Q))/Q

for f in sci['features']:
  quantize(f['geometry']['coordinates'])
  p = f['properties']
  f['properties'] = {'name': p['SITE_NAME'], 'id': p['SITECODE']}
