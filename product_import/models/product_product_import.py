# -*- coding: utf-8 -*-
import base64
import xlrd


from openerp import models, fields, api, _
from openerp.exceptions import UserError


class product_import(models.Model):
    _name = 'product.product.import'
    _description = u'产品变型导入'

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
            self._import_product_product(sheet)


    @api.multi
    def _import_product_product(self, sheet):
        pt = self.env['product.product']

        # 直接从第2行开始读取数据
        for i in range(1, sheet.nrows):

            code1 = sheet.cell(i, 2).value
            if code1!='':
                code=str(int(code1))
            else:
                code=code1
            product_template_name = sheet.cell(i, 1).value
            vals = {
                'name': product_template_name,
                'default_code': code,
            }
            attribute = sheet.cell(i, 4).value

            print product_template_name
            self._cr.execute("select name,id from product_template where name='"+product_template_name+"';")
            template_dict = dict(self._cr.fetchall())
            if product_template_name in template_dict:
                template_id=template_dict[product_template_name]


                # self._cr.execute("select attribute_value_ids,id from product_attribute_value where product_tmpl_id='"+template_id+"';")
                # product_dict = dict(self._cr.fetchall())
                # print product_dict[0]
                #
                print template_id
                # if template_id !="":
                self._cr.execute("select id from product_product where product_tmpl_id="+template_id+";")
                #     self._cr.execute("select name,id from product_template ;")

                    # product_list =[a for (a,) in self._cr.fetchall()]
                    # product_list = []
                    # for a in dict(self._cr.fetchall()):
                    #     product_list.append(a)
                    #
                    # print product_list






















