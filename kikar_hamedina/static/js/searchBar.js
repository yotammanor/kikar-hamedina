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

    var resultList, // search results jQuery object
        tabindex;

    $("#navbar-search-box").bind({
        // event: When a letter is typed in, the auto-suggest updates
        input: function (event) {
            $('#search-results-dropdown').removeClass("open")
            inputText = $("#navbar-search-box").val()
            url = "/search_bar/?text=" + inputText
            if (inputText.length > 1) {
                $.ajax({
                    url: url,
                    contentType: "application/json",
                    success: function (data) {
                        tabindex = 0; // only first result is focusable
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

                            if ( i > 0 && tabindex == 0 ) {
                              tabindex = -1;
                            }
                            result['tabindex'] = tabindex;

                            var template = Handlebars.compile(source);
                            var html = template(result);
                            $('#search-results-list').append(html)
                        }
                        if (data['number_of_results'] > 0) {
                            $('#search-results-dropdown').addClass("open")
                            resultList = $('.result-container a');
                        }
                    }
                });
            }

        },

        // event: Enter-key is pressed while typing - equivalent to submit-search
        keydown: function (event) {
            if (event.which == 13) {
                var uri = buildURIWithQuotes($("#search-bar-submit").data('target'));
                var full_url = window.location.origin + encodeURI(uri);
                window.location.assign(full_url)
            }
        }
    });

    // event: Up / Down keys navigation in search results
    $("#search-results-list").bind('keydown', focusController);

    // event: Click on submit search button
    $("#search-bar-submit").click(function () {
        var uri = buildURIWithQuotes($("#search-bar-submit").data('target'));
        window.location.assign(window.location.origin + encodeURI(uri))
    });


    var key, currentIndex, previousElm, nextElm;
    function focusController(e) {
    // Resets the tabindex for the current focused element and sets
    // the tabindex for the next/previous element + focuses it

        // finds current focused element
        resultList.each(function(i, elm) {
          if ( elm.getAttribute('tabindex') == 0 ) {
            currentIndex = i;
            return false;
          }
        });

        thisElm = resultList[currentIndex];
        nextElm = resultList[currentIndex + 1];
        prevElm = resultList[currentIndex - 1];

        key = e.which;

        switch ( key ) {
          case 40:
            e.preventDefault();
            if ( nextElm ) {
              thisElm.setAttribute('tabindex', -1);
              nextElm.setAttribute('tabindex', 0);
              nextElm.focus();
            }
            break;

          case 38:
            e.preventDefault();
            if ( prevElm ) {
              thisElm.setAttribute('tabindex', -1);
              prevElm.setAttribute('tabindex', 0);
              prevElm.focus();
            }
            break;
        }
    }
});
