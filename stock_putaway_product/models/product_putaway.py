# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ProductPutawayStrategy(models.Model):
    _inherit = 'product.putaway'

    @api.model
    def _get_putaway_options(self):
        ret = super(ProductPutawayStrategy, self)._get_putaway_options()
        return ret + [('per_product', 'Fixed per product location')]

    product_location_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='putaway_id',
        string='Fixed per product location',
        copy=True)
    method = fields.Selection(selection=_get_putaway_options)

    # @api.multi
    # def get_product_putaway_strategies(self, product):
    #     self.ensure_one()
    #     return self.product_location_ids.filtered(lambda x: (
    #         x.product_product_id == product or
    #         (not x.product_product_id and
    #          x.product_tmpl_id == product.product_tmpl_id)))

    def _putaway_apply_per_product(self, product):
        for strat in self.product_location_ids:
            product_id = product.id
            if strat.product_product_id.id == product_id:
                return strat.fixed_location_id.id

        return self.env['stock.location']


class StockFixedPutawayStrategy(models.Model):
    _name = 'stock.product.putaway.strategy'
    _rec_name = 'product_product_id'
    _order = 'putaway_id, sequence'

    _sql_constraints = [(
        'putaway_product_location_unique',
        'unique(putaway_id,product_product_id,fixed_location_id)',
        _('There is a duplicate location by put away assignment!')
    )]

    @api.model
    def get_default_inventory_id(self):
        return self.env['stock.inventory'].search(
            [('id', '=', self.env.context.get('active_id', False))])

    putaway_id = fields.Many2one(
        comodel_name='product.putaway',
        string='Put Away Strategy',
        required=True,
        index=True)
    # product_tmpl_id = fields.Many2one(
    #     comodel_name='product.template',
    #     string='Product Template',
    #     index=True,
    #     oldname='product_template_id',
    #     required=True)
    product_product_id = fields.Many2one(
        comodel_name='product.product',
        string='产品',
        index=True)
    fixed_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        required=True,
        domain=[('usage', '=', 'internal')])
    sequence = fields.Integer()
