from odoo import api, fields, models
from odoo.exceptions import UserError

class PosSeriales(models.Model):
    _name = 'pos.seriales'

    name = fields.Char('Nro. Serie')
    serial_char_id = fields.Char('Identificador')
    
    company_id = fields.Many2one(
        string='Venta vinculada',
        comodel_name='res.company'
    )

