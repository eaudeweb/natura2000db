$(document).ready(function() {

    var advanced = 'search-advanced-visible';
    var cookie_name = 'chm-rio-advanced-search';

    $('.search-toggle').click(function(evt) {
        evt.preventDefault();
        toggle_advanced_search();
    });

    if($.cookie(cookie_name)) {
        toggle_advanced_search();
    }

    function advanced_on() {
        return $('.search-criteria').hasClass(advanced);
    }

    function toggle_advanced_search() {
        $('.search-criteria').toggleClass(advanced);
        var cookie_value = advanced_on() ? 'on' : null;
        $.cookie(cookie_name, cookie_value, {expires: 1});
    }

    $('form[name=search]').submit(function(evt) {
        if(! advanced_on()) {
            // clear advanced search inputs
            $('.search-advanced :input').val(null);
        }
    });

    $('#search-results-map').each(function() {

        var map = new L.Map(this, {
            center: new L.LatLng(46, 25.0),
            zoom: 6
        });

        var osm_url = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        var osm = new L.TileLayer(osm_url, {maxZoom: 18});
        map.addLayer(osm);

        var shapes = new L.GeoJSON();
        map.addLayer(shapes);

        $.getJSON(R.assets + 'sci-wgs84.geojson', function(data) {
            shapes.addGeoJSON(data);
        });

        $.getJSON(R.assets + 'spa-wgs84.geojson', function(data) {
            shapes.addGeoJSON(data);
        });

    });

});
