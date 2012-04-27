(function () {


TG.MapLayers = Backbone.View.extend({

    className: 'sidebar-layers',
    templateName: 'sidebar-layers',
    itemTemplateName: "sidebar-layer-item",

    events: {
        "change": "show"
    },

    render: function () {
        var itemTemplate = TG.templates[this.itemTemplateName];

        this.$el.html(TG.templates[this.templateName]());
        var select = this.$el.find('select');

        this.collection.each(function (model, i) {
            var data = model.toJSON();
            data["cid"] = model.cid;
            select.append(itemTemplate(data));
        }, this);
        select.chosen();
    },

    show: function () {
        var cid = this.$el.find('select').val();
        var model = this.collection.getByCid(cid);
        model.set('visible', true);
    }

});


TG.Overlays = Backbone.View.extend({

    events: {
        "click .selector": "select",
        "click .expand": "click_expand",
        "click a.item": "click_expand"
    },

    tagName: "ul",
    className: "nav nav-tabs nav-stacked overlays",
    templateName: "sidebar-overlays",
    itemTemplateName: "sidebar-overlay-item",

    initialize: function () {
        this.collection.on("add", this.render, this);
        this.collection.on("change:visible", this.updateVisible, this);
    },

    render: function () {
        var template = TG.templates[this.templateName];
        var itemTemplate = TG.templates[this.itemTemplateName];

        this.$el.html(template());

        this.collection.each(_.bind(function (model, i) {
            var data = model.toJSON();
            data["cid"] = model.cid;
            data["geojson"] = model.geojson ;
            data["visible"] = data["visible"] || false;
            var $item_el = $(itemTemplate(data));
            this.$el.append($item_el);
            if(model.geojson) {
                var editor = new TG.FeatureCollectionEditor({
                    model: this.collection.getByCid(model.cid).geojson
                });
                editor.$el.appendTo($item_el);
            }
        }, this));
    },

    select: function (e) {
        var that = $(e.currentTarget);
        var model = this.collection.getByCid(that.parent().data("id"));
        model.set('visible', ! model.get('visible'));
    },

    updateVisible: function(model, newValue) {
        var box = this.$el.find('[data-id=' + model.cid + '] .selector');
        box.toggleClass('selected', !! newValue);
    },

    click_expand: function (e) {
        var li = $(e.currentTarget).parents("li")[0];
        this.expand(li);
    }

});


TG.SidebarContainer = Backbone.View.extend({

    id: "sidebar-container",
    templateName: "sidebar-container",

    events: {
        "click #togglebar": "togglebar"
    },

    initialize: function () {
        this.render();
        this.collapsed = false;
    },

    render: function () {
        this.$el.html(TG.templates[this.templateName]());
    },

    togglebar: function () {
        var sidebar = this.$el.find("#sidebar");
        var togglebar = this.$el.find('#togglebar');
        var map_container = this.$el.find('.map-container');
        var trigger_resize = _.bind(this.trigger, this, 'resize');

        this.collapsed = ! this.collapsed;

        if(this.collapsed) {
             sidebar.animate({"width": 0, "padding": 0}, 250);
             togglebar.animate({"left": 0}, 250);
             map_container.animate({"left": 7}, 250, trigger_resize);
        } else {
            sidebar.animate({"width": 180, "padding": 20}, 250);
             togglebar.animate({"left": 220}, 250);
             map_container.animate({"left": 227}, 250, trigger_resize);
        }
    }

});


})();
