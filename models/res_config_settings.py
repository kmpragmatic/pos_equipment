from odoo import models, fields, api
import requests

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_token_pos_config = fields.Char(string="Auth Pos Token", config_parameter='auth_token_pos_config')
   