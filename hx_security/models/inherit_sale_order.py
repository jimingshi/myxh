# -*- coding: utf-8 -*-
"""
    
Description:
Author:Gala
Versions:
    Created by Gala on 2017/11/23 10:55
"""
import json
from odoo import models, api, fields, _
from odoo.tools import float_is_zero, float_compare

class InheritSaleOrder(models.Model):

    _inherit = ["sale.order"]

