// AJAX that updates the stats for every status-panel.
$(document).ready(function () {
    $(".status-panel").each(function (index) {
        status_id = $(this).data("statusid");
        url = "/status_update/" + status_id + "/"
        $("#status-metrics-is-updating-indicator-" + status_id).removeClass("hidden-updating-spinner");
        $.ajax({
            url: url,
            contentType: "application/json",
            success: function (data) {
                $("#" + data['id'] + "-likes").text(data['likes'])
                $("#" + data['id'] + "-comments").text(data['comments'])
                $("#" + data['id'] + "-shares").text(data['shares'])
                $("#status-metrics-is-updating-indicator-" + data['id']).addClass("hidden-updating-spinner");
            }
        });
    });
});
