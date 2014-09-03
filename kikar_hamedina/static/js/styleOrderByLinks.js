/* styleOrderByLinks.js - handles the styling and link generation for order by options
   as they appear in facebook_statuses_page, right above a given list of statuses.

 */

function getUrlVars() {
    // a javascript snippet used to extract GET arguments from the current window.location.href.

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

function rebuildOrderByHrefAttr(obj) {
    // This function sets the href parameter for order_by links to include all other given arguments, but set
    // the order-by argument as dictated in the data-order-by attribute.

    var order_by_param = obj.data('order-by');
    if (order_by_param != 'custom') {
        var url_args = getUrlVars();
        var new_url_args = ''
        for (var i = 0; i < url_args.length; i++) {
            if (url_args[i] != 'order_by') {
                new_url_args += url_args[i] + '=' + url_args[url_args[i]] + "&"
            }
        }
        console.log(new_url_args)
        new_url_args += 'order_by=' + order_by_param;
        var new_uri = window.location.pathname + "?" + new_url_args;
        console.log(new_url_args);
        console.log(new_uri);
        obj.find('a').attr('href', new_uri)
    }
}

$(document).ready(function () {

    // on load, redefine href links as needed.
    $("#order-by-options").children().each(function () {
        rebuildOrderByHrefAttr($(this))
    });

    // Set active link style, according to arguments from GET at href.
    var vars = getUrlVars(), order_by_param;
    if (!vars['order_by']) {
        // when there aren't any parameters, the default order_by is -published (as set in the views and settings.py)
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
        } else {
            $(this).removeClass('active');
        }
    });
    if (set_custom == true) {
        order_by_custom.show()
        order_by_custom.addClass('active')
    }

});