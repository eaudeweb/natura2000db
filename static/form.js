$(document).ready(function() {

$('.virtual-child').each(function() {
    var list = $(this).parent();
    var button = $('a.add', list);
    var item_with_button = $('> :has(a.add)', list);
    var virtual = $(this).remove().removeClass('virtual-child');
    var html = $('<div>').append(virtual).html();
    var next_id = Number(button.text());
    button.text('');

    button.click(function(evt) {
        evt.preventDefault();
        var next_html = html.replace(/NEW_LIST_ITEM/g, next_id);
        var new_item = $('<div>').html(next_html).children();
        item_with_button.before(new_item);
        next_id += 1;
    });
});

});
