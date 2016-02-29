/* addTagToStatus.js - handles adding of tags to posts.
 * has auto-suggest capabilities, and handles the ajax-based process
 * of adding the selected tags to the status.
 *
 */

function showAddTagError(status_id, error_msg) {
    $("#add-tag-error-msg-" + status_id).text('Error: ' + (error_msg || ''));
    $("#add-tag-error-" + status_id).show();
}

function addTag(status_id, tag_name, csrf_token) {
    /*
     The ajax request to add a particular tag, based on received input.
     */
    var add_tag_uri = "/add_tag_to_status/?id=" + status_id + "&tag_str=" + tag_name + "&csrftoken=" + csrf_token
    console.log(add_tag_uri);
    $.ajax({
        url: add_tag_uri,
        contentType: "application/json",
        success: function (data) {
//            console.log("GOT RESPONSE")
//            console.log(data)
            if (data['success']) {
                tag = data['tag'];
                console.log(tag);
                var source = $("#add-tag-to-status-template").html();
                var template = Handlebars.compile(source);
                var html = template(tag);
                console.log("html: " + html);
                $("#" + data['id'] + "-tags").prev().css("display", "inline");
                $("#" + data['id'] + "-tags").append(html)
            } else {
                console.log(data);
                console.log("ERROR AT SERVER");
                showAddTagError(status_id, data["error"]);
            }
        },
        error: function (data) {
            console.log("BADDDDD ERROR!!");
            showAddTagError(status_id, "internal error");
        }
    });
}

function addAutosuggestAjaxTags(data, status_id_on_page, recommended) {
    /*
        @param data - has the returned suggested tags from an Ajax call
        @param status_id_on_page - has the id of the status to add the suggested tags to the autocomplete section
                                    of its tag input field
     */
    $('#add-tag-dropdown-' + status_id_on_page).removeClass('open');
    addTagListElem = $('#add-tag-list-' + status_id_on_page);
    addTagListElem.html('');
    for (var i = 0; i < data['number_of_results']; i++) {
        if (data['results'][i]['type'] != 'tag') {
            continue;
        }
        var result = data['results'][i];
        result['recommended'] = recommended;
        var source = $("#add-tag-result-tag-list-item-template").html();
        var template = Handlebars.compile(source);
        var html = template(result);
        addTagListElem.append(html)
    }
    if (data['number_of_results'] > 0) {
        $('#add-tag-dropdown-' + status_id_on_page).addClass("open")
    }
    // handler for adding the tag from suggestion list
    $(".add-tag-from-list").bind({
        click: function () {
            console.log("adding tag");
            tag_to_add = $(this);
//                        var status_id = tag_to_add.data('status-id');
            var tag_name = tag_to_add.data('tag-name');
            console.log(status_id_on_page + ' ' + tag_name);
            addTag(status_id_on_page, tag_name, csrf_token);
            $('#add-tag-list-' + status_id_on_page).html('');
            obj.val("")
        }
    });
}

function tagAddingHandler(obj) {
    /*
     adds auto-suggests and activates handler
     for adding status from auto-suggest.
     */
    inputText = obj.val();
    var id = obj.parent().parent().data("statusid");
    var csrf_token = obj.parent().siblings("[name=csrfmiddlewaretoken]").attr('value');
    if (inputText.length > 1) {
        // auto-suggest ajax request based on text in the input
        $.ajax({
            url: "/search_bar/?text=" + inputText,
            contentType: "application/json",
            success: function (data) {
                addAutosuggestAjaxTags(data, id, false)
            },
        });
        obj.data("empty","True")
    }
    else if (inputText.length <= 1  && obj.is(":focus")) {
        if (inputText.length == 0) {

        }


        //This if is here so that the AJAX call is made just once when the
        //input is empty
        if (obj.data("empty") == "True") {
            // auto-suggest ajax request based on suggested tags
            $.ajax({
                url: "/suggested_tags/" + obj.data("statusid"),
                contentType: "application/json",
                success: function (data) {
                    addAutosuggestAjaxTags(data, id, true)
                }
            });
            obj.data("empty","False")
        }
    }
    else {
        $('#add-tag-list-' + id).html('')
    }
}

function removeAutocompleteTags(obj) {
    var id = obj.parent().parent().data("statusid");
    $('#add-tag-list-' + id).html('');
    obj.data("empty","True")
}

$(document).ready(function () {
    $("div.row").on("click", ".add-tag-button", function (event) {
        // event: clicking on the add-tag button
        console.log("adding tag");
        id = $(this).parent().parent().data("statusid");
        tag = $(this).parent().parent().find(".add-tag-input");
        csrf_token = $(this).parent().siblings("[name=csrfmiddlewaretoken]").attr('value');
        var tags = (String(tag.val())).split(",");
        tag.val("");
        console.log(tag.val());
        console.log(tags);

        for (var t in tags) {
            addTag(id, tags[t], csrf_token)
        }
    }).on("input", ".add-tag-input", function (event) {
        // event - text is inserted or focus is returned to tag input.
        //
        //         * Aimed  at opening and populating list  of auto-suggest.
//        $('#add-tag-dropdown').removeClass("open")
        tagAddingHandler($(this))
    }).on("focusin", ".add-tag-input", function (event) {
        tagAddingHandler($(this))
    }).on("click", ".add-tag-input", function (event) {
        tagAddingHandler($(this))
    }).on("focusout", ".add-tag-input", function (event) {
        removeAutocompleteTags($(this))
    }).on("click", ".add-tag-error-close", function (event) {
        $(this).parent().hide()
    });
});
