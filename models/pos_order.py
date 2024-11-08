# -*- coding: utf-8 -*-

import uuid
from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    custom_order_uuid = fields.Char(string="UUID", readonly=True, copy=False, default=None)

    # @api.model
    # def create(self, vals):
    #     # Genera un UUID y lo asigna al campo 'order_uuid'
    #     vals['order_uuid'] = str(uuid.uuid4())
    #     return super(PosOrder, self).create(vals)
