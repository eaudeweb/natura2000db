$(document).ready(function() {

$('tr.table-append').each(function() {
    var tr = $(this);
    var tds = tr.children().remove();
    var button = $('<a href="#">+</a>').click(function(evt) {
        evt.preventDefault();
        var new_tr = $('<tr>').append(tds.clone());
        tr.before(new_tr);
    });
    var td_button = $('<td>').attr('colspan', tds.length);
    td_button.append('[', button, ']');
    tr.append(td_button).show();
});

});
