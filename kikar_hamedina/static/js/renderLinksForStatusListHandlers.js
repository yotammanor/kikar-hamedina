/* renderLinksForStatusListHandler.js -
 handles the styling and link generation for order-by and filter-by-date options.
 uses get request arguments to build relevant links, and uses that data (or lackthereof)
 to style links as active (or hidden).

 used at: core/facebook_status_page.html
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

function setActiveElem(obj, data_param_name, data_param_value, set_custom) {
    // sets element as active if appears in the relevant get request parameter.
    // if all values passed are not set to active, then set_custom will end up being true,
    // Otherwise it will be false.
    if (obj.data(data_param_name).replace('-', '') == data_param_value.replace('-', '')) {
        obj.addClass('active');
        $('a i', obj).show();
        set_custom = false;
    } else {
        obj.removeClass('active');
        $('a i', obj).hide();

    }
    return set_custom
}

function rebuildOrderByHrefAttr(obj, data_param_name, arg_name) {
    // This function renders a url href parameter according to a given element's
    // desired filter or order-by handler, alongside with all other already-applied handlers.
    // after rendering the desired url, it is set as an href parameter to the given object.

    var data_param_value = obj.data(data_param_name);
    if (data_param_value != 'custom') {
        var url_args = getUrlVars();
        var new_url_args = '';
        for (var i = 0; i < url_args.length; i++) {
            if (url_args[i] != arg_name) {
                new_url_args += url_args[i] + '=' + url_args[url_args[i]] + "&"
            }
        }
        new_url_args += arg_name + '=' + data_param_value;
        var new_uri = window.location.pathname + "?" + new_url_args;

        obj.find('a').attr('href', new_uri)
    }
}

$(document).ready(function () {

    // on load, render order-by links as needed.
    $("#order-by-options").children().each(function () {
        rebuildOrderByHrefAttr($(this), "order-by", "order_by")
    });

    // on load, render filter-by-date links as needed.
    $("#filter-by-date-range-options").children().each(function () {
        rebuildOrderByHrefAttr($(this), "range", "range")
    });

    // Set active order-by link style.
    var vars = getUrlVars(), order_by_param, range_param;
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
        set_custom = setActiveElem($(this), 'order-by', order_by_param, set_custom)
    });

    // set default order-by if needed.
    if (set_custom == true) {
        order_by_custom.show()
        order_by_custom.addClass('active')
    }

    // set ascending/descending attributes
    var orderByActiveElem = $('#order-by-options').children('.active');
    var urlArgs = getUrlVars();
    if ('order_by' in urlArgs) {
        if (urlArgs['order_by'].indexOf('-') == -1) {
            // is currently ascending, set to descending
//            orderByActiveElem.data('orderBy', '-' + orderByActiveElem.data('orderBy'))
            $('a i', orderByActiveElem).removeClass('fa-caret-down');
            $('a i', orderByActiveElem).addClass('fa-caret-up')
        } else {
            // is currently descending, set to ascending

            orderByActiveElem.data('orderBy', orderByActiveElem.data('orderBy').replace('-', ''))
        }
    } else {
//      Default order-by is -published, therefor - reverse
        orderByActiveElem.data('orderBy', orderByActiveElem.data('orderBy').replace('-', ''))
    }
    rebuildOrderByHrefAttr(orderByActiveElem, "order-by", "order_by")

    // Set active filter-by-date link style.

    var default_filter = true;
    if (!vars['range']) {
        range_param = false
    } else {
        range_param = vars['range']
    }

    if (range_param != false) {


        $('#filter-by-date-range-options').children().not('.heading').each(function () {
            default_filter = setActiveElem($(this), 'range', range_param, default_filter)
        });

    }

    // set default filter-by-date if needed.

    if (default_filter == true) {
        $('#default-filter').addClass('active')
    }


});