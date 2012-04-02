# geometry code ported from OpenLayers geometry code
# Copyright (c) 2006-2012 by OpenLayers Contributors
# http://svn.openlayers.org/trunk/openlayers/license.txt


def approx(num, sig):
    if sig > 0:
        power = 10**sig
        return float(int(num*power))/power
    else:
        return 0


def hit_test_ring(ring, latlng):
    digs = 14
    px = approx(latlng['lng'], digs)
    py = approx(latlng['lat'], digs)
    def getX(y, x1, y1, x2, y2):
        return (((x1 - x2) * y) + ((x2 * y1) - (x1 * y2))) / (y1 - y2)
    numSeg = len(ring) - 1
    crosses = 0
    for i in range(numSeg): # for(i=0; i<numSeg; ++i):
        start = ring[i]
        x1 = approx(start[0], digs)
        y1 = approx(start[1], digs)
        end = ring[i + 1]
        x2 = approx(end[0], digs)
        y2 = approx(end[1], digs)

        # The following conditions enforce five edge-crossing rules:
        #    1. points coincident with edges are considered contained;
        #    2. an upward edge includes its starting endpoint, and
        #    excludes its final endpoint;
        #    3. a downward edge excludes its starting endpoint, and
        #    includes its final endpoint;
        #    4. horizontal edges are excluded; and
        #    5. the edge-ray intersection point must be strictly right
        #    of the point P.

        if(y1 == y2):
            # horizontal edge
            if(py == y1):
                # point on horizontal line
                if(x1 <= x2 and (px >= x1 and px <= x2) or # right or vert
                   x1 >= x2 and (px <= x1 and px >= x2)): # left or vert
                    # point on edge
                    crosses = -1
                    break
            # ignore other horizontal edges
            continue
        cx = approx(getX(py, x1, y1, x2, y2), digs)
        if(cx == px):
            # point on line
            if(y1 < y2 and (py >= y1 and py <= y2) or # upward
               y1 > y2 and (py <= y1 and py >= y2)): # downward
                # point on edge
                crosses = -1
                break
        if(cx <= px):
            # no crossing to the right
            continue
        if(x1 != x2 and (cx < min([x1, x2]) or cx > max([x1, x2]))):
            # no crossing
            continue
        if(y1 < y2 and (py >= y1 and py < y2) or # upward
           y1 > y2 and (py < y1 and py >= y2)): # downward
            crosses += 1
    contained = (1 if (crosses == -1) else not not (crosses & 1))
    # var contained = (crosses == -1) ?
    #     // on edge
    #     1 :
    #     // even (out) or odd (in)
    #     !!(crosses & 1);

    return contained


def hit_test_polygon(coordinates, latlng):
    numRings = len(coordinates)
    contained = False
    if(numRings > 0):
        # check exterior ring - 1 means on edge, boolean otherwise
        contained = hit_test_ring(coordinates[0], latlng)
        if(contained !=1):
            if(contained and numRings > 1):
                # check interior rings
                for i in range(1, numRings): #for(i=1; i<numRings; ++i):
                    hole = hit_test_ring(coordinates[i], latlng)
                    if(hole):
                        if(hole == 1):
                            # on edge
                            contained = 1
                        else:
                            # in hole
                            contained = False
                        break
    return contained


def hit_test_multipolygon(coordinates, latlng):
    for coord in coordinates:
        if hit_test_polygon(coord, latlng):
            return True
    else:
        return False


def point_in_box(latlng, bbox):
    if not bbox:
        return True
    elif latlng['lng'] < bbox[0] or latlng['lng'] > bbox[2]:
        return False
    elif latlng['lat'] < bbox[1] or latlng['lat'] > bbox[3]:
        return False
    else:
        return True


def hit_test(geometry, latlng):
    if not point_in_box(latlng, geometry.get('bbox', None)):
        return False
    elif geometry['type'] == 'Polygon':
        return hit_test_polygon(geometry['coordinates'], latlng)
    elif geometry['type'] == 'MultiPolygon':
        return hit_test_multipolygon(geometry['coordinates'], latlng)
    else:
        return False

def bounding_box_polygon(ring):
    lng_list = [lnglat[0] for lnglat in ring]
    lat_list = [lnglat[1] for lnglat in ring]
    return [
        min(lng_list),
        min(lat_list),
        max(lng_list),
        max(lat_list),
    ]

def bounding_box_aggregate(boxes):
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]

def bounding_box_multipolygon(coordinates):
    return bounding_box_aggregate([bounding_box_polygon(poly_coords[0])
                                   for poly_coords in coordinates])

def bounding_box_features(features):
    return bounding_box_aggregate([feature['geometry']['bbox']
                                   for feature in features])

def bounding_box(geometry):
    if(geometry['type'] == 'Polygon'):
        return bounding_box_polygon(geometry['coordinates'][0])

    if(geometry['type'] == 'MultiPolygon'):
        return bounding_box_multipolygon(geometry['coordinates'])


_feature_name_map = {
    'sci': 'SITECODE',
    'spa': 'SITECODE',
    'judete': 'denjud',
    'parcuri': 'NUME',
    'rezervatii': 'DENUMIRE',
}


from flask import json
from path import path as ppath
layers = {}
for geojson_file in (ppath(__file__).parent/'static').listdir('*.geojson'):
    name = geojson_file.basename().split('-wgs84', 1)[0]
    name_prop = _feature_name_map[name]
    with open(geojson_file, 'rb') as f:
        layers[name] = json.load(f)

    for feature in layers[name]['features']:
        feature['geometry']['bbox'] = bounding_box(feature['geometry'])
        feature['properties']['name'] = feature['properties'].get(name_prop, "")


def features_at(latlng):
    for layer_name, layer in layers.items():
        for feature in layer['features']:
            feature_name = feature['properties']['name']
            if feature_name == 'ROSPA0076':
                print layer_name, feature_name
            if hit_test(feature['geometry'], latlng):
                yield {
                    'layer': layer_name,
                    'feature': feature_name,
                }
