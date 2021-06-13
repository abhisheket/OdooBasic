odoo.define('pos_discount_type_13.discount_input_popup', function (require) {
    "use strict";

    var popups = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');

    var DiscountInputPopupWidget = popups.extend({
        template: 'DiscountInputPopupWidget',
        events: _.extend({}, popups.prototype.events, {
            'keydown input':  '_checkInput',
        }),
        show: function(options){
            options = options || {};
            this._super(options);

            this.renderElement();
            this.$('input,textarea').focus();
        },
        _checkInput: function (event) {
            if (! this.$('input,textarea').val() && event.key === '.') {
                event.preventDefault();
                this.$('input,textarea').val() = '0.';
            }
            if ((! event.key.match(/[\d.]/) && event.keyCode != 8) || (event.key === '.' && this.$('input,textarea').val().includes('.')) || (event.key.match(/\d/) && this.$('input,textarea').val().match(/\.\d{2}$/))) {
                event.preventDefault();
            }
        },
        click_confirm: function(){
            var value = this.$('input,textarea').val();
            this.gui.close_popup();
            var discount_percentage, discount_amount, total_without_tax;
            var discount_type = this.pos.config.discount_type;
            var line = this.pos.get_order().get_selected_orderline();
            line.discount_type = discount_type;
            var product_price = line.product.lst_price;
            var product_quantity = line.quantity;
            var order_total = 0;
            if (discount_type =='percentage') {
                if (value > 100) {
                    discount_percentage = 100;
                } else {
                    discount_percentage = value;
                }
                line.discount_percentage = parseFloat(discount_percentage).toFixed(2);
                line.discount_amount = (product_quantity * product_price * discount_percentage / 100).toFixed(2);
                line.price = (product_price * (100 - discount_percentage) / 100).toFixed(2);
            }
            if (discount_type =='amount') {
                if (value > (product_quantity * product_price)) {
                    discount_amount = product_quantity * product_price;
                } else {
                    discount_amount = value;
                }
                line.discount_amount = parseFloat(discount_amount).toFixed(2);
                line.price = ((product_price * 100 - (discount_amount / product_quantity) * 100) / 100).toFixed(2);
                line.discount_total = ((product_quantity * product_price * 100 - discount_amount * 100) / 100).toFixed(2);
            }
            line.update_orderline();
        },
    });
    gui.define_popup({name:'discount-input', widget: DiscountInputPopupWidget});

});