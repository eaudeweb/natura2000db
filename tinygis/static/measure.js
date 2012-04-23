(function() {

TG.MapMeasure = Backbone.View.extend({

    className: 'tinygis-map-measure',

    events: {
        'click .measure-begin': 'begin',
        'click .close': 'deactivate'
    },

    initialize: function(options) {
        this.olMap = options['olMap'];
        this.infoBox = options['infoBox'];
        var sketchSymbolizers = {
            "Point": {
                pointRadius: 4,
                graphicName: "square",
                fillColor: "white",
                fillOpacity: 1,
                strokeWidth: 1,
                strokeOpacity: 1,
                strokeColor: "#333333"
            },
            "Line": {
                strokeWidth: 3,
                strokeOpacity: 1,
                strokeColor: "#666666",
                strokeDashstyle: "dash"
            },
            "Polygon": {
                strokeWidth: 2,
                strokeOpacity: 1,
                strokeColor: "#666666",
                fillColor: "#888888",
                fillOpacity: 0.5
            }
        };
        var style = new OpenLayers.Style();
        style.addRules([
            new OpenLayers.Rule({symbolizer: sketchSymbolizers})
        ]);
        var styleMap = new OpenLayers.StyleMap({"default": style});

        this.controls = {
            line: new OpenLayers.Control.Measure(
                OpenLayers.Handler.Path, {
                    persist: true,
                    geodesic: true,
                    immediate: true,
                    handlerOptions: {
                        layerOptions: {
                            styleMap: styleMap
                        }
                    }
                }
            ),
            polygon: new OpenLayers.Control.Measure(
                OpenLayers.Handler.Polygon, {
                    persist: true,
                    geodesic: true,
                    immediate: true,
                    handlerOptions: {
                        layerOptions: {
                            styleMap: styleMap
                        }
                    }
                }
            )
        };

        _(_(this.controls).values()).forEach(function(control) {
            control.events.on({
                "measurepartial": this.measureUpdate,
                "measure": this.measureEnd,
                scope: this
            }, this);
            this.olMap.addControl(control);
        }, this);

        this.render();

        this.active = null;
    },

    render: function() {
        this.$el.html(TG.templates['measure']({active: this.active}));
        if(this.active) {
            this.infoBox.on('clear', this.deactivate, this);
            this.infoBox.show(TG.templates['measure-result']({
                result: this.result
            }));
        }
        else {
            this.infoBox.off('clear', this.deactivate, this);
        }
    },

    setActive: function(measurement) {
        this.controls['line'].deactivate();
        this.controls['polygon'].deactivate();
        this.result = null;
        this.active = measurement;
        if(this.controls[measurement]) {
            this.controls[measurement].activate();
        }
        this.render();
    },

    begin: function(evt) {
        this.setActive($(evt.target).data('measure'));
    },

    deactivate: function(evt) {
        this.setActive(null);
    },

    measureUpdate: function(evt) {
        this.result = {
            value: evt.measure.toFixed(3),
            units: evt.units,
            order: evt.order
        };
        this.render();
    },

    measureEnd: function(evt) {
        this.measureUpdate(evt);
    }

});

})();
