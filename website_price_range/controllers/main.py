# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.models.ir_http import sitemap_qs2dom

from odoo.addons.website_sale.controllers.main import WebsiteSale


class PriceRange(WebsiteSale):

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        domains = request.website.sale_product_domain()
        print(domains)
        print(post)
        if post.get('price_min'):
            domains.append(('price', '>=', int(post['price_min'])))
            print('price_min')
        if post.get('price_max'):
            domains.append(('price', '<=', int(post['price_max'])))
            print('price_max')
        print(domains)
        # Product = request.env['product.template'].with_context(bin_size=True)
        res = super(PriceRange, self).shop(page=page, category=category,
                                           search=search, ppg=ppg, **post)
        return res
