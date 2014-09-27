// AJAX that updates the stats for every status-panel.
$(document).ready(function () {
    $(".status-panel").each(function (index) {
        var status_id = $(this).data("statusid");
        update_status_url = "/status_update/" + status_id + "/";
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
