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

if(Proj4js !== undefined) {
    Proj4js.defs['EPSG:31700'] = ("+proj=sterea +lat_0=46 +lon_0=25 " +
        "+k=0.99975 +x_0=500000 +y_0=500000 +ellps=krass +units=m +no_defs");
}


TG.GeoJSONGeometry = Backbone.Model.extend({
});


TG.GeoJSONFeature = Backbone.Model.extend({
    initialize: function(attributes, options) {
        this.geometry = options['geometry'];
    },

    toJSON: function() {
        return {
            type: "Feature",
            geometry: this.geometry.toJSON(),
            properties: _.clone(this.attributes)
        };
    }
});


TG.FeatureCollection = Backbone.Model.extend({
    initialize: function() {
        this.features = new Backbone.Collection;
    },

    toJSON: function() {
        var data = {
            type: "FeatureCollection",
            features: this.features.toJSON()
        };
        if(this.crs !== undefined) {
            data['crs'] = {type: 'name', properties: {name: this.crs}};
        }
        return data;
    },

    getCrs: function() {
        var crs = this.crs;
        if(! this.crs) {
            crs = "EPSG:4326";
        }
        return crs;
    },

    setCrs: function(newCrs) {
        this.crs = newCrs;
        this.trigger('crs-change', this);
    },

    parse: function(resp, xhr) {
        var data = _(resp).clone();
        var crs = _(data).pop('crs');
        if(_.isObject(crs) && crs['type'] == 'name' &&
           _.isObject(crs['properties']) && crs['properties']['name']) {
            this.crs = crs['properties']['name'];
        }
        var features_data = _(data).pop('features');
        if(features_data !== undefined) {
            var models = _(features_data).map(function(feature_data) {
                return new TG.GeoJSONFeature(feature_data['properties'], {
                    geometry: new TG.GeoJSONGeometry(feature_data['geometry'])
                });
            });
            this.features.reset(models);
        }
        return data;
    }
});


TG.VectorFeature = Backbone.View.extend({
    initialize: function() {
        this.proj = this.options.proj;
        var type = this.model.geometry.get('type');
        if(type == 'Point') {
            this.geometry = new OpenLayers.Geometry.Point();
        } else if(type == 'Polygon') {
            this.geometry = new OpenLayers.Geometry.Polygon();
        }
        this.feature = new OpenLayers.Feature.Vector(this.geometry);
        this.updateGeometry();
        this.model.geometry.on('change', this.updateGeometry, this);
    },

    updateGeometry: function() {
        var coordinates = this.model.geometry.get('coordinates');
        var type = this.model.geometry.get('type');
        if(type == 'Point') {
            if(coordinates) {
                var lng = coordinates[0], lat = coordinates[1];
                var newGeometry = this.proj(
                    new OpenLayers.Geometry.Point(lng, lat));
                this.geometry.y = newGeometry.y;
                this.geometry.x = newGeometry.x;
                this.geometry.clearBounds();
            }
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
        this.olLayer = new OpenLayers.Layer.Vector("Editabil");
        this.mapCrs = this.options['mapCrs'];
        this.model.features.on('add', this.addOne, this);
        this.model.features.on('reset', this.addAll, this);
        this.model.features.on('destroy', this.destroyFeature, this);
        this.model.on('crs-change', this.crsChange, this);
        this.vectorFeatures = {};
    },

    proj: function(value) {
        return value.transform(this.model.getCrs(), this.mapCrs);
    },

    addOne: function(feature) {
        var vectorFeature = new TG.VectorFeature({
            model: feature,
            proj: _.bind(this.proj, this)
        });
        this.olLayer.addFeatures([vectorFeature.feature]);
        vectorFeature.on('geometry-change', function() {
            this.olLayer.drawFeature(vectorFeature.feature);
        }, this);
        this.vectorFeatures[feature.cid] = vectorFeature;
    },

    addAll: function(features) {
        features.each(this.addOne, this);
    },

    destroyFeature: function(model) {
        var vectorFeature = this.vectorFeatures[model.cid];
        this.olLayer.removeFeatures([vectorFeature.feature]);
    },

    crsChange: function() {
        _(this.vectorFeatures).forEach(function(vectorFeature) {
            vectorFeature.updateGeometry();
        }, this);
    }
});


TG.PointEditor = Backbone.View.extend({
    tagName: 'li',

    className: 'point-editor',

    templateName: 'point-editor',

    events: {
        "click .feature-delete": "featureDelete",
        "click .edit-point-save": "uiChange",
        "mouseover": "over",
        "mouseout": "out"
    },

    initialize: function() {
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        var coordinates = this.model.geometry.get('coordinates') || ['', ''];

        var data = this.model.toJSON();
        data["lng"] = coordinates[0];
        data["lat"] = coordinates[1];

        this.$el.html(template(data));
    },

    featureDelete: function (e) {
        e.preventDefault();
        this.model.destroy();
    },

    uiChange: function() {
        var title = this.$el.find('[name=title]').val();
        var lat = parseFloat(this.$el.find('[name=lat]').val());
        var lng = parseFloat(this.$el.find('[name=lng]').val());

        this.$el.find('.modal').modal('hide');

        this.model.geometry.set("coordinates", [lng, lat]);
        this.model.set("title", title);
        this.render();
    },

    over: function () {
        this.$el.find(".btn-group").show();
    },

    out: function () {
        this.$el.find(".btn-group").hide();
    },

    launchEdit: function() {
        this.$el.find(".modal").modal();
    }
});


TG.PolygonEditor = Backbone.View.extend({
    tagName: 'li',

    className: 'polygon-editor',

    templateName: 'polygon-editor',

    events: {
        "click .import-coordinates-save": "importCoordinates",
        "click .feature-delete": "featureDelete",
        "mouseover": "over",
        "mouseout": "out"
    },

    initialize: function() {
        this.model.geometry.on('change', this.render, this);
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        var coordinates = this.model.geometry.get('coordinates') || [];

        var data = this.model.toJSON();
        data['coordinates'] = function () {
            // last point is same as first so we don't show it
            var str = "";
            _.each(_(coordinates).initial(), function (i) {
                str += i[0] + " " + i[1] + "\n";
            });
            return str;
        };

        this.$el.html(template(data));
    },

    featureDelete: function (e) {
        e.preventDefault();
        this.model.destroy();
    },

    importCoordinates: function(e) {
        e.preventDefault();

        var coordinateData = $('[name=coordinate-data]', this.el).val();
        var title = $('[name=title]', this.el).val();
        var description = $('[name=description]', this.el).val();

        this.$el.find('.modal').modal('hide');
        var newCoordinates = [];
        _(coordinateData.split(/\n/)).forEach(function(row) {
            var m = row.match(/^\s*(\d+([.,]\d+)?)\s+(\d+([.,]\d+)?)\s*$/);
            if(! m) return;
            newCoordinates.push([parseFloat(m[1]), parseFloat(m[3])]);
        });
        if(! _.isEqual(_(newCoordinates).first(), _(newCoordinates).last())) {
            newCoordinates.push(newCoordinates[0]);
        }
        this.model.geometry.set({coordinates: newCoordinates});
        this.model.set("title", title);
        this.model.set("description", description);
        this.render();
    },

    over: function () {
        this.$el.find(".btn-group").show();
    },

    out: function () {
        this.$el.find(".btn-group").hide();
    },

    launchEdit: function() {
        this.$el.find(".modal").modal();
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
        this.featureViews = {};
        this.addAll(this.model);
        this.model.on('add', this.addOne, this);
        this.model.on('reset', this.addAll, this);
        this.model.on('remove', this.removeOne, this);
    },

    addOne: function(feature, collection, options) {
        var editorCls = this.editorClass[feature.geometry.get('type')];
        var view = new editorCls({model: feature});
        this.$el.append(view.$el);
        this.featureViews[view.model.cid] = view;
        if(options && options['is_new']) {
            view.launchEdit();
        }
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

    events: {
        "click [name='add-point']": "createPoint",
        "click [name='add-polygon']": "createPolygon",
        "click .editor-save": "save",
        "change select[name=crs]": "crsSelect"
    },

    initialize: function() {
        this.features = new TG.FeatureList({model: this.model.features});
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        this.$el.html(template({model: this.model}));
        this.$el.append(this.features.$el);

        var crsSelect = this.$el.find('select[name=crs]');
        crsSelect.val(this.model.getCrs());
    },

    crsSelect: function () {
        var crsSelect = this.$el.find('select[name=crs]');
        this.model.setCrs(crsSelect.val());
    },

    createPoint: function() {
        var geometry = new TG.GeoJSONGeometry({type: 'Point'});
        var feature = new TG.GeoJSONFeature({}, {geometry: geometry});
        this.model.features.add(feature, {'is_new': true});
    },

    createPolygon: function() {
        var geometry = new TG.GeoJSONGeometry({type: 'Polygon'});
        var feature = new TG.GeoJSONFeature({}, {geometry: geometry});
        this.model.features.add(feature, {'is_new': true});
    },

    save: function(e) {
        e.preventDefault();
        var xhr = this.model.save();
        xhr.done(function() {
            var msg = TG.message['msg-layer-save-ok'];
            TG.alertBox({message: msg, category: 'success'});
        });
        xhr.fail(function() {
            var msg = TG.message['msg-layer-save-fail'];
            TG.alertBox({message: msg, category: 'error'});
        });
    }

});

})();
