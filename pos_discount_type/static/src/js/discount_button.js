odoo.define('pos_discount_type.discount_button', function (require) {
    "use strict";

    const { Gui } = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');

    class DiscountButton extends PosComponent {
        constructor() {
           super(...arguments);
           useListener('click', this.onClick);
       }
        onClick() {
            Gui.showPopup("DiscountInputPopup", {
                title: this.env._t('Discount'),
                body: this.env._t('Enter discount in ' + this.env.pos.config.discount_type),
            });
        }
   }
   DiscountButton.template = 'DiscountButton';
   ProductScreen.addControlButton({
       component: DiscountButton,
       condition: function() {
           return this.env.pos.config.manual_discount;
       },
   });
   Registries.Component.add(DiscountButton);
   return DiscountButton;

});