(function() {


TG.alertBox = function(options) {
    _(options).defaults({category: 'info'});
    var msg_html = TG.templates['message']({options: options});
    $('.alert-container').append(msg_html);
};


TG.main = function() {
    TG.load_templates();

    TG.map = new TG.Map({parent: $('body')[0]});

    _(TG['AVAILABLE_OVERLAYS']).forEach(function(overlay_options) {
        var layer = new TG.TileLayer(overlay_options);
        TG.map.addOverlay(layer.olLayer);
    });

    if(window.google && window.google.maps) {
        TG.map.addGoogleLayers();
    }
    if(TG['BING_MAPS_KEY']) {
        TG.map.addBingLayers(TG['BING_MAPS_KEY']);
    }

    TG.FeatureCollection.prototype.urlRoot = '/map/userlayers';

    $.get('/map/userlayers').done(function(data) {
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
            name: TG.vectorLayer.olLayer.name
        });
        layerModel.geojson = TG.featureCollection;
        TG.map.addOverlay(TG.vectorLayer.olLayer, {model: layerModel});
    });

    var sidebar = new TG.Sidebar();
    sidebar.on('resize', TG.map.updateSize, TG.map);
    var mapLayers = new TG.MapLayers({"collection": TG.map.baseLayerCollection});
    var overlayLayers = new TG.Overlays({"collection": TG.map.overlayCollection});
};

$(document).ready(TG.main);
})();
