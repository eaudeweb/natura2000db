$(document).ready(function() {

    $('.search-results .map').each(function() {

        var map = new L.Map(this, {
            center: new L.LatLng(46, 25.0),
            zoom: 6,
            fadeAnimation: false
        });

        var osm_url = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        var osm = new L.TileLayer(osm_url, {maxZoom: 18});
        map.addLayer(osm);

        var layers = {
            sci: new L.GeoJSON(),
            spa: new L.GeoJSON()
        };
        R.layers = layers;

        map.addLayer(layers['sci']);
        map.addLayer(layers['spa']);

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

        function filter_features(features, keep) {
            return $.map(features, function(feature) {
                var sitecode = feature['properties']['SITECODE'];
                if(keep(sitecode)) {
                    return feature;
                }
            });
        }

    });

});
