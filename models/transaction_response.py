from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import uuid
import logging
import json

_logger = logging.getLogger(__name__)

from odoo.api import depends
from odoo.exceptions import UserError


class TransactionResponse(models.Model):
    _name = 'transaction.response'

    name = fields.Char(readonly=True)
    code = fields.Char()
    message = fields.Char()
    provider = fields.Char()
    data = fields.Json()
    sale_id = fields.Many2one(
        string='Venta vinculada',
        comodel_name='sale.order'
    )

    response_uuid = fields.Char(string="UUID", copy=False, default=None, required=True)
    json_txt = fields.Text(string="JSON Text", readonly=True, compute='_compute_json_txt')

    def _compute_json_txt(self):
        for record in self:
            if record.data:
                try:
                    record.json_txt = json.dumps(record.data, indent=4, sort_keys=True)
                except (TypeError, ValueError) as e:
                    record.json_txt = f"Error al convertir a JSON: {e}"
            else:
                record.json_txt = "{}"

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
        res.name = res.response_uuid
        res.code = 0
        res._action_send_transaction_notification()
        return res
