(function() {

TG.main = function() {
    TG.load_templates();

    TG.map = new TG.Map({parent: $('body')[0]});

    var sciSpaLayer = new TG.TileLayer({
        name: "SCI + SPA",
        url_template: '/static/tiles/all-sites/${z}/${x}/${y}.png'
    })
    TG.map.addOverlay(sciSpaLayer.olLayer);

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

        TG.featureCollectionEditor = new TG.FeatureCollectionEditor({
            model: TG.featureCollection});
        TG.featureCollectionEditor.$el.appendTo($('body'));

        TG.vectorLayer = new TG.VectorLayer({
            model: TG.featureCollection,
            proj: _.bind(TG.map.project, TG.map)
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
};

$(document).ready(TG.main);

})();
