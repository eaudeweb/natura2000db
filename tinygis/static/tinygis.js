(function() {


window.TG = {};


TG.load_templates = function() {
    TG.templates = {};
    $('.template-src').each(function() {
        var name = $(this).attr('data-name');
        var template = _.template($(this).text());
        TG.templates[name] = template;
    });
};


var Map = Backbone.View.extend({

    tagName: 'div',
    id: 'tinygis-map',

    initialize: function() {
        this.parent = this.options['parent'];
        this.$el.prependTo(this.parent);
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


TG.Identify = Backbone.Model.extend({

    initialize: function() {
        this._pending = false;
        this._in_flight = false;
    },

    updateCoordinates: function(coords) {
        this.set(coords);
        this._next_coords = coords;
        this._pending = true;
        this._tick();
    },

    _tick: function() {
        if(this._in_flight) { return; }
        if(! this._pending) { return; }
        this._in_flight = true;
        this._pending = false;
        this.trigger('update-start');
        $.ajax({
            url: 'get_features_at',
            data: {lat: this.get('lat'), lng: this.get('lng')},
            context: this
        }).done(function(data) {
            this.set(_.extend({error: false}, data));
            this.trigger('change');
        }).fail(function() {
            this.set({error: true, hit_list: []});
            this.trigger('change');
            this.trigger('update-error');
        }).always(function() {
            this._in_flight = false;
            this.trigger('update-end');
            this._tick();
        });
    }

});


TG.IdentifyView = Backbone.View.extend({
    tagName: 'div',
    className: 'identify',
    templateName: 'identify',

    initialize: function() {
        this.model.on('change', this.render, this);
        this.model.on('update-start', function() {
            this.$el.addClass('update-in-progress');
        }, this);
        this.model.on('update-end', function() {
            this.$el.removeClass('update-in-progress');
        }, this);
    },

    render: function() {
        var template = TG.templates[this.templateName];
        this.$el.html(template(this.model.attributes));
    }

});


$(function() {
    TG.load_templates();

    TG.map = new Map({parent: $('body')[0]});
    TG.map.addLayer(new TG.TileLayer({
        name: "SCI + SPA",
        url_template: '/static/tiles/all-sites/${z}/${x}/${y}.png'
    }));

    TG.identify = new TG.Identify;
    TG.map.on("mousemove", TG.identify.updateCoordinates,
                           TG.identify);

    TG.identifyView = new TG.IdentifyView({model: TG.identify});
    TG.identifyView.$el.appendTo($('body'));
});


})();
