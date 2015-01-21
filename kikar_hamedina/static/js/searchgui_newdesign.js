/**
 * Created by agamrafaeli on 08/01/15.
 */

function searchguiAjaxGetSuggestions(inputValue) {
    url = "/search_bar/?text=" + inputValue
    $.ajax({
        url: url,
        contentType: "application/json",
        success: function (data) {
            $('#searchgui-suggestion-list').html('')
            for (var i = 0; i < data['number_of_results']; i++) {
                var result = data['results'][i]
                result["searchgui_type"] = "suggest-parameter"
                if (result["name"].length > 20) {result["name"] = result["name"].substr(0,25)+"..."}
                var source = $("#searchgui-add-template").html()
                var template = Handlebars.compile(source);
                var html = template(result);
                $('#searchgui-suggestion-list').append(html);

                addedElement = $('#searchgui-suggestion-list').find("#" + result['type'] + result['id'])
                addedElement.click(function() {
                    id = $(this).data('id')
                    name = $(this).data('name')
                    type = $(this).data('type')
                    searchguiAddSuggestToSearchParameters(id,name,type)
                })

            }
        }
    });
}

function searchguiAddSuggestToSearchParameters(id,name,type) {
    entity = {
        "id": id,
        "name": name,
        "type": type,
        "searchgui_type": "search-parameter"
    }
    var source = $("#searchgui-add-template").html()
    var template = Handlebars.compile(source);
    var html = template(entity);
    $("#searchgui-parameters-list").append(html)

    addedElement = $("#searchgui-parameters-list").find("#" + entity['type'] + entity['id'])
    addedElement.click(function() { $(this).remove() })
    $("#searchgui-suggestion-list").find("#" + entity['type'] + entity['id']).remove()

}

function searchguiPostSearch() {
    parties = []
    members = []
    tags = []
    searchParameters = $(".search-parameter")
    for (var i = 0; i < searchParameters.length; i++) {
        parameter = $(searchParameters[i])
        switch (parameter.data("type")) {
            case "member":
                members.push(parameter.data("id"))
                break;
            case "tag":
                tags.push(parameter.data("id"))
                break;
            case "party":
                parties.push(parameter.data("id"))
                break;
        }
    }
    paramatersExist = false
    url = "/search?"
    if (members.length > 0) {
        paramatersExist = true
        url = url + "members="+members.toString()
    }
    if (parties.length > 0) {
        paramatersExist = true
        url = url + "&parties="+parties.toString()
    }
    if (tags.length > 0) {
        paramatersExist = true
        url = url + "&tags="+tags.toString()
    }
    if (paramatersExist) {
        window.location = url
    }
}

$(document).ready(function() {
    $('#searchgui-input').bind({
        input: function (event) {
            inputValue = $('#searchgui-input').val()
            if (inputValue.length > 1) {
                searchguiAjaxGetSuggestions(inputValue)
            }
            else {
                $('#searchgui-suggestion-list').html('')
            }
        }
    });


});