/* SearchGui.js - defines the behaviour of the advanced search interface.
 *  It allows auto-suggest as you type (mk, party, tags),
 * allows for free search, lets you set advanced filtering and order-by.
 * */

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


function deconstuctURL(fullPath) {
    //var url;
    var searchTerms = {
        'member': [],
        'party': [],
        'tag': [],
        'search_str': [],
        'excluded': []
    };
    //$(".result-info").each(function () {
    //    type = $(this).data('type');
    //    id = $(this).data('id');
    //    searchTerms[type].push(id)
    //
    //});

    //url = baseURL;
    var memberIDs = getParameterByName('members');
    memberIDs.length > 0 ? searchTerms['member'] = memberIDs.split(',') : searchTerms['member'] = [];

    var partyIDs = getParameterByName('parties');
    partyIDs.length > 0 ? searchTerms['party'] = partyIDs.split(',') : searchTerms['party'] = [];

    var TagIDs = getParameterByName('tags');
    TagIDs.length > 0 ? searchTerms['tag'] = TagIDs.split(',') : searchTerms['tag'] = [];

    var searchStrIDs = getParameterByName('search_str');
    if (searchStrIDs.length > 0) {
        var searchStrArray = searchStrIDs.split(',');
        searchStrArray.forEach(function (elem, index, array) {
            array[index] = elem.replace(/"/g, '')
        });
        searchTerms['search_str'] = searchStrArray
    }

    var excludedIDs = getParameterByName('excluded');
    excludedIDs.length > 0 ? searchTerms['excluded'] = excludedIDs.split(',') : searchTerms['excluded'] = [];


    for (var dictIndex in searchTerms) {
        if (searchTerms.hasOwnProperty(dictIndex)) {
            var attr = searchTerms[dictIndex];
            attr.forEach(function (elem, index, array) {
                var id = elem;
                var type = dictIndex;
                var icon;
                var url;
                var useAjax = true;
                var baseAPI = '/api/v1/';
                switch (type) {
                    case 'member':
                        icon = 'user';
                        url = baseAPI + type + '/' + id + '/';
                        break;
                    case 'party':
                        icon = 'group';
                        url = baseAPI + type + '/' + id + '/';
                        break;
                    case 'tag':
                        icon = 'tag';
                        url = baseAPI + type + '/' + id + '/';
                        break;
                    case 'excluded':
                        url = baseAPI + 'facebook_status/?status_id=' + id;
                        icon = 'ban';
                        break;
                    default: // case search_str
                        useAjax = false;
                        icon = 'comment';
                }
                var name;
                if (useAjax == true) {
                    $.ajax({
                        url: url,
                        method: 'get',
                        contentType: "application/json",
                        success: function (data) {
                            if (type == 'excluded') {
                                name = 'סטאטוס מאת: ' + data['objects'][0]['member'] + ' - ' + id
                            } else {
                                name = data['name'];
                            }

                            addAutoSuggestElementToFilter(id, name, type, icon)
                        }
                    });
                } else {
                    name = id;
                    addWordElementToFilter(name)
                }
            });
        }
    }

    var orderByFull = getParameterByName('order_by');
    if (orderByFull.length > 0) {
        if (orderByFull.indexOf('-') == 0) {
            $('#searchgui-order-by-dir-desc').attr('checked', 'checked');
        } else {
            $('#searchgui-order-by-dir-asc').attr('checked', 'checked')
        }
        var orderBy = orderByFull.split('-')[1];
        $("input:radio[name=selected-order-by][value=" + orderBy + "]").attr('checked', 'checked');
    }

    var fromDate = getParameterByName('from_date');
    fromDate.length > 0 && $('#input-from-date').val(fromDate);

    var toDate = getParameterByName('to_date');
    toDate.length > 0 && $('#input-to-date').val(toDate);

    var operator = getParameterByName('tags_and_search_str_operator');
    operator.length > 0 && $('#searchgui-selected-operator-' + operator.split('_operator')[0]).attr('checked', 'checked');

    return searchTerms;
}

function buildURL(baseURL) {
    var url;
    var searchTerms = {
        'member': [],
        'party': [],
        'tag': [],
        'search_str': [],
        'excluded': []
    };
    $(".result-info").each(function () {
        type = $(this).data('type');
        id = $(this).data('id');
        searchTerms[type].push(id)

    });
    url = baseURL;
    var member_ids = searchTerms['member'].join(',');
    if (member_ids.length > 0) {
        url += "members=" + member_ids + "&"
    }
    var party_ids = searchTerms['party'].join(',');
    if (party_ids.length > 0) {
        url += "parties=" + party_ids + "&"
    }
    var tag_ids = searchTerms['tag'].join(',');
    if (tag_ids.length > 0) {
        url += "tags=" + tag_ids + "&"
    }

    var orderByDir = $('#search-gui-order-by-direction-input').children('input:checked').val();


    var inputValue = $('#searchgui-text-input').val();
    if (inputValue.length > 0) {
        searchTerms['search_str'].push(inputValue)
    }

    var search_str_ids = '"' + searchTerms['search_str'].join('","') + '"';
    if (search_str_ids.length > 2) {
        // length > 2 - is set because an empty string will be "" //
        url += "search_str=" + search_str_ids + "&"
    }
    var excluded_ids = searchTerms['excluded'].join(',');
    if (excluded_ids.length > 2) {
        url += "excluded=" + excluded_ids + "&";
    }
    var operator = $("input:radio[name=selected-operator]:checked").val();
    var orderBy = $("input:radio[name=selected-order-by]:checked").val();
    if (orderByDir == 'desc') {
        orderBy = '-' + orderBy
    } else if (orderByDir == 'asc') {
    }
    var fromDate = $('#input-from-date').val();
    var toDate = $('#input-to-date').val();
    url += "tags_and_search_str_operator=" + operator + "&order_by=" + orderBy;
    if(fromDate != "") {
        url += "&from_date=" + fromDate
    }
    if(toDate != ""){
        url += "&to_date=" + toDate
    }
    return url
}

function addWordElementToFilter(name) {
    var context = {};
    context['id'] = name;
    context['name'] = name;
    $(this).data('word-num', context['id'] + 1);
    context['type'] = 'search_str';
    context['icon'] = 'comment';
    var source = $("#search-gui-added-list-item-template").html();
    var template = Handlebars.compile(source);
    var html = template(context);
    $('#searchgui-search-words').append(html);

    var addedElement = $('#searchgui-search-words').find("#" + context['type'] + context['id']);
    addedElement.find(".fa-times").parent().click(function () {
        $('#searchgui-search-words').find("#" + context['type'] + context['id']).remove();
        updateSearchGUIObjectsVisibility()
    });
    addedElement.find(".fa-times").parent().hover(function () {
        $(this).toggleClass("alert-danger")
    });
    addedElement.hover(function () {
        $(this).find(".fa-" + context['icon']).parent().toggleClass("alert-success");
        $(this).find(".fa-times").parent().toggleClass("hidden-badge")
    });


    $('#searchgui-text-input').val('');
    updateSearchGUIObjectsVisibility()
}

function addAutoSuggestElementToFilter(id, name, type, icon) {
    /* This function adds a selected auto-suggest option to applied filters.
     *
     * */
    var source = $("#search-gui-added-list-item-template").html();
    var template = Handlebars.compile(source);
    var context = {'id': id, 'name': name, 'type': type, 'icon': icon};
    var html = template(context);
    $('#search-gui-' + type + '-added-list').append(html);
    var addedElement = $('#search-gui-' + type + '-added-list').find("#" + type + id);
    addedElement.find(".fa-times").parent().click(function () {
        id = $(this).data('id');
        type = $(this).data('type');
        removeSelectedFilterElement(id, type)
    });
    addedElement.find(".fa-times").parent().hover(function () {
        $(this).toggleClass("alert-danger")
    });
    addedElement.hover(function () {
        $(this).find(".fa-" + icon).parent().toggleClass("alert-success");
        $(this).find(".fa-times").parent().toggleClass("hidden-badge");
    });

    // clean-ups after adding.
    $('#searchgui-text-input').val('');

    updateSearchGUIObjectsVisibility()


}

function removeSelectedFilterElement(id, type) {
    /* remove a selected element fro applied filters.
     */
    $("#" + type + id).remove();

    // clean-up after removing.
    updateSearchGUIObjectsVisibility()

}

function updateSearchGUIObjectsVisibility() {
    /* This function reapplies visibility paraemeters for all necessary elements.

     */
    var tempScrollTop = $(window).scrollTop();
    var searchTerms = {
        'member': [],
        'party': [],
        'tag': [],
        'search_str': [],
        'excluded': []
    };
    $(".result-info").each(function () {
        var type = $(this).data('type');
        var id = $(this).data('id');
        searchTerms[type].push(id)
    });
    var keysOfSearchTerms = Object.keys(searchTerms);
    for (var i = 0; i < keysOfSearchTerms.length; i++) {
        if (searchTerms[keysOfSearchTerms[i]].length > 0) {
            $('#list-of-' + keysOfSearchTerms[i] + '-title').show()
        } else {
            $('#list-of-' + keysOfSearchTerms[i] + '-title').hide()
        }
    }

    var results_to_delete = $('#search-gui-result-list').children();
    for (var i = 0; i < results_to_delete.length; i++) {
        results_to_delete[i].remove()
    }
    if (searchTerms['tag'].length > 0 && searchTerms['search_str'].length > 0) {
        $('#searchgui-operator-input').show()
    } else {
        $('#searchgui-operator-input').hide()
    }
    $(window).scrollTop(tempScrollTop)
}

$(document).ready(function () {
    // Initialize datepicker
    var date_input = $('#search-gui-date-filter-input .input-daterange');
    var options = {
        format: "dd-mm-yyyy",
        maxViewMode: 2,
        endDate: "+1d",
        todayBtn: "linked",
        language: $('#datepicker').data('datepicker-options-language'),
        orientation: "top left",
        todayHighlight: true,
        rtl: true

    };
    date_input.datepicker(options);
    $('#datepicker input').on("focus", function (event) {
        $('.datepicker').css("left", "inherit"); // Fix RTL display
    });

//  cleans results list at loading.
    $(".fa-trash").parent().click(function () {
        $('#searchgui-text-input').val('');
        $('#search-gui-result-list').html('');
        $('#search-gui-member-added-list').html('');
        $('#search-gui-party-added-list').html('');
        $('#search-gui-tag-added-list').html('')
    });

    deconstuctURL();

    // Event: click save query button to open modal-dialog form
    $('#searchgui-save-button').click(function () {
        var query = $('#form-query');
        var url = buildURL("/search/?");
        query.html(url);
    });

    // event: submit save query modal-dialog form
    $('#save-query-submit-form-btn').click(function () {
        $('.inline-error-p').html('');
        var title = $('#form-query-title').val();
        var url = '/title_exists/?title=' + title;
        if ($('#form-query').val().length == 0) {
            $('#query-error-message').html('No Query to save!')
        }
        $.ajax({
            url: url,
            type: 'get',
            contentType: "application/json",
            success: function (data) {
                if (data['approved'] == true) {
                    $.ajax({
                        url: '/custom/save/',
                        type: 'post',
                        dataType: 'json',
                        data: $('form#save-query-form').serialize(),
                        success: function (data) {
                            console.log(data);
                            $('#query-error-message').html('Query Saved Successfuly!')

                        },
                        error: function (data) {
                            console.log(data)
                        }
                    });
                } else {
                    $('#title-error-message').html(data['message'])
                }
                console.log(data)
            },
            error: function (x, y) {
                console.log(x);
                console.log(y)
            }
        });
    });

//  hover-effects on submit button
    $("#searchgui-go-button").hover(function () {
        $(this).toggleClass("alert-info")
    });

//  event: clicking on Submit button, when search is non-empty.
//         Builds search path and parameters.
    $(".searchgui-execute-btn").click(function () {
        if ($(".result-info").length > 0 || $('#searchgui-text-input').val().length > 0 || this.id == 'searchgui-preview-button') {
            var url, baseURL;
            var target;
            if (this.id == 'searchgui-preview-button') {
                $('#loading').show();
                target = 'iframe';
                baseURL = "/preview/?";
            } else if (this.id == 'searchgui-go-button') {
                target = 'window';
                baseURL = "/search/?";
            }

            url = buildURL(baseURL);

            if (target == 'window') {
                window.location.assign(encodeURI(url))

            } else if (target == 'iframe') {
                $('#preview-iframe').attr('src', encodeURI(url));
            } else if (target == 'form') {
                $('#form-query').html(url)
            }
        } else {
            // no input at all.
            $("#searchgui-text-input").attr("placeholder", 'צריך לחפש משהו בשביל למצוא משהו')
        }
    });

    // events within the iframe
    var iframe = $('#preview-iframe');
    iframe.load(function () {
        $('#preview-iframe').contents().find(".exclude-status").each(function () {
            $(this).show()
        });
        // event: a status was excluded
        iframe.contents().find("body").on('click', '.exclude-status', function (e) {
            var context = {};
            context['id'] = $(this).data('status-id');
            context['name'] = $(this).data('status-name');
            $("#searchgui-exclude-status").data('word-num');
            context['type'] = 'excluded';
            context['icon'] = 'ban';
            var source = $("#search-gui-added-list-item-template").html();
            var template = Handlebars.compile(source);
            var html = template(context);
            $('#search-gui-excluded-added-list').append(html);


            var addedElement = $('#search-gui-excluded-added-list').find("#" + context['type'] + context['id']);
            addedElement.find(".fa-times").parent().click(function () {
                $('#search-gui-excluded-added-list').find("#" + context['type'] + context['id']).remove();
                var excludeButton = iframe.contents().find('#exclude-status-' + context['id']);
                excludeButton.removeClass('disabled').text('Exclude Me Again!');
                updateSearchGUIObjectsVisibility()
            });
            addedElement.find(".fa-times").parent().hover(function () {
                $(this).toggleClass("alert-danger")
            });
            addedElement.hover(function () {
                $(this).find(".fa-" + context['icon']).parent().toggleClass("alert-success");
                $(this).find(".fa-times").parent().toggleClass("hidden-badge")
            });

            updateSearchGUIObjectsVisibility();
            $(this).addClass('disabled');
            $(this).text('Excluded!');


        });

    });

    // event: adding a word to the advanced filtering
    $("#searchgui-add-word").click(function () {
        if ($('#searchgui-text-input').val().length > 0) {
            var context = {};
            context['name'] = $('#searchgui-text-input').val();
            addWordElementToFilter(context['name'])
        }
    });
    // event: auto-suggest on insertion of text
    $('#searchgui-text-input').bind({
        input: function (event) {
            var inputValue = $('#searchgui-text-input').val();

            url = "/search_bar/?text=" + inputValue;
            if (inputValue.length > 1) {
                $.ajax({
                    url: url,
                    contentType: "application/json",
                    success: function (data) {
                        $('#search-gui-result-list').html('');
                        for (var i = 0; i < data['number_of_results']; i++) {
                            var result = data['results'][i];
                            var resList = $('#search-gui-' + result['type'] + '-added-list').find("#" + result['type'] + result['id']);
                            if (resList.size() > 0) {
                                continue;
                            }
                            var source = $("#search-gui-result-list-item-template").html();
                            if (result['type'] == "member") {
                                result['icon'] = 'user'
                            }
                            else if (result['type'] == "party") {
                                result['icon'] = 'group'
                            }
                            else if (result['type'] == "tag") {
                                result['icon'] = 'tag'
                            }
                            var template = Handlebars.compile(source);
                            var html = template(result);
                            $('#search-gui-result-list').append(html);
                            var addedElement = $('#search-gui-result-list').find("#" + result['type'] + result['id']);

                            // event: when an element is selected
                            addedElement.click(function () {
                                id = $(this).data('id');
                                name = $(this).data('name');
                                type = $(this).data('type');
                                icon = $(this).data('icon');
                                addAutoSuggestElementToFilter(id, name, type, icon)
                            });


                            addedElement.hover(function () {
                                $(this).find(".fa-" + $(this).data('icon')).parent().toggleClass("alert-success");
                                $(this).find(".fa-arrow-left").parent().toggleClass("hidden-badge");
                                $(this).find(".fa-arrow-right").parent().toggleClass("hidden-badge");
                                $(this).find(".fa-arrow-left").parent().toggleClass("alert-info");
                                $(this).find(".fa-arrow-right").parent().toggleClass("alert-info")
                            })
                        }
                    }
                });
            }
        }
    });
});


