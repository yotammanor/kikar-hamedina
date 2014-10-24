/* addTagToStatus.js - handles adding of tags to posts.
 * has auto-suggest capabilities, and handles the ajax-based process
 * of adding the selected tags to the status.
 *
 */

function addTag(status_id, tag_name, csrf_token) {
    /*
     The ajax request to add a particular tag, based on received input.
     */
    var add_tag_uri = "/add_tag_to_status/?id=" + status_id + "&tag_str=" + tag_name + "&csrftoken=" + csrf_token
    console.log(add_tag_uri)
    $.ajax({
        url: add_tag_uri,
        contentType: "application/json",
        success: function (data) {
//            console.log("GOT RESPONSE")
//            console.log(data)
            if (data['success']) {
                tag = data['tag']
                console.log(tag)
                var source = $("#add-tag-to-status-template").html()
                var template = Handlebars.compile(source);
                var html = template(tag);
                console.log("html: " + html)
                $("#" + data['id'] + "-tags").prev().css("display", "inline")
                $("#" + data['id'] + "-tags").append(html)
            }
            else {
                console.log(data)
                console.log("ERROR AT SERVER")
            }
        },
        error: function (data) {
            console.log("BADDDDD ERROR!!")
        }
    });
};

function tagAddingHandler(obj) {
    /*
     adds auto-suggests and activates handler
     for adding status from auto-suggest.
     */
    inputText = obj.val();
    var id = obj.parent().parent().data("statusid");
    var csrf_token = obj.parent().siblings("[name=csrfmiddlewaretoken]").attr('value');
    add_tag_url = "/search_bar/?text=" + inputText;

    if (inputText.length > 1) {
        // auto-suggest ajax request
        $.ajax({
            url: add_tag_url,
            contentType: "application/json",
            success: function (data) {
                $('#add-tag-dropdown-' + id).removeClass('open')
                addTagListElem = $('#add-tag-list-' + id)
                addTagListElem.html('')
                for (var i = 0; i < data['number_of_results']; i++) {
                    if (data['results'][i]['type'] != 'tag') {
                        continue;
                    }
                    var result = data['results'][i]
                    var source = $("#add-tag-result-tag-list-item-template").html()
                    var template = Handlebars.compile(source);
                    var html = template(result);
                    addTagListElem.append(html)
                }
                if (data['number_of_results'] > 0) {
                    $('#add-tag-dropdown-' + id).addClass("open")
                }

                // handler for adding the tag from suggestion list
                $(".add-tag-from-list").bind({
                    click: function () {
                        console.log("adding tag");
                        tag_to_add = $(this);
//                        var status_id = tag_to_add.data('status-id');
                        var tag_name = tag_to_add.data('tag-name');
                        console.log(id + ' ' + tag_name);
                        addTag(id, tag_name, csrf_token);
                        $('#add-tag-list-' + id).html('')
                        obj.val("")

                    }
                });
            },
            error: function (data) {
                console.log("BADDDDD ERROR!!")
                console.log(data)
            }

        });
    }
    else {
        // clean suggestion list
        $('#add-tag-list-' + id).html('')
    }
}


$(document).ready(function () {
    // event: clicking on the add-tag button
    $(".add-tag-button").click(function () {
        console.log("adding tag");
        id = $(this).parent().parent().data("statusid");
        tag = $(this).parent().parent().find(".add-tag-input");
        csrf_token = $(this).parent().siblings("[name=csrfmiddlewaretoken]").attr('value');
        var tags = (String(tag.val())).split(",");
        tag.val("");
        console.log(tag.val());
        console.log(tags);

        for (t in tags) {
            addTag(id, tags[t], csrf_token)
        }

    });
    // event - text is inserted or focus is returned to tag input.
    //
    //         * Aimed  at opening and populating list  of auto-suggest.
    $(".add-tag-input").bind({
        input: function (event) {
//        $('#add-tag-dropdown').removeClass("open")
            tagAddingHandler($(this))
        } //,

//        focusin: function (event) {
//            tagAddingHandler($(this))
//        }
    });
});
