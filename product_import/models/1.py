# -*- coding: utf-8 -*-
import base64
import xlrd
import string
import types


from openerp import models, fields, api, _
from openerp.exceptions import UserError


class product_import(models.Model):
    _name = 'product.import'
    _description = u'产品导入'

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

        self._cr.execute("select name,id from res_partner where supplier = 't'")
        gys_dict = dict(self._cr.fetchall())

        for sheet in wb.sheets():
            self._handle_mx(sheet, gys_dict)


    @api.multi
    def _handle_mx(self, sheet, gys_dict):
        pt = self.env['product.product']

        # 直接从第2行开始读取数据
        for i in range(1, sheet.nrows):

            code1 = sheet.cell(i, 3).value
            if code1!='':
                code=str(int(code1))
            else:
                code=code1
            product_product_name = sheet.cell(i, 1).value
            attribute=sheet.cell(i, 2).value
            vals = {
                'name': product_product_name,
                'default_code': code,
            }

            print self.env['product.product'].search([('name', '=', product_product_name )]).id

            # if product_product_name in product_template_dict:
            pt.search(['&',('name', '=', product_product_name),('attribute_value_ids', '=', attribute)]).write({'default_code': code})


