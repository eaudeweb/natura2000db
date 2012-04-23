(function() {


_.mixin({
    startswith: function(obj) {
        if(! _.isString(obj)) return false;
        for(var c = 1; c < arguments.length; c++) {
            var prefix = arguments[c];
            if(_.isString(prefix) &&
               obj.slice(0, prefix.length) == prefix) {
                return true;
            }
        }
        return false;
    }
});


TG.load_templates = function() {
    TG.templates = {};
    $('.template-src').each(function() {
        var name = $(this).attr('data-name');
        var template = _.template($(this).html());
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

        var osm_layer = new OpenLayers.Layer.OSM("OpenStreetMap");
        this.olMap.addLayer(osm_layer);
        this.trackLayer(osm_layer);
        this.olMap.setCenter(this.project(new OpenLayers.LonLat(25, 46)), 7);

        this.olMap.events.register("mousemove", this, function(e) {
            lonLat = this.invproject(this.olMap.getLonLatFromPixel(e.xy));
            this.trigger("mousemove", {lng: lonLat.lon, lat: lonLat.lat});
        });

        // hack to restrict maximum zoom
        this.olMap.getNumZoomLevels = function() { return 14; }
    },

    trackLayer: function(olLayer) {
        var collection = (olLayer.isBaseLayer
                          ? this.baseLayerCollection
                          : this.overlayCollection);
        var layer = collection.get(olLayer.id);
        if(layer === undefined) {
            layer = new TG.Layer({
                id: olLayer.id,
                title: olLayer.name
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
        this.trackLayer(olLayer);
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
        this.trackLayer(road);
        this.trackLayer(hybrid);
        this.trackLayer(aerial);
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
        this.trackLayer(gsat);
        this.trackLayer(gphy);
        this.trackLayer(gmap);
        this.trackLayer(ghyb);
    }

});


TG.MapInfoBox = Backbone.View.extend({

    className: 'map-info-box',
    templateName: 'info-box',

    events: {
        'click .close': 'close'
    },

    show: function(content) {
        var template = TG.templates[this.templateName];
        this.$el.empty().append(template(), content);
        this.delegateEvents();
    },

    close: function(evt) {
        evt.preventDefault();
        this.$el.empty();
        this.trigger('clear');
    }

});


TG.TileLayer = Backbone.Model.extend({
    initialize: function() {
        this.olLayer = new OpenLayers.Layer.XYZ(
            this.get('title'),
            this.get('urlTemplate'),
            {
                isBaseLayer: false,
                sphericalMercator: true,
                visibility: !!this.get('visible')
            }
        );
    }
});


TG.Identify = Backbone.Model.extend({

    initialize: function() {
        this._pending = false;
        this._in_flight = false;
    },

    setCoordinates: function(coords) {
        this.set({'coords': coords});
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
        var coords = this.get('coords');
        $.ajax({
            url: 'get_features_at',
            data: {lat: coords['lat'], lng: coords['lng']},
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

    templateName: 'identify',

    initialize: function(options) {
        this.map = options['map'];
        this.infoBox = options['infoBox'];
        this.model = new TG.Identify;
        this.model.on('change', this.render, this);
        this.model.on('update-start', function() {
            this.$el.addClass('update-in-progress');
        }, this);
        this.model.on('update-end', function() {
            this.$el.removeClass('update-in-progress');
        }, this);

        this.clickHandler = new OpenLayers.Handler.Click(
            this, {'click': this.mapClick}, {map: this.map.olMap, delay: 0});
        this.clickHandler.activate();
    },

    mapClick: function(evt) {
        var lonLat = this.map.invproject(this.map.olMap.getLonLatFromPixel(evt.xy));
        this.model.setCoordinates({lng: lonLat.lon, lat: lonLat.lat});
    },

    render: function() {
        var template = TG.templates[this.templateName];
        var coords = this.model.get('coords');
        var p = new OpenLayers.Geometry.Point(coords['lng'], coords['lat']);
        p = p.transform('EPSG:4326', 'EPSG:31700');
        var features = [];
        _(this.model.get('hit_list')).forEach(function(hit) {
            var layer = this.map.overlayCollection.find(function(o){
                return o.get('name') == hit['layer'];
            });
            if(layer && layer.get('visible')) {
                var f = _.extend({}, hit['properties']);
                if(_(f['id']).startswith('ROSCI')) {
                    f['extra'] = f['id'];
                    f['legend'] = 'sci';
                }
                if(_(f['id']).startswith('ROSPA')) {
                    f['extra'] = f['id'];
                    f['legend'] = 'spa';
                }
                if(_(f['id']).startswith('rezervatie-')) {
                    f['extra'] = 'rezervație';
                    f['legend'] = 'rezervatie';
                }
                if(_(f['id']).startswith('parc-')) {
                    f['extra'] = 'parc';
                    f['legend'] = 'parc';
                }
                features.push(f);
            }
        }, this);
        this.$el.html(template({
            'coords_s70': {'lng': p.x, 'lat': p.y},
            'features': features,
            'error': this.model.get('error')
        }));
        this.infoBox.show(this.el);
    }

});


TG.SiteZoom = Backbone.View.extend({

    initialize: function(options) {
        this.map = options['map'];
    },

    try_to_zoom: function() {
        var hash = window.location.hash;
        if(hash && hash.slice(0, 6) == '#site=') {
            var site_id = hash.slice(6);
            $.get('get_bbox_for_site', {'site_id': site_id},
                  _.bind(this.ajax_result, this));
        }
    },

    ajax_result: function(result) {
        var bbox = this.map.project(OpenLayers.Bounds.fromArray(result['bbox']));
        this.map.olMap.zoomToExtent(bbox);
    }

});


})();
