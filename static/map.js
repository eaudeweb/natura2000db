$(document).ready(function() {

    $('.search-results .map').each(function() {
        var map = new L.Map(this, {
            center: new L.LatLng(46, 25.0),
            zoom: 6,
            fadeAnimation: false
        });

        var zoom_box = $('.leaflet-control-zoom').parent();
        zoom_box.removeClass('leaflet-left').addClass('leaflet-right');

        if(R.debug) {
            var circle = new L.CircleMarker(new L.LatLng(46, 25));
            map.addLayer(circle);
        }

        var legend = $('<div class="legend">');
        legend.appendTo($('.leaflet-control-container', this));

        var osm_url = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        var osm = new L.TileLayer(osm_url, {maxZoom: 18});
        map.addLayer(osm);

        function new_layer(options) {
            var layer = new L.GeoJSON();
            layer.features = [];
            $.extend(layer, options);

            layer.on('featureparse', function(e) {
                var name = e.properties['name'];
                var feature_layer = e.layer;
                feature_layer.name = name;
                layer.features.push(e.properties['_feature']);
                feature_layer.setStyle({
                    color: layer['color'],
                    weight: 2,
                    clickable: false
                });
            });

            map.addLayer(layer);
            return layer;
        }

        var layers = {
            judete: new_layer({color: '#888'}),
            sci: new_layer({color: '#b92'}),
            spa: new_layer({color: '#9b2'})
        };
        R.layers = layers;

        function features_at(latlng) {
            if(R.debug) { console.time(1); }
            var hit_list = [];
            $.each(layers, function(layer_name, layer) {
                $.each(layer.features, function(i, feature) {
                    if(hit_test(feature['geometry'], latlng)) {
                        hit_list.push({
                            feature: feature,
                            layer: layer
                        });
                    }
                });
            });
            if(R.debug) { console.timeEnd(1); }
            return hit_list;
        }

        function hit_list_html(hit_list, item_content) {
            if(! item_content) {
                item_content = function(feature) {
                    return feature['properties']['name'];
                }
            }
            var ul = $('<ul class="hit-list">');
            $.each(hit_list, function(i, hit) {
                var item = $('<li>').appendTo(ul);
                var sample = $('<div class="legend-sample">');
                sample.css({background: hit['layer']['color']});
                item.append(sample, item_content(hit['feature']))[0];
            });
            return ul;
        }

        map.on('mousemove', function(e) {
            legend.empty().append($('<span class="number coordinates">').text(
                float_repr(e.latlng.lat, 4) + ', ' +
                float_repr(e.latlng.lng, 4)
            ));

            var hit_list = features_at(e.latlng);
            if(hit_list.length > 0) {
                legend.append(hit_list_html(hit_list));
            }

            if(R.debug) { circle.setLatLng(e.latlng); }
        });

        map.on('click', function(e) {
            var hit_list = features_at(e.latlng);
            if(hit_list.length > 0) {
                var popup = new L.Popup();
                popup.setLatLng(e.latlng);
                popup.setContent(hit_list_html(hit_list, linkify)[0]);
                map.openPopup(popup);
            }
        });

        function linkify(feature) {
            var url = feature['properties']['url'];
            var label = feature['properties']['name'];
            if(url) {
                return $('<a>').attr('href', url).text(label);
            }
            else {
                return label;
            }
        }

        function process_geometry(feature) {
            feature['properties']['_feature'] = feature;
            feature['geometry']['bbox'] = bounding_box(feature['geometry']);
        }

        var site_data_map = {};
        var sitecode_hash = {};
        var sitename = {};
        var site_url = {};
        $('.search-results .sitecode').each(function() {
            var code = $(this).text();
            var a = $(this).parent('li').children('a.sitename')
            site_data_map[code] = {
                'name': a.text(),
                'url': a.attr('href')
            }
        });
        var keep = function(code) { return site_data_map.hasOwnProperty(code); };

        function add_site_features(features, layer) {
            $.each(features, function(i, feature) {
                var sitecode = feature['properties']['SITECODE'];
                if(! keep(sitecode)) { return; }
                var site_data = site_data_map[sitecode];
                feature['properties']['name'] = site_data['name'];
                feature['properties']['url'] = site_data['url'];
                process_geometry(feature);
                layer.addGeoJSON(feature);
            });
        }

        $.getJSON(R.assets + 'sci-wgs84.geojson', function(data) {
            add_site_features(data['features'], layers['sci']);
        });

        $.getJSON(R.assets + 'spa-wgs84.geojson', function(data) {
            add_site_features(data['features'], layers['spa']);
        });

        $.getJSON(R.assets + 'judete-wgs84.geojson', function(data) {
            var layer = layers['judete'];
            $.each(data['features'], function(i, feature) {
                var name = feature['properties']['denjud'];
                name = name[0] + name.slice(1).toLowerCase();
                process_geometry(feature);
                feature['properties']['name'] = name;
                layer.addGeoJSON(feature);
            });
            layer.setStyle({
                color: layer['color'],
                weight: 2
            });
        });

    });





    function bounding_box(geometry) {
        if(geometry['type'] == 'Polygon') {
            return bounding_box_polygon(geometry['coordinates'][0]);
        }

        if(geometry['type'] == 'MultiPolygon') {
            return bounding_box_multipolygon(geometry['coordinates']);
        }
    }

    function bounding_box_polygon(ring) {
        var lng_list = $.map(ring, function(lnglat) { return lnglat[0]; });
        var lat_list = $.map(ring, function(lnglat) { return lnglat[1]; });
        return [
            Math.min.apply(null, lng_list),
            Math.min.apply(null, lat_list),
            Math.max.apply(null, lng_list),
            Math.max.apply(null, lat_list)
        ];
    }

    function bounding_box_multipolygon(coordinates) {
        var boxes = $.map(coordinates, function(poly_coords) {
            return [bounding_box_polygon(poly_coords[0])];
        });
        function extract(list, name) {
            return $.map(list, function(dic) { return dic[name]; });
        }
        return [
            Math.min.apply(null, extract(boxes, 0)),
            Math.min.apply(null, extract(boxes, 1)),
            Math.max.apply(null, extract(boxes, 2)),
            Math.max.apply(null, extract(boxes, 3))
        ];
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
        if(! point_in_box(latlng, geometry['bbox'])) {
            return false;
        }
        if(geometry['type'] == 'Polygon') {
            return hit_test_polygon(geometry['coordinates'], latlng);
        }
        if(geometry['type'] == 'MultiPolygon') {
            return hit_test_multipolygon(geometry['coordinates'], latlng);
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

    function hit_test_multipolygon(coordinates, latlng) {
        for(var c = 0; c < coordinates.length; c ++) {
            if(hit_test_polygon(coordinates[c], latlng)) {
                return true;
            }
        }
        return false;
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
