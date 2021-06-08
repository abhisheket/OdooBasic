odoo.define('pos_product_brand_13.order_line', function (require) {
    'use strict';

    var models = require('point_of_sale.models');

    models.load_fields('product.product', 'brand');

});
