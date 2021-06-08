odoo.define('pos_product_brand.order_line', function (require) {
    'use strict';

    var models = require('point_of_sale.models');

    models.load_fields('product.product', 'brand');

});
