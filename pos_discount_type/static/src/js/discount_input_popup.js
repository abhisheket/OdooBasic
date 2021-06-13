odoo.define('pos_discount_type.discount_input_popup', function (require) {
    "use strict";

    const { useState, useRef, useExternalListener } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const { Gui } = require('point_of_sale.Gui');
    const Registries = require('point_of_sale.Registries');


    class DiscountInputPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
            useExternalListener(window, 'keydown', this._checkInput);
        }
        mounted() {
            this.inputRef.el.focus();
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
            var discount_percentage, discount_amount, total_without_tax;
            var discount_type = this.env.pos.config.discount_type;
            var line = this.env.pos.get_order().get_selected_orderline();
            line.discount_type = discount_type;
            var product_price = line.product.lst_price;
            var product_quantity = line.quantity;
            var order_total = 0;
            if (discount_type =='percentage') {
                if (this.state.inputValue > 100) {
                    discount_percentage = 100;
                } else {
                    discount_percentage = this.state.inputValue;
                }
                line.discount_percentage = parseFloat(discount_percentage).toFixed(2);
                line.discount_amount = (product_quantity * product_price * discount_percentage / 100).toFixed(2);
                line.price = (product_price * (100 - discount_percentage) / 100).toFixed(2);

            }
            if (discount_type =='amount') {
                if (this.state.inputValue > (product_quantity * product_price)) {
                    discount_amount = product_quantity * product_price;
                } else {
                    discount_amount = this.state.inputValue;
                }
                line.discount_amount = parseFloat(discount_amount).toFixed(2);
                line.price = ((product_price * 100 - (discount_amount / product_quantity) * 100) / 100).toFixed(2);
                line.discount_total = ((product_quantity * product_price * 100 - discount_amount * 100) / 100).toFixed(2);
            }
            line.update_orderline();
        }
    }
    DiscountInputPopup.template = 'DiscountInputPopup';
    DiscountInputPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Discount',
        body: 'Enter discount',
        startingValue: '',
    };

    Registries.Component.add(DiscountInputPopup);

    return DiscountInputPopup;
});