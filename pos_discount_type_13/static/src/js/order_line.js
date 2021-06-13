odoo.define('pos_discount_type_13.order_line', function (require) {
    'use strict';

    var field_utils = require('web.field_utils');
    var models = require('point_of_sale.models');

    var _super_orderline = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({
        initialize: function() {
            _super_orderline.initialize.apply(this,arguments);
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.set_discount_type(json.discount_type);
            this.discount_amount = json.discount_amount;
            this.discount_percentage = json.discount_percentage;
            this.set_discount_total(json.discount_total);
        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.call(this);
            if(this.discount_type) {
                json.discount_type = this.discount_type;
                json.discount_amount = this.discount_amount;
                if(this.discount_type == "percentage") {
                    json.discount_percentage = this.discount_percentage;
                }
                if(this.discount_type == "amount"){
                    json.discount_total = this.discount_total;
                }
            }
            return json;
        },
        set_discount_total: function(discount_total){
            this.discount_total = discount_total || false;
        },
        get_discount_total: function(){
            return this.discount_total;
        },
        set_discount_type: function(discount_type){
            this.discount_type = discount_type || false;
        },
        get_discount_type: function(){
            return this.discount_type;
        },
        update_orderline: function(){
            this.trigger('change', this);
        }
    });

});
