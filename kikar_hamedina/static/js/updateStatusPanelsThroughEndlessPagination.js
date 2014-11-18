$.endlessPaginate({
    paginateOnScroll: true,
    paginateOnScrollMargin: 1000,
    paginateOnScrollChunkSize: 10,
    onCompleted: function (context, fragment) {
//        fragment is a div#status-list-container, with some of its children the
//        relevant .status-panel objects.
//
//        Structure of fragment is set at core/templates/core/facebook_status_list.html
//
        var new_statuses = $.grep($(fragment).children(), function (elem) {
            return $(elem).is(".status-needs-refresh")
        });
        $(new_statuses).each(function (index) {
            status_id = $(this).data("statusid");
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
                error: function (data) {
                    $("#status-metrics-is-updating-indicator-" + data['id']).hide();
                    $("#status-metrics-is-error-indicator-" + data['id']).show();
                }
            });
        });
    }
});