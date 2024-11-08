from odoo import api, fields, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'


    pos_active = fields.Boolean(
        string='Conectado a POS',
    )
    
    equipment_id = fields.Many2one(
        string='Equipo POS',
        comodel_name='pos.equipment',
        ondelete='restrict',
    )

    def get_equipment_info(self):
        for rec in self:
            auth_token = self.env['ir.config_parameter'].sudo().get_param('auth_token_pos_config')
            return {
                'id': rec.equipment_id.id if rec.equipment_id else False,
                'model': rec.equipment_id.name if rec.equipment_id else False,
                'serial': rec.equipment_id.serial_id.serial_char_id if rec.equipment_id and rec.equipment_id.serial_id else '',
                'token': auth_token if auth_token else False,
                'validation_delay': rec.equipment_id.pos_api_config_id.payment_delay_validation if rec.equipment_id else False
            }


    @api.model
    def execute_request_receipt_create_model(self, order_reference):
        pos_order_id = self.env['pos.order'].search([('pos_reference', '=', order_reference[0] if isinstance(order_reference, list) else order_reference)])
        if pos_order_id:
            response = pos_order_id.account_move.do_execute_receipt_invoice()
            _logger.info('execute_request_receipt_create_model-response')
            _logger.info(response)
            if 'error' not in response and response['result']['status'] == 'success':
                num_folio =  response['result']['data'][0]['folio']
                num_uuid =  response['result']['data'][0]['uuid']
                qr_code =  response['result']['data'][0]['ted']
                pos_order_id.account_move.set_data_payment_request(num_folio, num_uuid)
                return {
                    "num_folio": num_folio,
                    "qr": qr_code,
                    "status": "success"
                }
            else:
                return response
        else:
            return {
                    "response": "No se encontro Pos Order",
                    "status": "error"
            }
    

    def execute_request_receipt_create(self, order_reference):
        for rec in self:
            pos_order_id = self.env['pos.order'].search([('pos_reference', '=', order_reference[0] if isinstance(order_reference, list) else order_reference)])
            if pos_order_id:
                response = pos_order_id.account_move.do_execute_receipt_invoice()
                if 'error' not in response and response['result']['status'] == 'success':
                    num_folio =  response['result']['data'][0]['folio']
                    num_uuid =  response['result']['data'][0]['uuid']
                    qr_code =  response['result']['data'][0]['ted']
                    pos_order_id.account_move.set_data_payment_request(num_folio, num_uuid)
                    return {
                        "num_folio": num_folio,
                        "qr": qr_code,
                        "status": "success"
                    }
                else:
                    return response
            else:
                return {
                    "response": "No se encontro Pos Order",
                    "status": "error"
                }
    
class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_pos_payment_method(self):
        res = super(PosSession, self)._loader_params_pos_payment_method()
        res['search_params']['fields'].append('pos_active')
        res['search_params']['fields'].append('equipment_id')
        return res

class PaxPayment(models.Model):
    _name = 'pax.payment'
    _description = 'Modelo de pagos Pax'


    pax_function  = fields.Integer(string='Tipo de función POS')
    pax_payment_response = fields.Integer(string='Respuesta')
    pax_payment_description = fields.Char(string='Mensaje',  help='Mensaje de texto que representa la respuesta de la operación puede ser Aprobado o Rechazado.')
    pax_auth_code = fields.Char(string='Autorización', help='Código de autorización de la transacción.')
    pax_operation_id = fields.Integer(string='Id Operación')
    pax_commerce_code = fields.Char(string='Código de comercio')
    pax_terminal_id = fields.Char(string='Id Terminal')
    pax_ticket = fields.Char(string='Ticket de oeración')

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    pax_function  = fields.Integer(string='Tipo de función POS', compute="_compute_value")
    pax_payment_response = fields.Integer(string='Respuesta', compute="_compute_value")
    pax_payment_description = fields.Char(string='Mensaje',  help='Mensaje de texto que representa la respuesta de la operación puede ser Aprobado o Rechazado.', compute="_compute_value")
    pax_auth_code = fields.Char(string='Autorización', help='Código de autorización de la transacción.', compute="_compute_value")
    pax_operation_id = fields.Integer(string='Id Operación', compute="_compute_value")
    pax_commerce_code = fields.Char(string='Código de comercio', compute="_compute_value")
    pax_terminal_id = fields.Char(string='Id Terminal', compute="_compute_value")
    pax_ticket = fields.Char(string='Ticket de oeración', compute="_compute_value")

    @api.depends("ticket")
    def _compute_value(self):
        for rec in self:
            # Falta definir segun los recs pax creados por la peticion desde el POS
            rec.pax_function = 0
            rec.pax_payment_response = 0
            rec.pax_payment_description = ""
            rec.pax_auth_code = ""
            rec.pax_operation_id = 0
            rec.pax_commerce_code = ""
            rec.pax_terminal_id = ""
            rec.pax_ticket = ""
