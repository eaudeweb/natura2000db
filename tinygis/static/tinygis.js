(function() {


window.TG = {};


var Map = Backbone.View.extend({

    tagName: 'div',
    id: 'tinygis-map',

    initialize: function() {
        this.parent = this.options['parent'];
        this.$el.appendTo(this.parent);
        this.map = new OpenLayers.Map(this.el.id);
        var osm_layer = new OpenLayers.Layer.OSM("OpenStreetMap");
        this.map.addLayer(osm_layer);
        this.map.setCenter(this.project(new OpenLayers.LonLat(25, 46)), 7);

        this.map.events.register("mousemove", this, function(e) {
            lonLat = this.invproject(this.map.getLonLatFromPixel(e.xy));
            this.trigger("mousemove", {lng: lonLat.lon, lat: lonLat.lat});
        });
    },

    project: function(value) {
        var wgs84 = new OpenLayers.Projection("EPSG:4326");
        var map_proj = this.map.getProjectionObject();
        return value.transform(wgs84, map_proj);
    },

    invproject: function(value) {
        var wgs84 = new OpenLayers.Projection("EPSG:4326");
        var map_proj = this.map.getProjectionObject();
        return value.transform(map_proj, wgs84);
    },

    addLayer: function(layer) {
        this.map.addLayer(layer.olLayer);
    }

});


TG.TileLayer = Backbone.Model.extend({
    initialize: function() {
        this.olLayer = new OpenLayers.Layer.XYZ(
            this.attributes.name,
            this.attributes.url_template,
            {
                isBaseLayer: false,
                sphericalMercator: true
            }
        );
    }
});


$(function() {
    TG.map = new Map({parent: $('body')[0]});
    TG.map.addLayer(new TG.TileLayer({
        name: "SCI + SPA",
        url_template: '/static/tiles/all-sites/${z}/${x}/${y}.png'
    }));
});


})();
