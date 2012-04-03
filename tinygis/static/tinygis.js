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
    },

    project: function(value) {
        var wgs84 = new OpenLayers.Projection("EPSG:4326");
        var map_proj = this.map.getProjectionObject();
        return value.transform(wgs84, map_proj);
    }

});


$(function() {
    TG.map = new Map({parent: $('body')[0]});
});


})();
