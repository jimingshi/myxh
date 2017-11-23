# coding:utf-8
import psycopg2
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class res_company(models.Model):
    _inherit = 'res.company'

    def upgrade(self):
        conn = psycopg2.connect('dbname=sw user=postgres password=admin')

        conn.close()

