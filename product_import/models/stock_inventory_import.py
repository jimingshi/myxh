# -*- coding: utf-8 -*-
import base64
import xlrd
import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class stock_inventory_import(models.Model):
    _name = 'stock.inventory.import'
    _description = u'库存盘点导入'

    excel = fields.Binary(u'文件', attachment=True, required=True)

    @api.multi
    def btn_import(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')

        try:
            wb = xlrd.open_workbook(file_contents=base64.decodestring(self.excel))
        except:
            raise UserError(_('文件格式不匹配或文件内容错误.'))

        for sheet in wb.sheets():
            self._handle_inventory(sheet)


    @api.multi
    def _handle_inventory(self, sheet):

        name=sheet.cell(1, 1).value
        date=sheet.cell(1, 2).value
        location_id=self.env['stock.location'].search([('name', '=', sheet.cell(1, 4).value)]).id
        self._cr.execute("select name from product_template;")
        pt_list = [a for (a,) in self._cr.fetchall()]
        self._cr.execute("select default_code from product_product;")
        code_list = [a for (a,) in self._cr.fetchall()]


        vals = {

            'name': name,
             # 'date': '2017/4/11  1:20:09',
            'location_id': location_id,
            'state':'confirm'

        }
        inventory=self.env['stock.inventory'].create(vals).id
        # print inventory
        # 直接从第2行开始读取数据
        for i in range(1, sheet.nrows):
            code = sheet.cell(i, 6).value
            if code != '':
                code = str(int(code))

            uom_name = sheet.cell(i, 13).value
            location_name = sheet.cell(i, 9).value

            product_template_name = sheet.cell(i, 5).value.strip()
            print product_template_name
            pt_list.append(product_template_name)
            code_list.append(code)

            prodlot_name = sheet.cell(i, 10).value
            self._cr.execute("select name from stock_production_lot ")
            prodlot_list = [a for (a,) in self._cr.fetchall()]


            if prodlot_name!='':
                if prodlot_name in prodlot_list:
                    pass
                else:
                    prodlot_id=self.env['stock.production.lot'].create({
                        'name': prodlot_name,
                        'product_id': self.env['product.product'].search([('default_code', '=', code)]).id,
                        'product_uom_id': self.env['product.uom'].search([('name', '=', uom_name)]).id,
                    }).id
                    prodlot_list.append(prodlot_name)

            product_id=self.env['product.product'].search([('default_code', '=', code)]).id
            print (product_id)
            vals1={
                'line_ids':[(0, False, {'product_id': product_id,

                    'product_name': product_template_name,
                    'product_code': code,
                    'product_uom_id': self.env['product.uom'].search([('name', '=', uom_name)]).id,
                    'product_qty': sheet.cell(i, 11).value,
                    'location_id': self.env['stock.location'].search([('name', '=', location_name)]).id,
                    'location_name': location_name,
                    'prod_lot_id': self.env['stock.production.lot'].search([('name', '=', prodlot_name),('product_id', '=', product_id)]).id,
                    'prodlot_name': prodlot_name,
            })]}

            self.env['stock.inventory'].search([('id', '=', inventory)]).write(vals1)











