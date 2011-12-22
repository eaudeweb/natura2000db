$(document).ready(function() {

    $('.search-advanced-button').click(function(evt) {
        evt.preventDefault();
        //$('.advanced-search').toggle();
        $('.search-criteria').toggleClass('search-advanced-visible');
    });

});
