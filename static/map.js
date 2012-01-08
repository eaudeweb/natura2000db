$(document).ready(function() {

    $('.search-results .map').each(function() {
        var map = new L.Map(this, {
            center: new L.LatLng(46, 25.0),
            zoom: 6,
            fadeAnimation: false
        });

        if(R.debug) {
            var circle = new L.CircleMarker(new L.LatLng(46, 25));
            map.addLayer(circle);
        }

        var legend = $('<div class="legend">');
        legend.appendTo($('.leaflet-control-container', this));

        var osm_url = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        var osm = new L.TileLayer(osm_url, {maxZoom: 18});
        map.addLayer(osm);

        function new_layer() {
            var layer = new L.GeoJSON();
            layer.geometries = {};

            layer.on('featureparse', function(e) {
                var sitecode = e.properties['SITECODE'];
                e.layer.sitecode = sitecode;
                layer.geometries[sitecode] = e.properties['_geometry'];
            });

            map.addLayer(layer);
            return layer;
        }

        var layers = {
            sci: new_layer(),
            spa: new_layer()
        };
        R.layers = layers;

        map.on('mousemove', function(e) {
            if(R.debug) { console.time(1); }
            var hit = [];
            $.each(layers, function(layer_name, layer) {
                $.each(layer.geometries, function(sitecode, geometry) {
                    //if(sitecode != 'ROSPA0076') return;
                    if(hit_test(geometry, e.latlng)) {
                        hit.push(sitecode);
                    }
                });
            });
            if(R.debug) { console.timeEnd(1); }

            legend.empty().append($('<span class="number">').text(
                float_repr(e.latlng.lat, 4) + ', ' +
                float_repr(e.latlng.lng, 4)
            ));

            if(hit.length > 0) {
                $('<ul>').appendTo(legend).append($.map(hit, function(code) {
                    return $('<li>').text(code)[0];
                }));
            }
            if(R.debug) { circle.setLatLng(e.latlng); }
        });

        var sitecode_hash = {};
        $('.search-results .sitecode').each(function() {
            var code = $(this).text();
            sitecode_hash[code] = true;
        });
        var keep = function(code) { return sitecode_hash[code]; };

        $.getJSON(R.assets + 'sci-wgs84.geojson', function(data) {
            data['features'] = filter_features(data['features'], keep);
            layers['sci'].addGeoJSON(data);
            layers['sci'].setStyle({
                color: '#b92',
                weight: 2
            });
        });

        $.getJSON(R.assets + 'spa-wgs84.geojson', function(data) {
            data['features'] = filter_features(data['features'], keep);
            layers['spa'].addGeoJSON(data);
            layers['spa'].setStyle({
                color: '#9b2',
                weight: 2
            });
        });

        function process_geometry(feature) {
            feature['properties']['_geometry'] = feature['geometry'];
            feature['geometry']['bbox'] = bounding_box(feature['geometry']);
        }

        function filter_features(features, keep) {
            return $.map(features, function(feature) {
                var sitecode = feature['properties']['SITECODE'];
                if(keep(sitecode)) {
                    process_geometry(feature);
                    return feature;
                }
            });
        }

    });





    function bounding_box(geometry) {
        if(geometry['type'] == 'Polygon') {
            var ring = geometry['coordinates'][0];
            var lng_list = $.map(ring, function(lnglat) { return lnglat[0]; });
            var lat_list = $.map(ring, function(lnglat) { return lnglat[1]; });
            return [
                Math.min.apply(null, lng_list),
                Math.min.apply(null, lat_list),
                Math.max.apply(null, lng_list),
                Math.max.apply(null, lat_list)
            ];
        }
    }

    function point_in_box(latlng, bbox) {
        if(! bbox)
            return true;
        if(latlng.lng < bbox[0] || latlng.lng > bbox[2])
            return false;
        if(latlng.lat < bbox[1] || latlng.lat > bbox[3])
            return false;
        return true;
    }

    function hit_test(geometry, latlng) {
        // TODO multipolygon
        if(! point_in_box(latlng, geometry['bbox'])) {
            return false;
        }
        if(geometry['type'] == 'Polygon') {
            return hit_test_polygon(geometry['coordinates'], latlng);
        }
        return false;
    }

    function float_repr(value, digits) {
        var str = '';
        if(value < 0) {
            str += '-';
            value = -value;
        }

        consume();
        str += '.';
        while(digits) {
            consume();
            digits -= 1;
        }
        return str;

        function consume() {
            var f = Math.floor(value)
            str += f;
            value -= f;
            value *= 10;
        }
    }



/* Copyright (c) 2006-2012 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the Clear BSD license.  
 * See http://svn.openlayers.org/trunk/openlayers/license.txt for the
 * full text of the license. */

    function hit_test_polygon(coordinates, latlng) {
        var numRings = coordinates.length;
        var contained = false;
        if(numRings > 0) {
            // check exterior ring - 1 means on edge, boolean otherwise
            contained = hit_test_ring(coordinates[0], latlng);
            if(contained !== 1) {
                if(contained && numRings > 1) {
                    // check interior rings
                    var hole;
                    for(var i=1; i<numRings; ++i) {
                        hole = hit_test_ring(coordinates[i], latlng);
                        if(hole) {
                            if(hole === 1) {
                                // on edge
                                contained = 1;
                            } else {
                                // in hole
                                contained = false;
                            }
                            break;
                        }
                    }
                }
            }
        }
        return contained;
    }

    function hit_test_ring(ring, latlng) {
        var digs = 14;
        var px = approx(latlng.lng, digs);
        var py = approx(latlng.lat, digs);
        function getX(y, x1, y1, x2, y2) {
            return (((x1 - x2) * y) + ((x2 * y1) - (x1 * y2))) / (y1 - y2);
        }
        var numSeg = ring.length - 1;
        var start, end, x1, y1, x2, y2, cx, cy;
        var crosses = 0;
        for(var i=0; i<numSeg; ++i) {
            start = ring[i];
            x1 = approx(start[0], digs);
            y1 = approx(start[1], digs);
            end = ring[i + 1];
            x2 = approx(end[0], digs);
            y2 = approx(end[1], digs);

            /**
             * The following conditions enforce five edge-crossing rules:
             *    1. points coincident with edges are considered contained;
             *    2. an upward edge includes its starting endpoint, and
             *    excludes its final endpoint;
             *    3. a downward edge excludes its starting endpoint, and
             *    includes its final endpoint;
             *    4. horizontal edges are excluded; and
             *    5. the edge-ray intersection point must be strictly right
             *    of the point P.
             */
            if(y1 == y2) {
                // horizontal edge
                if(py == y1) {
                    // point on horizontal line
                    if(x1 <= x2 && (px >= x1 && px <= x2) || // right or vert
                       x1 >= x2 && (px <= x1 && px >= x2)) { // left or vert
                        // point on edge
                        crosses = -1;
                        break;
                    }
                }
                // ignore other horizontal edges
                continue;
            }
            cx = approx(getX(py, x1, y1, x2, y2), digs);
            if(cx == px) {
                // point on line
                if(y1 < y2 && (py >= y1 && py <= y2) || // upward
                   y1 > y2 && (py <= y1 && py >= y2)) { // downward
                    // point on edge
                    crosses = -1;
                    break;
                }
            }
            if(cx <= px) {
                // no crossing to the right
                continue;
            }
            if(x1 != x2 && (cx < Math.min(x1, x2) || cx > Math.max(x1, x2))) {
                // no crossing
                continue;
            }
            if(y1 < y2 && (py >= y1 && py < y2) || // upward
               y1 > y2 && (py < y1 && py >= y2)) { // downward
                ++crosses;
            }
        }
        var contained = (crosses == -1) ?
            // on edge
            1 :
            // even (out) or odd (in)
            !!(crosses & 1);

        return contained;
    }

    function approx(num, sig) {
        var fig = 0;
        if (sig > 0) {
            fig = parseFloat(num.toPrecision(sig));
        }
        return fig;
    }

});
