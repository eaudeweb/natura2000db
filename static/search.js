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
        var cookie_value = advanced_on() ? 'on' : null;
        $.cookie(cookie_name, cookie_value, {expires: 1});
    }

    $('form[name=search]').submit(function(evt) {
        if(! advanced_on()) {
            // clear advanced search inputs
            $('.search-advanced :input').val(null);
        }
    });

});
