# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pos Equipment",
    "version": "17.0.1.0.1",
    "license": "AGPL-3",
    "author": "CTiEG",
    "website": "https://www.ctieg.com/",
    "depends": ["point_of_sale",'pos_online_payment', 'billon_integration'],
    "data": [
                "security/ir.model.access.csv", 
                "views/res_config_settings_views.xml",
                "views/pos_order.xml",
                "views/pos_equipment.xml",
                "views/payment_method.xml",
                "views/pos_payment.xml",
                "views/auth_token_view.xml",

                "views/pos_config.xml",
                "views/transaction_response.xml",
                "views/pos_seriales.xml",
                "views/account_move.xml",

                
                #"views/payment_extend.xml",
    ],
    "maintainers": ["CTiEG"],
    'assets': {
         'point_of_sale._assets_pos': [
            'pos_equipment/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
