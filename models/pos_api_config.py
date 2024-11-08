from odoo import api, fields, models
from odoo.exceptions import UserError

class PosApiConfig(models.Model):
    _name = 'pos.api.config'

    name = fields.Char()
    payment_delay_validation = fields.Integer('Tiempo de validacion (seg)', default=0)

