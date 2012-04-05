(function() {


_.mixin({
    pop: function(obj, name) {
        if(_.has(obj, name)) {
            var value = obj[name];
            delete obj[name];
            return value;
        }
    }
});


TG.PointFeature = Backbone.Model.extend({
    defaults: {lat: 0, lng: 0},

    toJSON: function() {
        return {
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [this.get('lng'), this.get('lat')]
            }
        };
    },

    parse: function(resp, xhr) {
        console.log('PointFeature.parse', resp);
        var data = _(resp).clone();
        var geometry = _(data).pop('geometry');
        if(geometry !== undefined) {
            _(data).extend({
                lng: geometry['coordinates'][0],
                lat: geometry['coordinates'][1]
            });
        }
        return data;
    }
});


TG.FeatureCollection = Backbone.Model.extend({
    initialize: function() {
        this.features = new Backbone.Collection;
    },

    toJSON: function() {
        return {
            type: "FeatureCollection",
            features: this.features.invoke('toJSON')
        };
    },

    parse: function(resp, xhr) {
        console.log('FeatureCollection.parse', resp);
        var data = _(resp).clone();
        var features = _(data).pop('features');
        if(features !== undefined) {
            var models = _(features).map(function(feature_data) {
                return new TG.PointFeature(feature_data,
                    {parse: TG.PointFeature.prototype.parse});
            });
            this.features.reset(models);
        }
        return data;
    }
});


TG.VectorFeature = Backbone.View.extend({
    initialize: function() {
        this.proj = this.options.proj;
        this.geometry = new OpenLayers.Geometry.Point(0, 0);
        this.feature = new OpenLayers.Feature.Vector(this.geometry);
        this.updateGeometry();
        this.model.on('change', this.updateGeometry, this);
    },

    updateGeometry: function() {
        var lat = this.model.get('lat'), lng = this.model.get('lng');
        new_geometry = this.proj(new OpenLayers.Geometry.Point(lng, lat));
        this.geometry.y = new_geometry.y;
        this.geometry.x = new_geometry.x;
        this.geometry.clearBounds();
        this.trigger('geometry-change');
    }
});


TG.VectorLayer = Backbone.View.extend({
    initialize: function() {
        this.layer = new OpenLayers.Layer.Vector("Vector");
        this.proj = this.options.proj;
        this.model.features.on('add', this.addOne, this);
        this.model.features.on('reset', this.addAll, this);
    },

    addOne: function(feature) {
        var vectorFeature = new TG.VectorFeature({
            model: feature,
            proj: this.proj
        });
        this.layer.addFeatures([vectorFeature.feature]);
        vectorFeature.on('geometry-change', function() {
            this.layer.drawFeature(vectorFeature.feature);
        }, this);
    },

    addAll: function(features) {
        console.log('VectorLayer.addAll', arguments);
        features.each(this.addOne, this);
    }
});


TG.PointEditor = Backbone.View.extend({
    tagName: 'li',
    className: 'point-editor',
    templateName: 'point-editor',

    initialize: function() {
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        this.$el.html(template(this.model.attributes));
        $('.point-geometry input', this.el).change(_.bind(this.uiChange, this));
    },

    uiChange: function() {
        this.model.set({
            lat: parseFloat($('.point-geometry [name=lat]', this.el).val()),
            lng: parseFloat($('.point-geometry [name=lng]', this.el).val())
        });
    }
});


TG.FeatureList = Backbone.View.extend({
    tagName: 'ul',
    className: 'editor-features',

    initialize: function() {
        this.model.on('add', this.addOne, this);
        this.model.on('reset', this.addAll, this);
    },

    addOne: function(feature) {
        var view = new TG.PointEditor({model: feature});
        this.$el.append(view.$el);
    },

    addAll: function(features) {
        features.each(this.addOne, this);
    }
});


TG.FeatureCollectionEditor = Backbone.View.extend({
    tagName: 'div',
    className: 'editor',
    templateName: 'editor',

    initialize: function() {
        this.features = new TG.FeatureList({model: this.model.features});
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        this.$el.html(template(this.model.attributes));
        $('[name="add-point"]', this.el).click(_.bind(this.createPoint, this));
        this.$el.append(this.features.$el);
        $('.editor-save', this.el).click(_.bind(this.save, this));
    },

    createPoint: function() {
        this.model.features.add(new TG.PointFeature);
    },

    save: function(evt) {
        evt.preventDefault();
        this.model.save();
    }

});


})();
