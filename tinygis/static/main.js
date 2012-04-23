(function() {


TG.alertBox = function(options) {
    _(options).defaults({category: 'info'});
    var msg_html = TG.templates['message']({options: options});
    $('.alert-container').append(msg_html);
};


TG.main = function() {
    TG.load_templates();

    TG.map = new TG.Map({parent: $('.alert-container').parent()[0]});

    _(TG['AVAILABLE_OVERLAYS']).forEach(function(overlay_options) {
        var layer = new TG.TileLayer(overlay_options);
        layer.id = layer.olLayer.id;
        TG.map.addOverlay(layer.olLayer, {model: layer});
    });

    if(window.google && window.google.maps) {
        TG.map.addGoogleLayers();
    }
    if(TG['BING_MAPS_KEY']) {
        TG.map.addBingLayers(TG['BING_MAPS_KEY']);
    }

    TG.FeatureCollection.prototype.urlRoot = TG.USERLAYERS_URL;

    $.get(TG.USERLAYERS_URL).done(function(data) {
        var id_list = data['ids'];
        var layer_id = null;
        if(id_list.length > 0) {
            layer_id = id_list[0];
        }

        TG.featureCollection = new TG.FeatureCollection({id: layer_id});
        if(layer_id !== null) {
            TG.featureCollection.fetch();
        }
        else {
            TG.featureCollection.setCrs('EPSG:31700');
        }

        TG.vectorLayer = new TG.VectorLayer({
            model: TG.featureCollection,
            mapCrs: TG.map.olMap.getProjectionObject()
        });
        var layerModel = new TG.Layer({
            id: TG.vectorLayer.olLayer.id,
            title: TG.vectorLayer.olLayer.name
        });
        layerModel.geojson = TG.featureCollection;
        TG.map.addOverlay(TG.vectorLayer.olLayer, {model: layerModel});
    });

    var sidebarContainer = new TG.SidebarContainer({
        el: $('#sidebar-container')[0]
    });
    sidebarContainer.on('resize', TG.map.updateSize, TG.map);

    var sidebar = new Backbone.View({
        el: sidebarContainer.$el.find('#sidebar')
    });

    var mapLayers = new TG.MapLayers({"collection": TG.map.baseLayerCollection});
    sidebar.$el.append(mapLayers.$el);
    mapLayers.render();

    var overlayLayers = new TG.Overlays({"collection": TG.map.overlayCollection});
    sidebar.$el.append(overlayLayers.$el);

    TG.mapInfoBox = new TG.MapInfoBox;
    TG.map.$el.parent().append(TG.mapInfoBox.el);

    TG.mapMeasure = new TG.MapMeasure({
        olMap: TG.map.olMap,
        infoBox: TG.mapInfoBox
    });
    TG.mapMeasure.$el.appendTo('#sidebar');

    TG.identify = new TG.IdentifyView({
        map: TG.map,
        infoBox: TG.mapInfoBox
    });

    TG.siteZoom = new TG.SiteZoom({map: TG.map});
    TG.siteZoom.try_to_zoom();
};

$(document).ready(TG.main);
})();
