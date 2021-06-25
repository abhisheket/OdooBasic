# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.osv import expression


class PriceRange(WebsiteSale):

    def new_search_domain(self, search, category, attrib_values, post,
                          search_in_description=True):
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                if search_in_description:
                    subdomains.append([('description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))
        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])
        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append(
                        [('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])
        if request.session['price_min']:
            domains.append(
                [('list_price', '>=', float(request.session['price_min']))])
        if request.session['price_max']:
            domains.append(
                [('list_price', '<=', float(request.session['price_max']))])
        return expression.AND(domains)

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
        add_qty = int(post.get('add_qty', 1))
        product_category = request.env['product.public.category']
        if category:
            category = product_category.search([('id', '=', int(category))],
                                               limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = product_category
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20
        ppr = request.env['website'].get_current_website().shop_ppr or 4
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in
                         attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}
        if not post.get('order') and not post.get(
                'price_min') and not post.get('price_max'):
            request.session['price_min'] = ''
            request.session['price_max'] = ''
            request.session['order'] = ''
        elif post.get('order') and not post.get(
                'price_min') and not post.get('price_max'):
            request.session['order'] = post.get('order')
        else:
            if post.get('price_min'):
                request.session['price_min'] = post.get('price_min')
                request.session['price_max'] = post.get('price_max')
            if post.get('price_max'):
                request.session['price_min'] = post.get('price_min')
                request.session['price_max'] = post.get('price_max')
        domain = self.new_search_domain(search, category, attrib_values, post)
        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list,
                        order=post.get('order'))
        pricelist_context, pricelist = self._get_pricelist_context()
        request.context = dict(request.context, pricelist=pricelist.id,
                               partner=request.env.user.partner_id)
        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list
        products = request.env['product.template'].with_context(bin_size=True)
        search_product = products.search(
            domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = product_category.search(
                [('product_tmpl_ids', 'in',
                  search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = product_category
        categs = product_category.search(categs_domain)
        if category:
            url = "/shop/category/%s" % slug(category)
        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page,
                                      step=ppg, scope=7,url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]
        product_attribute = request.env['product.attribute']
        if products:
            attributes = product_attribute.search(
                [('product_tmpl_ids', 'in',  search_product.ids)])
        else:
            attributes = product_attribute.browse(attributes_ids)
        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref(
                    'website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'price_min':  request.session.get('price_min') or '',
            'price_max':  request.session.get('price_max') or '',
            'order':  request.session.get('order') or '',
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)
