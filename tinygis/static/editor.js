(function() {


TG.PointFeature = Backbone.Model.extend({
    initialize: function() {
        this.set({lat: 0, lng: 0});
    }
});


TG.FeatureCollection = Backbone.Model.extend({
    initialize: function() {
        this.features = new Backbone.Collection;
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
    },

    addOne: function(feature) {
        var view = new TG.PointEditor({model: feature});
        this.$el.append(view.$el);
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
