(function() {


TG.load_templates = function() {
    TG.templates = {};
    $('.template-src').each(function() {
        var name = $(this).attr('data-name');
        var template = _.template($(this).text());
        TG.templates[name] = template;
    });
};


TG.MapLayerCollection = Backbone.Collection.extend();


TG.Layer = Backbone.Model.extend();


TG.MapLayer = Backbone.View.extend({
    initialize: function(options) {
        this.olLayer = options['olLayer'];
        this.olLayer.events.register('visibilitychanged',
                                     this, this.mapUpdateVisibility);
        this.mapUpdateVisibility();
        this.model.on('change:visible', this.modelUpdateVisibility, this);
    },

    modelUpdateVisibility: function(model, visible) {
        if(this.olLayer.isBaseLayer) {
            if(visible) {
                this.olLayer.map.setBaseLayer(this.olLayer);
            }
        }
        else {
            this.olLayer.setVisibility(visible);
        }
    },

    mapUpdateVisibility: function(options) {
        this.model.set('visible', this.olLayer.visibility);
    }
});


TG.Map = Backbone.View.extend({

    tagName: 'div',
    id: 'tinygis-map',

    initialize: function() {
        this.parent = this.options['parent'];
        this.$el.prependTo(this.parent);
        this.olMap = new OpenLayers.Map(this.el.id);

        this.baseLayerCollection = new TG.MapLayerCollection;
        this.overlayCollection = new TG.MapLayerCollection;
        this.olMap.events.register('addlayer', this, this.layerAdded);

        var osm_layer = new OpenLayers.Layer.OSM("OpenStreetMap");
        this.olMap.addLayer(osm_layer);
        this.olMap.setCenter(this.project(new OpenLayers.LonLat(25, 46)), 7);

        this.olMap.events.register("mousemove", this, function(e) {
            lonLat = this.invproject(this.olMap.getLonLatFromPixel(e.xy));
            this.trigger("mousemove", {lng: lonLat.lon, lat: lonLat.lat});
        });
    },

    layerAdded: function(evt) {
        var olLayer = evt.layer;
        var collection = (olLayer.isBaseLayer
                          ? this.baseLayerCollection
                          : this.overlayCollection);
        var layer = collection.get(olLayer.id);
        if(layer === undefined) {
            layer = new TG.Layer({
                id: olLayer.id,
                name: olLayer.name
            });
        }
        var mapLayer = new TG.MapLayer({model: layer, olLayer: olLayer});
        collection.add(layer);
    },

    updateSize: function() {
        this.olMap.updateSize();
    },

    project: function(value) {
        var wgs84 = new OpenLayers.Projection("EPSG:4326");
        var map_proj = this.olMap.getProjectionObject();
        return value.transform(wgs84, map_proj);
    },

    invproject: function(value) {
        var wgs84 = new OpenLayers.Projection("EPSG:4326");
        var map_proj = this.olMap.getProjectionObject();
        return value.transform(map_proj, wgs84);
    },

    addOverlay: function(olLayer, options) {
        if(options === undefined) { options = {}; }
        if(options['model'] !== undefined) {
            this.overlayCollection.add(options['model'], options);
        }
        this.olMap.addLayer(olLayer);
    },

    addBingLayers: function(bingKey) {
        var road = new OpenLayers.Layer.Bing({
            name: "Bing Road",
            key: bingKey,
            type: "Road"
        });
        var hybrid = new OpenLayers.Layer.Bing({
            name: "Bing Hybrid",
            key: bingKey,
            type: "AerialWithLabels"
        });
        var aerial = new OpenLayers.Layer.Bing({
            name: "Bing Aerial",
            key: bingKey,
            type: "Aerial"
        });
        this.olMap.addLayers([road, hybrid, aerial]);
    },

    addGoogleLayers: function() {
        var gsat = new OpenLayers.Layer.Google("Google Satellite", {
            type: google.maps.MapTypeId.SATELLITE,
            animationEnabled: false,
            numZoomLevels: 22
        });
        var gphy = new OpenLayers.Layer.Google("Google Physical", {
            type: google.maps.MapTypeId.TERRAIN,
            animationEnabled: false
        });
        var gmap = new OpenLayers.Layer.Google("Google Streets", {
            animationEnabled: false,
            numZoomLevels: 20
        });
        var ghyb = new OpenLayers.Layer.Google("Google Hybrid", {
            type: google.maps.MapTypeId.HYBRID,
            animationEnabled: false,
            numZoomLevels: 22
        });
        this.olMap.addLayers([gsat, gphy, gmap, ghyb]);
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

})();
