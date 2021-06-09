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
            if (event.key === '.' && this.state.inputValue.includes('.')) {
                event.preventDefault();
            }
            if (! event.key.match(/[\d.]/) && event.keyCode != 8) {
                event.preventDefault();
                console.log(this);
                console.log(this.env.pos.get_order());
            }
        }
        getPayload() {
            if (this.state.inputValue > 100 && this.env.pos.config.discount_type =='percentage') {
                this.state.inputValue = 100;
            }
//            return this.state.inputValue;
            alert(this.state.inputValue);
        }

    }
    DiscountInputPopup.template = 'TextInputPopup';

    Registries.Component.add(DiscountInputPopup);

    return DiscountInputPopup;
});