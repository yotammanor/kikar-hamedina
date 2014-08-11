$('#insights').toggle(true);
function int2str(num) {
    return $.isNumeric(num) ? num : 0;
}

function float2str(num) {
    return $.isNumeric(num) ? num.toFixed(1) : 0;
}

$(document).ready(function () {
    member_id = $("#insights").data('objectid');
    $("#insights-loading").removeClass('hidden-updating-spinner');
    $.getJSON('/api/v1/insights/member/' + member_id + '/?format=json', function (data) {
        $("#ins_n_month").text(int2str(data.n_statuses_last_month));
        $("#ins_mean_likes_month").text(float2str(data.mean_status_likes_last_month));
        $("#ins_n_week").text(int2str(data.n_statuses_last_week));
        $("#ins_mean_likes_week").text(float2str(data.mean_status_likes_last_week));
        $("#insights-loading").addClass('hidden-updating-spinner');
        $('#insights').toggle(true);
        return;
    });
});
