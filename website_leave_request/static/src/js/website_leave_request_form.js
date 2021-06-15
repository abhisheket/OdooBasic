odoo.define('website_leave_request.website_leave_request_form', function(require) {
    'use strict';

    $(document).ready(function() {
        $("#holiday_status_id").change(function() {
            if ($(this).val() == 1 || $(this).val() == 2) {
                $('#request_unit_half').prop('checked', false);
                $("#request_unit_hours").prop('checked', false);
                $(".leave-checkbox").css("display", "none");
                $(".date_to").css("display", "none");
                $(".from_label").css("display", "block");
                $(".to_label").css("display", "block");
                $(".date_to").css("display", "block");
            } else {
                $(".leave-checkbox").css("display", "block");
                $(".date_to").css("display", "block");
            }
        });
        $("#request_unit_half").change(function() {
            if ($(this).is(':checked')) {
                $("#request_unit_hours").prop('checked', false);
                $(".from_label").css("display", "none");
                $(".to_label").css("display", "none");
                $(".date_to").css("display", "none");
                $("#request_date_from_period").css("display", "block");
            } else {
                $(".from_label").css("display", "block");
                $(".to_label").css("display", "block");
                $(".date_to").css("display", "block");
                $("#request_date_from_period").css("display", "none");
                $("#request_date_from_period").val("");
            }
        });
        $("#request_unit_hours").change(function() {
            if ($(this).is(':checked')) {
                $('#request_unit_half').prop('checked', false);
                $(".custom_hours").css("display", "block");
            } else {
                $(".custom_hours").css("display", "none");
                $(".custom_hours").val("");
            }
        });
    });

});