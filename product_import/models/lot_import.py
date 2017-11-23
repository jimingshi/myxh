# -*- coding: utf-8 -*-
import base64
import xlrd
from openerp import models, fields, api, _
from openerp.exceptions import UserError


class product_import(models.Model):
    _name = 'lot.import'
    _description = u'产品序号导入'

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
            self._handle_lot(sheet)

    @api.multi
    def _handle_lot(self, sheet, gys_dict):

        # 直接从第2行开始读取数据
        for i in range(1, sheet.nrows):

            code1 = sheet.cell(i, 2).value
            if code1!='':
                code=str(int(code1))
            else:
                code=code1
            product_template_id = sheet.cell(i, 0).value
            product_template_name = sheet.cell(i, 1).value
            vals = {
                'name': product_template_name,
                'default_code': code,
            }






