from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import uuid
import logging

_logger = logging.getLogger(__name__)

from odoo.api import depends
from odoo.exceptions import UserError


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

    response_uuid = fields.Char(string="UUID", readonly=True, copy=False, default=None, required=True)

    @api.model
    def get_payment_uuid_info(self, uuid):
        payment_uuid = self.search([('response_uuid', '=', uuid)], limit=1)
        return {
            'code': payment_uuid.code,
            'uuid': payment_uuid.response_uuid,
            'response': payment_uuid.message
        }

    def _action_send_transaction_notification(self):
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'transaction_response',
            {
                'code': self.code,
                'uuid': self.response_uuid,
                'response': self.message
            },
        )

    def create(self, vals):
        if self.env['transaction.response'].search([('response_uuid', '=', vals.get('response_uuid'))]):
            raise UserError('El valor UUID ya existe o no puede ser vacio')
        res = super(TransactionResponse, self).create(vals)
        res._action_send_transaction_notification()
        return res
