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

    _sql_constraints = [
        ('name_unique', 'unique(name)', "The name number is unique for each serial.!"),
        ('serial_char_id_unique', 'unique(serial_char_id)', "The serial_char_id number is unique for each serial.!"),
    ]

    @api.model
    def create(self, vals):
        if self.env['pos.seriales'].search([('name', '=', vals['name'])]):
            raise UserError("El número de serie '%s' ya existe." % vals['name'])
        if self.env['pos.seriales'].search([('serial_char_id', '=', vals['serial_char_id'])]):
            raise UserError("El identificador '%s' ya existe." % vals['serial_char_id'])
        return super(PosSeriales, self).create(vals)
