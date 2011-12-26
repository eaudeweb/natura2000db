$(document).ready(function() {

    var advanced = 'search-advanced-visible';
    var cookie_name = 'chm-rio-advanced-search';

    $('.search-toggle').click(function(evt) {
        evt.preventDefault();
        toggle_advanced_search();
    });

    if($.cookie(cookie_name)) {
        toggle_advanced_search();
    }

    function toggle_advanced_search() {
        var on = $('.search-criteria').toggleClass(advanced).hasClass(advanced);
        $.cookie(cookie_name, on ? 'on' : null, {expires: 1});
    }

});
