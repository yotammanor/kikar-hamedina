$(document).ready(function () {
    $("#navbar-search-box").keydown(function (event) {
        if (event.which == 13) {
            var uri = add_quotes($("#search-bar-submit").data('target'));
            var full_url = window.location.origin + encodeURI(uri);
            window.location.assign(full_url)

        } else {
            $('#search-results-dropdown').removeClass("open")
            inputText = $("#navbar-search-box").val()
            url = "/search_bar/?text=" + inputText
            if (inputText.length > 1) {
                $.ajax({
                    url: url,
                    contentType: "application/json",
                    success: function (data) {
                        $('#search-results-list').html('')
                        for (var i = 0; i < data['number_of_results']; i++) {
                            var result = data['results'][i]
                            if (result['type'] == "member") {
                                var source = $("#result-member-list-item-template").html()
                            }
                            else if (result['type'] == "tag") {
                                var source = $("#result-tag-list-item-template").html()
                            }
                            else if (result['type'] == "party") {
                                var source = $("#result-party-list-item-template").html()
                            }
                            var template = Handlebars.compile(source);
                            var html = template(result);
                            $('#search-results-list').append(html)
                        }
                        if (data['number_of_results'] > 0) {
                            $('#search-results-dropdown').addClass("open")
                        }
                    }
                });
            }
        }
    });

    $("#search-bar-submit").click(function () {
        var uri = add_quotes($("#search-bar-submit").data('target'));
        window.location.assign(window.location.origin + encodeURI(uri))
    });
});

function add_quotes(SearchURI) {
    var inputText = $("#navbar-search-box").val()
    var url = SearchURI
    var fixed_url = url + '?search_str="' + inputText + '"'
    return fixed_url
}





