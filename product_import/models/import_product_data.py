# -*- encoding: utf-8 -*-
import xlrd
import base64
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class import_product_data(models.TransientModel):
    _name = 'import.product.data'
    _description = u'导入产品'

    files = fields.Binary(u'上传导入文件')

    @api.one
    def _old_import_data(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.files))

        sheet = wb.sheet_by_index(0)
        for i in range(sheet.nrows):
            if i in [0, 1]:
                continue
            row = sheet.row_values(i)
            if not row[0]:
                break

            # 查找或创建品牌及系列
            if row[1]:
                brand_id = self.env['product.brand'].search([('name', '=', row[1])]).id
                if not brand_id:
                    brand_id = self.env['product.brand'].create({'name': row[1]}).id
            else:
                brand_id = False

            if row[2]:
                series_id = self.env['product.series'].search([('name', '=', row[2])]).id
                if not series_id:
                    series_id = self.env['product.series'].create({'name': row[2], 'brand_id': brand_id}).id
            else:
                series_id = False

            # !!!!手动创建单位!!!! 检查
            uom_id = self.env['product.uom'].search([('name', '=', row[4])]).id or False

            pt = self.env['product.template'].create({
                'name': row[6],
                'default_code': row[0],
                'brand_id': brand_id,
                'series_id': series_id,
                'type': 'product',
                'uom_id': uom_id,
                'uom_po_id': uom_id,
                'cost_method': 'real',
            })
            # if len(pt.product_variant_ids) == 1:
            #     pt.product_variant_ids[0].default_code = row[0]
            # else:
            #     raise Warning('Warning!!')

    @api.one
    def import_data(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.files))

        sheet = wb.sheet_by_index(0)
        # 商品编码，类别，品牌，系列，基本单位，商品名称，规格名1，规格值1，规格名2，规格值2，规格名3，规格值3，规格名4，。。。

        leibie_obj = self.env['product.project']
        pinpai_obj = self.env['product.brand']
        series_obj = self.env['product.series']
        uom_obj = self.env['product.uom']
        for i in range(sheet.nrows):
            if i in [0]:
                continue
            row = sheet.row_values(i)
            if not row[0]:
                break

            # 处理类别
            if row[1]:
                leibie_id = leibie_obj.search([('name', '=', row[1])]).id
                if not leibie_id:
                    leibie_id = leibie_obj.create({'name': row[1]}).id
            else:
                _logger.warning("%s has no leibie", i)
                leibie_id = False

            # 处理品牌
            if row[2]:
                brand_id = pinpai_obj.search([('name', '=', row[2]), ('leibie_id', '=', leibie_id)]).id
                if not brand_id:
                    brand_id = pinpai_obj.create({'name': row[2], 'leibie_id': leibie_id}).id
            else:
                _logger.warning("%s has no brand_id", i)
                brand_id = False

            # 处理系列
            if row[3]:
                series_id = series_obj.search([('name', '=', row[3])]).id
                if not series_id:
                    series_id = series_obj.create({'name': row[3], 'brand_id': brand_id}).id
            else:
                _logger.warning("%s has no series_id", i)
                series_id = False

            # 处理单位 手动创建
            uom_id = uom_obj.search([('name', '=', row[4])]).id or False

            # 获取或创建产品模板
            pt = self.env['product.template'].search([('name', '=', row[5])])
            if not pt:
                pt = self.env['product.template'].create({
                    'type': 'product',
                    'name': row[5],
                    'leibie_id':leibie_id,
                    'brand_id': brand_id,
                    'series_id': series_id,
                    'uom_id': uom_id,
                    'uom_po_id': uom_id,
                    'default_code': row[0]
                })
            #########################################################################################

            # 获取excel中属性值列表
            atts = {}
            for atti in range(sheet.ncols):
                if atti > 5 and atti % 2 == 0 and atti != sheet.ncols - 1:
                    if row[atti] and row[atti + 1]:
                        if row[atti] not in atts:
                            atts[row[atti]] = []

                        atts[row[atti]] += str(row[atti + 1]).split(',')

            # 获取/创建属性名
            atts_dict = {}
            for att in atts:
                att_id = self.env['product.attribute'].search([('name', '=', att)]).id
                if isinstance(att_id, list):
                    att_id = att_id[0]
                if not att_id:
                    att_id = self.env['product.attribute'].create({'name': att}).id

                atts_dict[att_id] = []
                # 获取/创建属性值
                for attv in atts[att]:
                    att_value = self.env['product.attribute.value'].search(
                            [('name', '=', attv), ('attribute_id', '=', att_id)]).id
                    if not att_value:
                        att_value = self.env['product.attribute.value'].create(
                                {'name': attv, 'attribute_id': att_id}).id
                    atts_dict[att_id].append(att_value)

            # 为产品模板添加规格（创建产品）
            if not atts_dict:
                # 属性为空
                pass
            else:
                vals = []
                for al in pt.attribute_line_ids:  # 处理已有属性
                    if al.attribute_id.id in atts_dict:
                        ids = list(set(al.value_ids.ids + atts_dict[al.attribute_id.id]))
                        vals.append([1, al.id, {'value_ids': [[6, False, ids]]}])
                        atts_dict.pop(al.attribute_id.id)  # 删除已处理数据

                for att_dict in atts_dict:  # 处理新建属性
                    vals.append([0, False, {'attribute_id': att_dict, 'value_ids': [[6, False, atts_dict[att_dict]]]}])

                pt.write({'attribute_line_ids': vals})
