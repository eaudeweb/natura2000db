(function () {

var mapLayersTemplate = "<li class='{{#visible}}active{{/visible}}'><a data-id={{cid}}>{{name}}</a></li>";

TG.MapLayers = Backbone.View.extend({

    id: "map-layers",

    tagName: "ul",

    className: "nav nav-tabs nav-stacked",

    events: {
        "click a": "show"
    },

    initialize: function () {
        this.render();
    },

    render: function () {
        var self = this;

        this.$el.append(this.make("li", {"class": "nav-header"}, "Base Layers"));
        this.collection.each(function (model, i) {
            var data = model.toJSON();
            data["cid"] = model.cid;
            self.$el.append(Mustache.to_html(mapLayersTemplate, data));
        });

        $("#sidebar").append(this.$el);
    },

    show: function (e) {
        var that = $(e.currentTarget);
        if(that.parent().hasClass("active")) {
            return;
        }

        this.$el.find("li").removeClass("active");
        that.parent().addClass("active");

        var model = this.collection.getByCid(that.data("id"));
        model.set('visible', true);

    }

});

TG.Sidebar = Backbone.View.extend({

    id: "sidebar-container",

    events: {
        "click #togglebar": "togglebar"
    },

    initialize: function () {
        this.render();
    },

    render: function () {

        var login = _.template($(".template-src[data-name=login]").html())();
        var togglebar = this.make("div", {"id": "togglebar"});
        var sidebar = this.make("div", {"id": "sidebar"}, login);

        $("body").append(
            this.$el
                .append(togglebar)
                .append(sidebar)
        );
    },

    togglebar: function () {
        var sidebar = $("#sidebar");
        var self = this;
        if(sidebar.width() === 0) {
            sidebar.animate({"width": 180, "padding": 20}, 250);
             $("#togglebar").animate({"left": 220}, 250);
             $("#tinygis-map").animate({"left": 220}, 250, function () {
                self.trigger("resize");
             });
        } else {
             sidebar.animate({"width": 0, "padding": 0}, 250);
             $("#togglebar").animate({"left": 0}, 250);
             $("#tinygis-map").animate({"left": 0}, 250, function () {
                self.trigger("resize");
             });
        }
    }

});

})();
