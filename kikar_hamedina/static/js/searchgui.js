/* SearchGui.js - defines the behaviour of the advanced search interface.
 *  It allows auto-suggest as you type (mk, party, tags),
 * allows for free search, lets you set advanced filtering and order-by.
 * */

function buildURL(baseURL) {
    var url;
    var searchTerms = {'member': [], 'party': [], 'tag': [], 'search_str': [], 'excluded': []};
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
    var dateRange = $('#range-option').val();
    url += "tags_and_search_str_operator=" + operator + "&order_by=" + orderBy + "&range=" + dateRange;
    console.log(url);
    return url
}

function addAutoSuggestElementToFilter(id, name, type, icon) {
    /* This function adds a selected auto-suggest option to applied filters.
     *
     * */
    var source = $("#search-gui-added-list-item-template").html();
    var template = Handlebars.compile(source);
    context = {'id': id, 'name': name, 'type': type, 'icon': icon};
    var html = template(context);
    $('#search-gui-' + type + '-added-list').append(html);
    addedElement = $('#search-gui-' + type + '-added-list').find("#" + type + id);
    addedElement.find(".glyphicon-remove").parent().click(function () {
        id = $(this).data('id');
        type = $(this).data('type');
        removeSelectedFilterElement(id, type)
    });
    addedElement.find(".glyphicon-remove").parent().hover(function () {
        $(this).toggleClass("alert-danger")
    });
    addedElement.hover(function () {
        $(this).find(".glyphicon-" + icon).parent().toggleClass("alert-success");
        $(this).find(".glyphicon-remove").parent().toggleClass("hidden-badge");
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
    var searchTerms = {'member': [], 'party': [], 'tag': [], 'search_str': [], 'excluded': []};
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
//  cleans results list at loading.
    $(".glyphicon-trash").parent().click(function () {
        $('#searchgui-text-input').val('');
        $('#search-gui-result-list').html('');
        $('#search-gui-member-added-list').html('');
        $('#search-gui-party-added-list').html('');
        $('#search-gui-tag-added-list').html('')
    });

    $('#searchgui-save-button').click(function () {
        var query = $('#form-query');
        var url = buildURL("/search/");
        query.html(url);
        //console.log(modal)
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
            console.log($(this).data('status-id'));

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
            addedElement.find(".glyphicon-remove").parent().click(function () {
                $('#search-gui-excluded-added-list').find("#" + context['type'] + context['id']).remove();
                var excludeButton = iframe.contents().find('#exclude-status-' + context['id']);
                excludeButton.removeClass('disabled').text('Exclude Me Again!');
                updateSearchGUIObjectsVisibility()
            });
            addedElement.find(".glyphicon-remove").parent().hover(function () {
                $(this).toggleClass("alert-danger")
            });
            addedElement.hover(function () {
                $(this).find(".glyphicon-" + context['icon']).parent().toggleClass("alert-success");
                $(this).find(".glyphicon-remove").parent().toggleClass("hidden-badge")
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
            context['id'] = $('#searchgui-text-input').val();
            $(this).data('word-num', context['id'] + 1);
            console.log($(this).data('word-num'));
            context['type'] = 'search_str';
            context['icon'] = 'comment';
            var source = $("#search-gui-added-list-item-template").html();
            var template = Handlebars.compile(source);
            var html = template(context);
            $('#searchgui-search-words').append(html);

            var addedElement = $('#searchgui-search-words').find("#" + context['type'] + context['id']);
            addedElement.find(".glyphicon-remove").parent().click(function () {
                $('#searchgui-search-words').find("#" + context['type'] + context['id']).remove();
                updateSearchGUIObjectsVisibility()
            });
            addedElement.find(".glyphicon-remove").parent().hover(function () {
                $(this).toggleClass("alert-danger")
            });
            addedElement.hover(function () {
                $(this).find(".glyphicon-" + context['icon']).parent().toggleClass("alert-success");
                $(this).find(".glyphicon-remove").parent().toggleClass("hidden-badge")
            });


            $('#searchgui-text-input').val('');
            updateSearchGUIObjectsVisibility()
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
                                $(this).find(".glyphicon-" + $(this).data('icon')).parent().toggleClass("alert-success");
                                $(this).find(".glyphicon-arrow-left").parent().toggleClass("hidden-badge");
                                $(this).find(".glyphicon-arrow-left").parent().toggleClass("alert-info")
                            })
                        }
                    }
                });
            }
        }
    });
});


