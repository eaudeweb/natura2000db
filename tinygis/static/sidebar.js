(function () {

    var Sidebar = Backbone.View.extend({

        id: "sidebar-container",

        events: {
            "click #togglebar": "togglebar"
        },

        initialize: function () {
            this.render();
        },

        render: function () {
            /* <div id="sidebar-container">
                   <div id="togglebar"></div>
                   <div id="sidebar"></div>
               </div>
            */

            var togglebar = this.make("div", {"id": "togglebar"});
            var sidebar = this.make("div", {"id": "sidebar"});

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
        },

        attachView: function () {

        }

    });

    $(function () {
        var sidebar = new Sidebar();
        sidebar.attachView();
    });

})();
