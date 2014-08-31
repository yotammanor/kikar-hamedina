function getUrlVars() {
    var vars = [], hash;
    if (window.location.href.indexOf('?') == -1) {
        vars = []
    } else {
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        for (var i = 0; i < hashes.length; i++) {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = hash[1];
        }
    }
    return vars;
}

$(document).ready(function () {
    var vars = getUrlVars(), order_by_param;
    if (vars.length == 0) {
        console.log('no params');
        order_by_param = '-published'
    } else {
        order_by_param = vars['order_by'];
    }
    var set_custom = true;
    var order_by_custom = $('#order-by-custom');
    order_by_custom.hide();
    $('#order-by-options').children().each(function () {
//        console.log($(this));
        if ($(this).data('order-by') == order_by_param) {
            $(this).addClass('active');
            set_custom = false;
            console.log('yes')
        } else {
            $(this).removeClass('active');
            console.log('no')
        }
    });
    if (set_custom == true) {
        order_by_custom.show()
        order_by_custom.addClass('active')
    }

});