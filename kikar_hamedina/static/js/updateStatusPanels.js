// AJAX that updates the stats for every status-panel.
$(document).ready(function () {
    $(".status-panel").each(function (index) {
        status_id = $(this).data("statusid");
        url = "/status_update/" + status_id
        $.ajax({
            url: url,
            contentType: "application/json",
            success: function (data) {
                $("#" + data['id'] + "-likes").text(data['likes'])
                $("#" + data['id'] + "-comments").text(data['comments'])
                $("#" + data['id'] + "-shares").text(data['shares'])
            }
        });
    });
});
