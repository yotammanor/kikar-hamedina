/**
 * Created by yotam on 12/15/2016.
 */


$(document).ready(function () {
    var searchPhrases = getSearchPhrases();
    var markOptions = {acrossElements: true};
    var context = document.querySelectorAll(".status-content");
    for (var i = 0; i < context.length; i++) {
        var instance = new Mark(context[i]);
        for (var j = 0; j < searchPhrases.length; j++)
            instance.mark(searchPhrases[j], markOptions);
    }


});


function getSearchPhrases() {
    var urlVars = getUrlVars();
    return decodeURIComponent(urlVars['search_str']).split(',')
}