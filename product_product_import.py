# -*- coding: utf-8 -*-
import base64
import xlrd
import re

from odoo import models,fields,api,_
from odoo.exceptions import UserError

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

    def _handle_attribute(self):
        '''
        获取当前数据库中 product.attribute 里属性名及属性值关系
        :return:{
            属性名：{
                id:属性名id,
                vals:{
                    属性值名称1：属性值id1,
                    属性值名称2：属性值id2,
                }
            }
        }
        '''
        res = {}

        self._cr.execute("select name,id from product_attribute;")
        att_dict={}
        for name,id in self._cr.fetchall():
            res[name]={'id':id,'vals':{}}
            att_dict[id]=name

        self._cr.execute("select attribute_id,name,id from product_attribute_value;")
        for att_id,name,id in self._cr.fetchall():
            res[att_dict[att_id]]['vals'][name] = id

        return res





    @api.multi
    def _handle_mx(self,sheet,gys_dict):
        att_dict = self._handle_attribute()
        self._cr.execute("select name from product_template;")
        pt_list=[a for (a,) in self._cr.fetchall()]

        # 直接从第2行开始读取数据
        for i in range(1, sheet.nrows):
            code = sheet.cell(i, 2).value
            if code != '':
                code = str(int(code))

            product_template_name = sheet.cell(i, 1).value.strip()
            if product_template_name in pt_list:
                continue
            pt_list.append(product_template_name)

            vals = {
                'name': product_template_name,
                'default_code': code,
            }
            # 如果联系人中没有此供应商，进行添加
            gys_name = sheet.cell(i, 3).value

            # 如果gys_name值为FALSE，设置gys_name为空
            if gys_name:
                if gys_name in gys_dict:
                    gys_id = gys_dict[gys_name]
                else:
                    gys_id = self.env['res.partner'].create({
                        'name': gys_name,
                        'company_type': 'company',
                        'supplier': True,
                        'customer': False,
                    }).id
                    gys_dict[gys_name] = gys_id
                vals['seller_ids'] = [[0, 0, {'name': gys_id, }]]



            #处理变形字段
            att_name = sheet.cell(i, 4).value
            att_value_name = sheet.cell(i, 5).value

            if att_value_name:
                vals['attribute_line_ids']=[]
                #获取属性
                if att_name not in att_dict:
                    att_dict[att_name]={
                        'id':self.env['product.attribute'].create({'name':att_name}).id,
                        'vals':{}
                    }

                #获取属性值ids
                value_ids=[]
                att_values = re.split(u',|，', att_value_name.strip().strip(u',').strip(u'，'))
                for value in att_values:
                    value=value.strip()
                    print value
                    if value not in att_dict[att_name]['vals']:
                        att_dict[att_name]['vals'][value]=self.env['product.attribute.value'].create({
                            'name':value,
                            'attribute_id':att_dict[att_name]['id']
                        }).id
                    value_ids.append(att_dict[att_name]['vals'][value])

                vals['attribute_line_ids'].append((0,0,{
                    'attribute_id':att_dict[att_name]['id'],
                    'value_ids':[(6,0,value_ids)]
                }))

            pt_id = self.env['product.template'].create(vals).id








