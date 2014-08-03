$(document).ready(function () {
    $("#navbar-search-box").keydown(function (event) {
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
    });
    $("#search-bar-submit").click(function () {
        var inputText = $("#navbar-search-box").val()
        var url = $("#search-bar-submit").data('target')
        alert(url)
        var fixed_url = url+'?search_str="'+ inputText +'"'
        alert(fixed_url)

        window.location.assign(encodeURI(fixed_url))

    });
})






