# coding:utf-8
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class id_dict(models.Model):
    _name = 'id.dict'
    _description = u'id映射'

    old_model = fields.Char()
    old_id = fields.Integer()

    now_model = fields.Char()
    now_id = fields.Integer()

    @api.multi
    def get_now_id(self, old_model, old_id):
        if not old_model or not old_id:
            return False

        self._cr.execute(
            "select now_model,now_id from id_dict where old_model = '%s' and old_id = %s" % (old_model, old_id))
        datas = self._cr.fetchall()
        for data in datas:
            return data[1]

        return False
