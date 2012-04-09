(function () {

var mapLayersTemplate = " \
    <li class='hide <% if (visible) { %> visible <% } %>'> \
        <a data-id=<%=cid%>><%=name%></a> \
    </li>";

var showMoreTemplate = "<li class='show-more' style='display: block'><a>show more</a>";

var overlaysTemplate = "\
    <li data-id='<%=cid%>'> \
        <% if(geojson) { %> <div class='icon icon-play expand'></div> <% } %> \
        <a><%=name%></a> \
        <div class='selector <% if(visible) { %> selected <% } %>'><b></b></div> \
    </li>";

var Layers = Backbone.View.extend({

    tagName: "ul",

    className: "nav nav-tabs nav-stacked",

    initialize: function () {
        this.render();
    }
});

TG.MapLayers = Layers.extend({

    events: {
        "click a": "show",
        "click .show-more a": "more"
    },

    render: function () {
        var self = this;

        this.$el.append(this.make("li", {"class": "nav-header"}, "Base Layers"));
        this.collection.each(function (model, i) {
            var data = model.toJSON();
            data["cid"] = model.cid;
            self.$el.append(_.template(mapLayersTemplate, data));
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
        var li = this.$el.find("li");
        var liShowMore = li.last().find("a");

        li.slice(3, li.length - 1).slideToggle("fast");
        liShowMore.text(liShowMore.text() == "show more" ? "show less" : "show more");
    }

});

TG.Overlays = Layers.extend({

    events: {
        "click .selector": "select",
        "click .expand": "expand"
    },

    initialize: function () {
        this.collection.on("add", function () {
            this.render();
        }, this);
    },

    render: function () {

        this.$el.addClass("overlays");
        this.$el.empty();
        this.$el.append(this.make("li", {"class": "nav-header"}, "Overlays"));

        this.collection.each(_.bind(function (model, i) {
            var data = model.toJSON();
            data["cid"] = model.cid;
            data["geojson"] = model.geojson ;
            data["visible"] = data["visible"] || true;
            this.$el.append(_.template(overlaysTemplate, data));
        }, this));

        $("#sidebar").append(this.$el);
    },

    select: function (e) {
        var that = $(e.currentTarget);
        that.toggleClass("selected");

        var model = this.collection.getByCid(that.parent().data("id"));
        if(that.hasClass("selected")) {
            model.set("visible", true);
        } else {
            model.set('visible', false);
        }
    },

    expand: function (e) {

        var that = $(e.currentTarget);
        var editor = that.parent().find(".editor");
        that.toggleClass("icon-play");
        that.toggleClass("icon-minus");

        if(editor.length == 0 ) {
            var model = this.collection.getByCid(that.parent().data("id"));
            TG.featureCollectionEditor = new TG.FeatureCollectionEditor({
                model: model.geojson});
            TG.featureCollectionEditor.$el.appendTo(that.parent());
        } else{
            editor.slideToggle("fast");
        }
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
