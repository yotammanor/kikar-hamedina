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
        selectedIndex = -1; // selected search result: -1 means nothing is selected.

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
                            resultList = $('.result-container a');
                            selectedIndex = -1;
                        }
                    }
                });
            }

        },

        // event: Enter-key pressed while typing - equivalent to submit-search.
        //        Enter-key pressed while selecting search result - go to search result
        //        Up / Down keys - navigation between search results

        keydown: function (event) {
          var uri, full_url;
          switch ( event.which ) {
            case 13:
                if ( selectedIndex > -1 ) {
                  full_url = $('.active-result').attr('href');
                }
                else {
                  uri = buildURIWithQuotes($("#search-bar-submit").data('target'));
                  full_url = window.location.origin + encodeURI(uri);
                }
                window.location.assign(full_url)
                break;

            case 40:
                setSelectedIndex(selectedIndex + 1);
                break;

            case 38:
                setSelectedIndex(selectedIndex - 1);
                break;
          }
        }

    });


    // event: Click on submit search button
    $("#search-bar-submit").click(function () {
        var uri = buildURIWithQuotes($("#search-bar-submit").data('target'));
        window.location.assign(window.location.origin + encodeURI(uri))
    });

    // sets the focus on the next/previous search result
    function setSelectedIndex(i) {

      // if a result has been already selected
      if ( selectedIndex > -1 ) {
        resultList[selectedIndex].className = '';
      }

      // end of result list - set to first result
      if ( i == resultList.length) {
        i = 0;
      }

      // first result - set to last result
      if ( i < 0 ) {
        i = resultList.length - 1;
      }

      resultList[i].className = 'active-result';
      selectedIndex = i;
    }
});
