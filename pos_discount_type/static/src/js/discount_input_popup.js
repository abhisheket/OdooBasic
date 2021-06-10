odoo.define('pos_discount_type.discount_input_popup', function (require) {
    "use strict";

    const { useState, useRef, useExternalListener } = owl.hooks;
    const TextInputPopup = require('point_of_sale.TextInputPopup');
    const Registries = require('point_of_sale.Registries');

    class DiscountInputPopup extends TextInputPopup {
        constructor() {
            super(...arguments);
            useExternalListener(window, 'keydown', this._checkInput);
        }
        _checkInput(event) {
            if (! this.state.inputValue && event.key === '.') {
                event.preventDefault();
                this.state.inputValue = '0.';
            }
            if ((! event.key.match(/[\d.]/) && event.keyCode != 8) || (event.key === '.' && this.state.inputValue.includes('.')) || (event.key.match(/\d/) && this.state.inputValue.match(/\.\d{2}$/))) {
                event.preventDefault();
            }
        }
        getPayload() {
            var product_price, product_quantity, discount_percentage, discount_amount, total_without_tax;
            var discount_type = this.env.pos.config.discount_type;
            this.env.pos.get_order().get_orderlines().forEach(function (line) {
                if (line.selected) {
                    product_price = line.price;
                    product_quantity = line.quantity;
                }
            });
            if (discount_type =='percentage') {
                if (this.state.inputValue > 100) {
                    discount_percentage = 100;
                } else {
                    discount_percentage = this.state.inputValue;
                }
                total_without_tax = (product_quantity * product_price * (100 - discount_percentage) / 100).toFixed(2)
            }
            if (discount_type =='amount') {
                if (this.state.inputValue > (product_quantity * product_price)) {
                    discount_amount = product_quantity * product_price;
                } else {
                    discount_amount = this.state.inputValue;
                }
                total_without_tax = (product_quantity * product_price * 100 - discount_amount * 100) / 100
            }
            this.env.pos.get_order().get_orderlines().forEach(function (line) {
                if (line.selected) {
                    line.discount_type = discount_type;
                    line.discount_amount = parseFloat(discount_amount).toFixed(2);
                    line.discount_percentage = parseFloat(discount_percentage).toFixed(2);
                    line.total_without_tax = total_without_tax;
                    return line;
                }
            });
        }

    }
    DiscountInputPopup.template = 'TextInputPopup';

    Registries.Component.add(DiscountInputPopup);

    return DiscountInputPopup;
});