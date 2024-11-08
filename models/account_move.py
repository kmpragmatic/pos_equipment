from odoo import models, api, fields
from odoo.http import request
import requests

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    folio_number = fields.Char('No. Folio')
    sequence_payment = fields.Char('No. Secuencia')

    def set_data_payment_request(self, folio, sequence_payment):
        for rec in self:
            rec.folio_number = folio
            rec.sequence_payment = sequence_payment

    def validate_setting_params(self):
        token = request.env['ir.config_parameter'].sudo().get_param('billon_token')
        if not token:
            raise UserError('Token no encontrado en parametros de sistema, debes generar uno desde POS equipment')

        service_url = request.env['ir.config_parameter'].sudo().get_param('billon_service_url')

        if not service_url:
            raise UserError('URL del servicio no configurada en los ajustes')

    def do_execute_receipt_invoice_from_view(self):
        for rec in self:
            rec.validate_setting_params()
            response = rec.do_execute_receipt_invoice()
            if 'error' not in response and response['result']['status'] == 'success':
                num_folio =  response['result']['data'][0]['folio']
                num_uuid =  response['result']['data'][0]['uuid']
                rec.set_data_payment_request(num_folio, num_uuid)
            else:
                raise UserError(f'{response}')

    def do_execute_receipt_invoice(self):
        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/odoo_invoice'
        payload = {
            'account_move_id': self.id
        }
        headers = {
            'Content-Type': 'application/json',
        }
        cookies = request.httprequest.cookies
        _logger.info("do_execute_receipt_invoice")
        _logger.info(url)
        _logger.info(payload)
        _logger.info(headers)
        _logger.info(cookies)
        response = requests.post(url, json=payload, headers=headers, cookies=cookies)
        if response.status_code == 200:
            response_data = response.json()
            return response_data
        else:
            return {
                "error": "Error en la solicitud",
                "status_code": response.status_code,
                "response": response.text
            }