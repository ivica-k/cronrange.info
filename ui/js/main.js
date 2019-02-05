function copy(t) {
    var n = $("<div>");
    $("body").append(n), n.attr("contenteditable", !0).html($(t).html()).select().on("focus", function() {
        document.execCommand("selectAll", !1, null)
    }).focus(), document.execCommand("copy"), n.remove()
}

function chunkArray(t, n) {
    var e = 0,
        a = t.length,
        o = [];
    for (e = 0; e < a; e += n) myChunk = t.slice(e, e + n), o.push(myChunk);
    return o
}
$(document).on("keyup", "input[name=quantity]", function() {
    var t = $(this),
        n = parseInt(t.attr("min")) || 1,
        e = parseInt(t.attr("max")) || 100,
        a = parseInt(t.val()) || n - 1;
    a < n && t.val(n), e < a && t.val(e)
}), $(document).ready(function() {
    $(function() {
        $("#dtpicker").daterangepicker({
            singleDatePicker: !0,
            showDropdowns: !0,
            timePicker: !0,
            timePicker24Hour: !0,
            startDate: moment().startOf("minute"),
            endDate: moment().startOf("hour").add(32, "hour"),
            locale: {
                format: "DD.MM.YYYY. HH:mm"
            }
        })
    })
}), $(function() {
    $("#btn").click(function() {
        if ("" == $("#cron_expression").val()) return $("#cron_expression").addClass("invalid"), !1;
        json_data = {}, $("#result").text(""), json_data.datetime = $("#dtpicker").val(), json_data.cron = $("#cron_expression").val(), json_data.executions = $("#iterations").val(), $("#modalTitle").text("Next " + json_data.executions + " executions"), $.ajax("http://localhost:8000/", {
            data: JSON.stringify(json_data),
            contentType: "application/json",
            type: "POST",
            dataType: "JSON",
            success: function(t) {
                $('#modal').modal('show');
                $("#alert").removeClass("alert-error");
                $("#cron_expression").removeClass("invalid");
                var e = chunkArray(t.cron_ranges, 25);
                $.each(e, function(t, n) {
                    lis = "<ol>", $.each(n, function(t, n) {
                        lis += "<li>" + n + "</li>"
                    }), lis += "</ol>", $("#result").append(lis), e.length <= 1 ? $("ol").addClass("one-column") : e.length <= 2 ? $("ol").addClass("two-columns") : e.length <= 3 && $("ol").addClass("three-columns")
                })
            },
            error: function(err){
                $("#alert").addClass("alert-error");
                $("#error-message").text(err.responseJSON.message);
            }
        })
    })
});