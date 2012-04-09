(function () {

var mapLayersTemplate = "<li class='{{#visible}}active{{/visible}}'><a data-id={{cid}}>{{name}}</a></li>";
var showMoreTemplate = "<li class='show-more' style='display: block'><a>show more</a>";

TG.MapLayers = Backbone.View.extend({

    id: "map-layers",

    tagName: "ul",

    className: "nav nav-tabs nav-stacked",

    events: {
        "click a": "show",
        "click .show-more a": "more"
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
        this.$el.find("li").slice(0, 3).show();
        this.$el.append(_.template(showMoreTemplate)());

        $("#sidebar").append(this.$el);
    },

    show: function (e) {
        var that = $(e.currentTarget);
        if(that.parent().hasClass("active") || that.parent().hasClass("show-more")) {
            return;
        }

        this.$el.find("li").removeClass("active");
        that.parent().addClass("active");

        var model = this.collection.getByCid(that.data("id"));
        model.set('visible', true);
    },

    more: function () {
        var li = this.$el.find("li")
        var showMore = li.last().find("a");
        li.slice(3, li.length - 1).slideToggle("fast");
        showMore.text(showMore.text() == "show more" ? "show less" : "show more");
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
