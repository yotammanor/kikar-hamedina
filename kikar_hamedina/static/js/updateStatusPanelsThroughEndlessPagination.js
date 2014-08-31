$.endlessPaginate({
    paginateOnScroll: true,
    paginateOnScrollMargin: 1000,
    paginateOnScrollChunkSize: 10,
    onCompleted: function (context, fragment) {
        console.log('URL:', context.url);
        var new_statuses = $.grep($(fragment), function (elem) {
            return $(elem).is(".status-panel")
        });
        $(new_statuses).each(function (index) {
            status_id = $(this).data("statusid");
            update_status_url = "/status_update/" + status_id + "/"
            $("#status-metrics-is-updating-indicator-" + status_id).removeClass("hidden-object");
            $.ajax({
                url: update_status_url,
                contentType: "application/json",
                success: function (data) {
                    $("#" + data['id'] + "-likes").text(data['likes'])
                    $("#" + data['id'] + "-comments").text(data['comments'])
                    $("#" + data['id'] + "-shares").text(data['shares'])
                    $("#status-metrics-is-updating-indicator-" + data['id']).addClass("hidden-object")
                },
                error: function (data) {
                    $("#status-metrics-is-updating-indicator-" + data['id']).addClass("hidden-object");
                    $("#status-metrics-is-error-indicator-" + data['id']).removeClass("hidden-object");
                }
            });
        });
    }
});