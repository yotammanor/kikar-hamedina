/* SearchBar.js - defines the behaviour of the search option that appears
* in the navigation bar. It allows auto-suggest as you type (mk, party, tags)
* and allows for free search.
* */

 function buildURIWithQuotes(SearchURI) {
//  This function receives target-uri for search,
//  extracts input text from search box, add quotes to search string,
//  and returns a ready-to-execute uri path with searc_str parameters.

    var inputText = $("#navbar-search-box").val()
    var url = SearchURI
    var fixed_url = url + '?search_str="' + inputText + '"'
    return fixed_url
}

$(document).ready(function () {
//    $("#navbar-search-box").input(function (event) {
    $("#navbar-search-box").bind({
        input: function (event) {
//          event - when a letter is typed in, the auto-suggest updates
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
                            if (result['type'] == "party") {
                                var source = $("#result-party-list-item-template").html()
                            }
                            else if (result['type'] == "member") {
                                var source = $("#result-member-list-item-template").html()
                            }
                            else if (result['type'] == "tag") {
                                var source = $("#result-tag-list-item-template").html()
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
        },

//      event: Enter-key is pressed while typing - equivalent to submit-search
        keydown: function (event) {
            if (event.which == 13) {
                var uri = buildURIWithQuotes($("#search-bar-submit").data('target'));
                var full_url = window.location.origin + encodeURI(uri);
                window.location.assign(full_url)
            }
        }
    });

// event: click on submit search button
    $("#search-bar-submit").click(function () {
        var uri = buildURIWithQuotes($("#search-bar-submit").data('target'));
        window.location.assign(window.location.origin + encodeURI(uri))
    });
});







