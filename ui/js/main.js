function copy(selector) {
    var $temp = $('<div>');
    $('body').append($temp);
    $temp
        .attr('contenteditable', true)
        .html($(selector).html())
        .select()
        .on('focus', function () {
            document.execCommand('selectAll', false, null);
        })
        .focus();
    document.execCommand('copy');
    $temp.remove();
}

function chunkArray(myArray, chunk_size) {
    var index = 0;
    var arrayLength = myArray.length;
    var tempArray = [];
    for (index = 0; index < arrayLength; index += chunk_size) {
        myChunk = myArray.slice(index, index + chunk_size);
        tempArray.push(myChunk);
    }
    return tempArray;
}

$(document).on('keyup', 'input[name=quantity]', function () {
    var _this = $(this);
    var min = parseInt(_this.attr('min')) || 1;
    var max = parseInt(_this.attr('max')) || 100;
    var val = parseInt(_this.val()) || min - 1;
    if (val < min) _this.val(min);
    if (val > max) _this.val(max);
});

$(document).ready(function () {
    $(function () {
        $('#dtpicker').daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            timePicker: true,
            timePicker24Hour: true,
            startDate: moment().startOf('minute').utc(),
            locale: {
                format: 'DD.MM.YYYY. HH:mm'
            }
        });
    });
});

$(function() {
    $("#btn").click(function() {
        if($('#cron_expression').val() == ""){
            $('#cron_expression').addClass("invalid");
            return false;
        }
        else{
            json_data = {};
            $("#result").text("");
            json_data.datetime = $("#dtpicker").val();
            json_data.cron = $("#cron_expression").val();
            json_data.executions = $("#iterations").val();
            $("#modalTitle").text("Next " + json_data.executions + " executions. All times are UTC");
            $.ajax("http://localhost:8000/", {            
                data: JSON.stringify(json_data),
                contentType: "application/json",
                type: "POST",
                dataType: "JSON",
                success: function(data) {
                    $('#modal').modal('show');
                    $("#alert").removeClass("alert-error");
                    $("#cron_expression").removeClass("invalid");
                    var columns = chunkArray(data.cron_ranges, 25);
                    $.each(columns, function(index, column) {
                        lis = "<ol>"; 
                        $.each(column, function(index, element) {
                            lis += "<li>" + element + "</li>"
                        }); 
                        lis += "</ol>"; 
                        $("#result").append(lis);
                    });
                },
                error: function(err){
                    $("#alert").addClass("alert-error");
                    $("#error-message").text(err.responseJSON.message);
                }
            });
        }            
    });
});

$('#cron-examples a').click(function(e) {
  var example_cron = $(e.target).attr('value');
  $('#cron_expression').val(example_cron);
});
