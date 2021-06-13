odoo.define('pos_discount_type_13.receipt_line', function (require) {
    'use strict';

    var models = require('point_of_sale.models');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

        export_for_printing: function() {
            var line = _super_orderline.export_for_printing.apply(this,arguments);
            if(this.discount_type) {
                line.discount_type = this.discount_type;
                line.discount_amount = this.discount_amount;
                if(this.discount_type == "percentage") {
                    line.discount_percentage = this.discount_percentage;
                }
            }
            return line;
        },
    });

});
