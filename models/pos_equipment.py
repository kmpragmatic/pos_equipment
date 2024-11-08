
from odoo import api, fields, models
from odoo.exceptions import UserError
import requests
import json

import logging

_logger = logging.getLogger(__name__)

class PosEquipment(models.Model):
    _name = 'pos.equipment'
    _description = 'POS Equipment'

        
    name = fields.Char(string='Nombre de POS', required=True)
    serial_id = fields.Many2one('pos.seriales', string='Serial de Equipo', required=True)
    # token = fields.Char(string='Token', size=100, required=True)
    token_config_id = fields.Many2one('token.token')
    product_id = fields.Many2one('product.product', string='Modelo de Equipo', required=True)
    response = fields.Char(string='Respuesta')
    pos_api_config_id = fields.Many2one('pos.api.config', string="Request Configuracion")


    def send_notification(self):
        for record in self:
            url = f"https://api.pushy.me/push?api_key={record.token_config_id.auth_token}"
            payload = {
                "to": record.serial_id.serial_char_id,
                "data": {
                    "notiTitle": "Nuevo Pago",
                    "notiMessage": "Tienes un pago pendiente por $4.000",
                    "command": "sale",
                    "paymentApp": "getnet",
                    "data": {
                        "amount": 4000,
                        "ticket": 12,
                        "printVoucher": False,
                        "employeeId": 12,
                        "saleType": 0
                    }
                },
                "notification": {
                    "title": "Pago pendiente",
                    "body": "Tienes un pago por $5.000",
                    "message": "Tienes un pago por $5.000",
                    "badge": 1,
                    "sound": "ping.aiff"
                }
            }
            headers = {
                'Content-Type': 'application/json'
            }
            _logger.warning(payload)
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            _logger.warning(response)
            if response.status_code == 200:
                record.write({'response':response})
            else:
                record.write({'response':response})

    def generate_service_token(self):
        # Obtener la URL del servicio desde los parámetros del sistema
        login_url = '/fapp/v1/auth/login'
        billon_service_url = self.env['ir.config_parameter'].sudo().get_param('billon_service_url')
        username = self.env['ir.config_parameter'].sudo().get_param('billon_username')
        password = self.env['ir.config_parameter'].sudo().get_param('billon_password')

        if not billon_service_url or not username or not password:
            return {'error': 'Parámetros del servicio no configurados'}

        # Construir el payload
        payload = {
            "username": username,
            "password": password
        }

        # Enviar el request
        response = requests.post(billon_service_url + login_url, json=payload)
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                # Guardar el token en otro parámetro del sistema
                self.env['ir.config_parameter'].sudo().set_param('billon_token', token)
                return {'success': 'Token guardado correctamente'}
            else:
                return {'error': 'Token no encontrado en la respuesta'}
        else:
            return {'error': f'Error en el request: {response.status_code}'}
        

class TokenToken(models.Model):
    _name = "token.token"

    name = fields.Char("Nombre de Servicio")
    auth_token = fields.Char("Token de acceso")
