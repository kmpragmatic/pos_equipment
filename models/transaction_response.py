from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import uuid

class TransactionResponse(models.Model):
    _name = 'transaction.response'

    name = fields.Char(default=f'Transaccion - {datetime.now().strftime("%d-%m-%Y")}')
    code = fields.Char()
    message = fields.Char()
    provider = fields.Char()
    data = fields.Json()
    sale_id = fields.Many2one(
        string='Venta vinculada',
        comodel_name='sale.order'
    )

    response_uuid = fields.Char(string="UUID", readonly=True, copy=False, default=None)

    @api.model
    def create(self, vals):
        vals['response_uuid'] = str(uuid.uuid4())
        return super(TransactionResponse, self).create(vals)

