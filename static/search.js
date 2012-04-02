function capitalise(string)
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

$(document).ready(function() {

    var advanced = 'search-advanced-visible';
    var cookie_name = 'chm-rio-advanced-search';

    $('.search-toggle a').click(function(evt) {
        evt.preventDefault();
        toggle_advanced_search();
    });

    if($.cookie(cookie_name)) {
        toggle_advanced_search();
    }

    function advanced_on() {
        return $('.search-criteria').hasClass(advanced);
    }

    function toggle_advanced_search() {
        $('.search-criteria').toggleClass(advanced);
        if($('.search-criteria').hasClass(advanced)) {
            $('.search-criteria').find('select').chosen();
        };
        var cookie_value = advanced_on() ? 'on' : null;
        $.cookie(cookie_name, cookie_value, {path: '/', expires: 1});
    }

    $('form[name=search]').submit(function(evt) {
        if(! advanced_on()) {
            // clear advanced search inputs
            $('.search-advanced :input:not([type=hidden])').val(null);
        }
    });

    $('.clear-filters').click(function(evt) {
        evt.preventDefault();
        $('.search-criteria :input:not(.search-button)').val(null);
    });

    $("#field-species, #field-habitat, #field-nuts3").chosen().on("change", function () {
        document.location = $(this).find("option:selected").data("url");

    }).val("");

    $("#field-species option,#f_species option,.search-facets .species").each(function () {
        var val = capitalise($.trim($(this).text()));
        $(this).text(val);
    });

    $("#field-species,#f_species").trigger("liszt:updated");
});
