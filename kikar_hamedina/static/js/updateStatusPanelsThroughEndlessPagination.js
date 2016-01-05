function isUnicode(str) {
    var ignoreCharacters = [8211, 8217, 8220, 8221];
    var letters = [];
    for (var i = 0; i <= str.length; i++) {
        letters[i] = str.substring((i - 1), i);
        if (letters[i].charCodeAt() > 255) {
            if ($.inArray(letters[i].charCodeAt(), ignoreCharacters) == -1) {
                //console.log(letters[i]);
                //console.log(letters[i].charCodeAt());
                return true;
            }
        }

    }
    return false;
}


$.endlessPaginate({
    paginateOnScroll: true,
    paginateOnScrollMargin: 1000,
    paginateOnScrollChunkSize: 10,
    onCompleted: function (context, fragment) {
        $(fragment).children().each(function () {
            $('.status-content p').each(function () {
                if (isUnicode($(this).text())) {
                    $(this).css('direction', 'rtl');
                } else {
                    $(this).css('direction', 'ltr');
                }
            });
        });

//        fragment is a div#status-list-container, with some of its children the
//        relevant .status-panel objects.
//
//        Structure of fragment is set at core/templates/core/facebook_status_list.html
//

        var new_statuses = $.grep($(fragment).children(), function (elem) {
            return $(elem).is(".status-needs-refresh")
        });
        $(new_statuses).each(function (index) {
            // For each status content element
            var status_id = $(this).data("statusid");
            var update_status_url = "/status_update/" + status_id + "/";
            $("#status-metrics-is-updating-indicator-" + status_id).show();
            $.ajax({
                url: update_status_url,
                contentType: "application/json",
                success: function (data) {
                    $("#" + data['id'] + "-likes").text(data['likes']);
                    $("#" + data['id'] + "-comments").text(data['comments']);
                    $("#" + data['id'] + "-shares").text(data['shares']);
                    $("#status-metrics-is-updating-indicator-" + data['id']).hide()
                },
                error: function (data) {
                    $("#status-metrics-is-updating-indicator-" + data['id']).hide();
                    $("#status-metrics-is-error-indicator-" + data['id']).show();
                }
            });

        });
        FB && FB.XFBML.parse(); // Update new embedded posts etc.
    }
});