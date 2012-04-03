(function() {


var map;


function map_coord(value) {
    map.getProjectionObject()
    var wgs84 = new OpenLayers.Projection("EPSG:4326");
    var map_proj = map.getProjectionObject();
    return value.transform(wgs84, map_proj);
}


function setup_map(map_div_id) {
    window.map = map = new OpenLayers.Map(map_div_id);

    osm_layer = new OpenLayers.Layer.OSM("OpenStreetMap");

    map.addLayer(osm_layer);
    map.setCenter(map_coord(new OpenLayers.LonLat(25, 46)), 7);
}


$(function() {
    var map_div = $('<div id="tinygis-map">').appendTo($('body'));
    setup_map('tinygis-map');
});


})();
