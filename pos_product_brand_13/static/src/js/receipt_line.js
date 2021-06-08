odoo.define('pos_product_brand_13.receipt_line', function (require) {
    'use strict';

    var models = require('point_of_sale.models');

    models.load_fields('product.product', 'brand');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function() {
            var line = _super_orderline.export_for_printing.apply(this,arguments);
            line.brand = this.get_product().brand;
            return line;
        },
    });

});
