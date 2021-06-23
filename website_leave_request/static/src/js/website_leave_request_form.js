odoo.define('website_leave_request.website_leave_request_form', function(require) {
    'use strict';

    const rpc = require('web.rpc');
    const ajax = require('web.ajax');

    $(document).ready(function() {
        $("#holiday_status_id").change(function() {
            if (!$('#request_date_to').val() && $('#request_date_from').val()) {
                $("#number_of_days").val(0.00);
                $("#number_of_hours").val(0);
                $(".datetime_duration").val("");
            } else if ($('#request_date_to').val() && $('#request_date_from').val()) {
                backend_calculation();
            }
            $("#request_date_to").prop('required', false);
            $(".date_from").removeClass("col-sm-4");
            $(".date_from").addClass("col-sm-2");
            $(".duration_div").show();
            $(".from_label").css("display", "block");
            $(".to_label").css("display", "block");
            $(".date_to").css("display", "block");
            $(".date_to").attr('required', true);
            $(".date_from").attr('required', true);
            $("#number_of_hours_text").removeClass("ml-3");
            $("#request_date_from_period").val("");
            $("#request_hour_from").prop('required', false);
            $("#request_hour_to").prop('required', false);
            $("#request_unit_half").val(false);
            $("#request_unit_hours").val(false);
            $("#request_unit_custom").val(true);
            rpc.query ({
                model: 'hr.leave.type',
                method: 'search_read' ,
                args: [[['id', '=', Number($(this).val())]], ['request_unit']],
            }). then ( function (data) {
                var request_unit = data[0].request_unit;
                if (request_unit == 'day') {
                    $("#request_unit_half").prop("checked", false);
                    $("#request_unit_hours").prop("checked", false);
                    $("#request_unit_custom").val(true);
                    $(".leave_checkbox").css("display", "none");
                    $(".custom_hours").css("display", "none");
                    $("#number_of_hours_text").css("display", "none");
                    $("#request_date_from_period").css("display", "none");
                    $("#request_date_from_period").val("");
                    $("#request_date_from_period").prop('required', false);
                    $(".duration").removeClass("col-sm-3");
                    $(".duration").addClass("col-sm-4");
                    $(".duration_days").css("display", "block");
                    $("#request_hour_to").val("");
                    $("#request_hour_from").val("");
                } else if (request_unit == 'hour') {
                    $(".leave_checkbox").css("display", "block");
                    $(".custom_hours_checkbox").show();
                    $(".duration").removeClass("col-sm-4");
                    $(".duration").addClass("col-sm-3");
                    $("#number_of_hours_text").css("display", "block");
                    $("#number_of_hours_text").val("(" + $("#number_of_hours").val() + " Hours)");
                } else {
                    $(".leave_checkbox").css("display", "block");
                    $(".duration_days").css("display", "block");
                    $(".custom_hours_checkbox").css("display", "none");
                    $(".custom_hours").css("display", "none");
                    $("#number_of_hours_text").css("display", "none");
                }
            });
        });
        $(".form-check-input").on("change", function() {
            $(".datetime_duration").val("");
            if ($("#request_unit_half").is(':checked') || $("#request_unit_hours").is(':checked')) {
                $("#request_unit_custom").val(false);
                $(".from_label").css("display", "none");
                $(".to_label").css("display", "none");
                $(".date_to").css("display", "none");
                $(".date_to").prop('required', false);
                $(".duration_days").css("display", "none");
                $(".date_from").addClass("ml-3");
                $("#number_of_hours_text").addClass("ml-3");
                $(".date_to").val("");
            } else {
                $("#request_unit_custom").val(true);
                $(".from_label").css("display", "block");
                $(".to_label").css("display", "block");
                $(".date_to").css("display", "block");
                $(".date_to").attr('required', true);
                $(".duration_days").css("display", "block");
                $("#request_date_from_period").css("display", "none");
                $("#request_date_from_period").val("");
                $("#request_date_from_period").prop('required', false);
                $(".custom_hours").hide();
                $("#request_hour_from").prop('required', false);
                $("#request_hour_to").prop('required', false);
                $(".date_from").removeClass("ml-3");
                $(".date_from").removeClass("col-sm-4");
                $(".date_from").addClass("col-sm-2");
                $("#number_of_hours_text").removeClass("ml-3");
                $("#request_hour_to").val("");
                $("#request_hour_from").val("");
            }
        });
        $("#request_unit_half").on("change", function() {
            $(".duration_div").show();
            if ($(this).is(':checked') && $(".custom_hours_checkbox").css("display") == 'none') {
                $(".duration_div").css("display", "none");
            }
            if ($(this).is(':checked')) {
                $("#number_of_hours_text").val("0 Hours");
                $("#request_unit_hours").prop("checked", false);
                $("#request_unit_hours").val(false);
                $(".custom_hours").css("display", "none");
                $("#request_hour_from").prop('required', false);
                $("#request_hour_to").prop('required', false);
                $(".date_to").prop('required', false);
                $("#request_date_from_period").css("display", "block");
                $("#request_date_from_period").attr('required', true);
                $(".date_from").removeClass("col-sm-4");
                $(".date_from").addClass("col-sm-2");
                $("#request_hour_to").val("");
                $("#request_hour_from").val("");
                $(this).val(true);
            } else {
                $("#number_of_days").val(0.00);
                $("#number_of_hours").val(0);
                $("#request_date_from_period").css("display", "none");
                $("#request_date_from_period").val("");
                $("#request_date_from_period").prop('required', false);
                $(".date_to").attr('required', true);
                $(this).val(false);
            }
        });
        $("#request_unit_hours").on("change", function() {
            if ($(this).is(':checked')) {
                $("#number_of_hours_text").val("0 Hours");
                $("#request_unit_half").prop("checked", false);
                $("#request_unit_half").val(false);
                $("#request_date_from_period").css("display", "none");
                $("#request_date_from_period").val("");
                $("#request_date_from_period").prop('required', false);
                $(".date_to").prop('required', false);
                $(".custom_hours").show();
                $("#request_hour_from").attr('required', true);
                $("#request_hour_to").attr('required', true);
                $(".date_from").removeClass("col-sm-2");
                $(".date_from").addClass("col-sm-4");
                $(this).val(true);
            } else {
                $("#number_of_days").val(0.00);
                $("#number_of_hours").val(0);
                $(".custom_hours").hide();
                $(".date_to").attr('required', true);
                $("#request_hour_from").prop('required', false);
                $("#request_hour_to").prop('required', false);
                $(this).val(false);
            }
        });
        $("#request_date_from").on("change", function() {
            if ($("#request_hour_from").val() && $("#request_hour_to").val()) {
                backend_calculation();
            } else if ($("#request_unit_half").is(':checked')) {
                checkHalfDay();
            } else if (!$("#request_unit_half").is(':checked') && !$("#request_unit_hours").is(':checked')) {
                checkFromToDate();
            }
        });
        $("#request_date_from_period").on("change", function() {
            checkHalfDay();
        });
        $("#request_date_to").on("change", function() {
            checkFromToDate();
        });
        $("#request_hour_from").on("change", function() {
            if ($("#request_hour_from").val() && $("#request_hour_to").val()) {
                if (!checkCustomHours()) {
                    $(this).val("");
                }
            }
        });
        $("#request_hour_to").on("change", function() {
            if ($("#request_hour_from").val() && $("#request_hour_to").val()) {
                if (!checkCustomHours()) {
                    $(this).val("");
                }
            }
        });
        function backend_calculation() {
            ajax.jsonRpc("/leave_requests/new_request_validate", 'call', {
                'request_date_from_period': $('#request_date_from_period').val(),
                'holiday_status_id': $('#holiday_status_id').val(),
                'request_hour_from': $('#request_hour_from').val(),
                'request_hour_to': $('#request_hour_to').val(),
                'request_date_from': $('#request_date_from').val(),
                'request_date_to': $('#request_date_to').val(),
                'request_unit_half': $('#request_unit_half').val(),
                'request_unit_hours': $('#request_unit_hours').val(),
                'request_unit_custom': $('#request_unit_custom').val(),
                'number_of_hours':$("#number_of_hours").val(),
                'number_of_hours_text': $('#number_of_hours_text').val(),
            }).then(function (data) {
                if (data) {
                    if (data['checks'] == "exists") {
                        $('#check_date_alert').show();
                    } else if (data['checks'] == "over") {
                        $('#check_holiday_alert').show();
                    } else {
                        $('#check_date_alert').hide();
                        $('#check_holiday_alert').hide();
                        $('#date_from').val(data['date_from']);
                        $('#date_to').val(data['date_to']);
                        $('#number_of_days').val(data['number_of_days'].toFixed(2));
                        $('#number_of_hours').val(data['number_of_hours']);
                        $('#number_of_hours_text').val(data['number_of_hours_text']);
                    }
                }
            });
        }
        function checkFromToDate() {
            if ($("#request_date_from").val() && $("#request_date_to").val()) {
                var date_from = new Date($("#request_date_from").val());
                var date_to = new Date($("#request_date_to").val());
                if (date_from > date_to) {
                    $("#request_date_to").val($("#request_date_from").val())
                }
                backend_calculation();
            }
        }
        function checkHalfDay() {
            if ($("#request_date_from").val() && $("#request_date_from_period").val()) {
                backend_calculation();
            }
        }
        function checkCustomHours() {
            var hour_from = $("#request_hour_from").val();
            var hour_to = $("#request_hour_to").val();
            if (eval(hour_from + " < " + hour_to)){
                $("#number_of_hours").val(eval(hour_to - hour_from));
                if ($("#request_date_from").val()) {
                    backend_calculation();
                }
                return true;
            } else {
                alert("The start time must be anterior to the end time.");
                return false;
            }
        }
    });
});