(function() {


_.mixin({
    pop: function(obj, key) {
        if(_.isArray(obj)) {
            return obj.splice(key, 1)[0];
        }
        if(_.has(obj, key)) {
            var value = obj[key];
            delete obj[key];
            return value;
        }
    }
});


var lastAutoId = 0;
_.mixin({
    generateAutoId: function() {
        lastAutoId += 1;
        return lastAutoId;
    }
});


TG.GeoJSONGeometry = Backbone.Model.extend({
});


TG.FeatureCollection = Backbone.Model.extend({
    initialize: function() {
        this.features = new Backbone.Collection;
    },

    toJSON: function() {
        return {
            type: "FeatureCollection",
            features: this.features.map(function(geojsonGeometry) {
                return {
                    type: "Feature",
                    geometry: geojsonGeometry.toJSON()
                };
            })
        };
    },

    parse: function(resp, xhr) {
        var data = _(resp).clone();
        var features_data = _(data).pop('features');
        if(features_data !== undefined) {
            var models = _(features_data).map(function(feature_data) {
                var geometry = _(feature_data).pop('geometry');
                return new TG.GeoJSONGeometry(geometry);
            });
            this.features.reset(models);
        }
        return data;
    }
});


TG.VectorFeature = Backbone.View.extend({
    initialize: function() {
        this.proj = this.options.proj;
        var type = this.model.get('type');
        if(type == 'Point') {
            this.geometry = new OpenLayers.Geometry.Point();
        } else if(type == 'Polygon') {
            this.geometry = new OpenLayers.Geometry.Polygon();
        }
        this.feature = new OpenLayers.Feature.Vector(this.geometry);
        this.updateGeometry();
        this.model.on('change', this.updateGeometry, this);
    },

    updateGeometry: function() {
        var coordinates = this.model.get('coordinates');
        var type = this.model.get('type');
        if(type == 'Point') {
            var lng = coordinates[0], lat = coordinates[1];
            var newGeometry = this.proj(new OpenLayers.Geometry.Point(lng, lat));
            this.geometry.y = newGeometry.y;
            this.geometry.x = newGeometry.x;
            this.geometry.clearBounds();
        } else if(type == 'Polygon') {
            while(this.geometry.components.length > 0) {
                this.geometry.removeComponent(this.geometry.components[0]);
            }
            var pointList = _(coordinates).map(function(pc) {
                return new OpenLayers.Geometry.Point(pc[0], pc[1]);
            });
            var newLinearRing = new OpenLayers.Geometry.LinearRing(pointList);
            this.geometry.addComponent(this.proj(newLinearRing));
        }
        this.trigger('geometry-change');
    }
});


TG.VectorLayer = Backbone.View.extend({
    initialize: function() {
        this.olLayer = new OpenLayers.Layer.Vector("Vector");
        this.proj = this.options.proj;
        this.model.features.on('add', this.addOne, this);
        this.model.features.on('reset', this.addAll, this);
    },

    addOne: function(feature) {
        var vectorFeature = new TG.VectorFeature({
            model: feature,
            proj: this.proj
        });
        this.olLayer.addFeatures([vectorFeature.feature]);
        vectorFeature.on('geometry-change', function() {
            this.olLayer.drawFeature(vectorFeature.feature);
        }, this);
    },

    addAll: function(features) {
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
        var coordinates = this.model.get('coordinates') || ['', ''];
        this.$el.html(template({lng: coordinates[0], lat: coordinates[1]}));
        $('.point-geometry input', this.el).change(_.bind(this.uiChange, this));
        $('.feature-delete', this.el).click(_.bind(function(evt) {
            evt.preventDefault();
            this.model.destroy();
        }, this));
    },

    uiChange: function() {
        var lat = parseFloat($('.point-geometry [name=lat]', this.el).val());
        var lng = parseFloat($('.point-geometry [name=lng]', this.el).val());
        this.model.set({coordinates: [lng, lat]});
    }
});


TG.PolygonEditor = Backbone.View.extend({
    tagName: 'li',
    className: 'polygon-editor',
    templateName: 'polygon-editor',

    initialize: function() {
        this.model.on('change', this.render, this);
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        var coordinates = this.model.get('coordinates');
        this.$el.html(template({
            coordinates: _(coordinates).initial() // last point is same as first
        }));
        var _importCoordinates = _.bind(this.importCoordinates, this);
        $('.import-coordinates-save', this.el).click(_importCoordinates);
        $('.feature-delete', this.el).click(_.bind(function(evt) {
            evt.preventDefault();
            this.model.destroy();
        }, this));
    },

    importCoordinates: function(evt) {
        evt.preventDefault();
        var coordinateData = $('[name=coordinate-data]', this.el).val();
        $('.modal', this.el).modal('hide');
        var newCoordinates = [];
        _(coordinateData.split(/\n/)).forEach(function(row) {
            var m = row.match(/^\s*(\d+([.,]\d+)?)\s+(\d+([.,]\d+)?)\s*$/);
            if(! m) return;
            newCoordinates.push([parseFloat(m[1]), parseFloat(m[3])]);
        });
        if(! _.isEqual(_(newCoordinates).first(), _(newCoordinates).last())) {
            newCoordinates.push(newCoordinates[0]);
        }
        this.model.set({coordinates: newCoordinates});
    }
});


TG.FeatureList = Backbone.View.extend({
    tagName: 'ul',
    className: 'editor-features',
    editorClass: {
        'Point': TG.PointEditor,
        'Polygon': TG.PolygonEditor
    },

    initialize: function() {
        this.model.on('add', this.addOne, this);
        this.model.on('reset', this.addAll, this);
        this.model.on('remove', this.removeOne, this);
        this.featureViews = {};
    },

    addOne: function(feature) {
        var editorCls = this.editorClass[feature.get('type')];
        var view = new editorCls({model: feature});
        this.$el.append(view.$el);
        this.featureViews[view.model.cid] = view;
    },

    addAll: function(features) {
        features.each(this.addOne, this);
    },

    removeOne: function(feature) {
        var view = _(this.featureViews).pop(feature.cid);
        view.$el.remove();
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
        $('[name="add-polygon"]', this.el).click(_.bind(this.createPolygon, this));
        this.$el.append(this.features.$el);
        $('.editor-save', this.el).click(_.bind(this.save, this));
    },

    createPoint: function() {
        this.model.features.add(new TG.GeoJSONGeometry({type: 'Point'}));
    },

    createPolygon: function() {
        this.model.features.add(new TG.GeoJSONGeometry({type: 'Polygon'}));
    },

    save: function(evt) {
        evt.preventDefault();
        this.model.save();
    }

});


})();
