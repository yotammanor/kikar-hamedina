// AJAX that updates the stats for every status-panel.
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

$(document).ready(function () {
    // For each status content element
    $('.status-content').each(function () {
        var that = this;
        // For each paragraph in content element
        $(this).children().each(function () {
            if (isUnicode($(this).text().trim())) {
                $(this).css('direction', 'rtl');
            } else {
                $(this).css('direction', 'ltr');
            }
        });
    });

    $(".status-needs-refresh").each(function (index) {
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
            error: function (jqXHR, textStatus, errorThrown) {
//                console.log(jqXHR);
                $("#status-metrics-is-updating-indicator-" + status_id).hide();
                $("#status-metrics-is-error-indicator-" + status_id).show()
            }
        });
    });
});
