$(document).ready(function() {

$('.virtual-child').each(function() {
    var list = $(this).parent();
    var button = $('a.add', list);
    var item_with_button = $('> :has(a.add)', list);
    var virtual = $(this).remove();

    button.click(function(evt) {
        evt.preventDefault();
        var new_item = virtual.clone().removeClass('virtual-child');
        item_with_button.before(new_item);
    });
});

});
