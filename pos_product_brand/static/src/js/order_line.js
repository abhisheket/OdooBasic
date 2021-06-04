odoo.define('pos_product_brand.order_line', function (require) {
    'use strict';

    var models = require('point_of_sale.models');

    models.load_fields('product.product', 'brand');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        get_orderlines: function() {
            var line = _super_orderline.get_orderlines.apply(this,arguments);
            line.brand = this.get_product().brand;
            return line;
        },
    });
});
