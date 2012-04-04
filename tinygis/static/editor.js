(function() {


TG.PointFeature = Backbone.Model.extend({
});


TG.UserLayer = Backbone.Model.extend({
    initialize: function() {
        this.features = new Backbone.Collection;
    }
});


TG.PointEditor = Backbone.View.extend({
    tagName: 'li',
    className: 'point-editor',
    templateName: 'point-editor',

    initialize: function() {
        this.model.on('change', this.render, this);
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        this.$el.html(template(this.model.attributes));
    }
});


TG.UserLayerFeatureList = Backbone.View.extend({
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


TG.UserLayerEditor = Backbone.View.extend({
    tagName: 'div',
    className: 'editor',
    templateName: 'editor',

    initialize: function() {
        this.features = new TG.UserLayerFeatureList({model: this.model.features});
        this.render();
    },

    render: function() {
        var template = TG.templates[this.templateName];
        this.$el.html(template(this.model.attributes));
        $('[name="add-point"]', this.el).click(_.bind(this.createPoint, this));
        this.$el.append(this.features.$el);
    },

    createPoint: function() {
        this.model.features.add(new TG.PointFeature);
    }

});


})();
