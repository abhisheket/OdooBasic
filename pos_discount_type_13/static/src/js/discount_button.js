odoo.define('pos_discount_type_13.discount_button', function (require) {
    "use strict";

    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var _t = core._t;

    var DiscountButton = screens.ActionButtonWidget.extend({
        template: 'DiscountButton',
        button_click: function(){
            if (this.pos.get_order().get_selected_orderline()){
                this.pos.gui.show_popup("discount-input", {
                    'title': _t('Discount'),
                    'body': _t('Enter discount in ' + this.pos.config.discount_type),
                });
            }
        }
    });
    screens.define_action_button({
        'name': 'Discount',
        'widget': DiscountButton,
        'condition': function(){
            return this.pos;
        },
    });

});