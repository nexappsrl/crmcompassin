# -*- coding: utf-8 -*-
{
    'name': "na_linkdanea",

    'summary': """
        Modulo per la lettura dei dati da Syncdanea""",

    'description': """
        permette al modulo SyncDanea di salvare i dati a seconda delle customizzazioni.
    """,

    'author': "Nexapp",
    'website': "http://www.nexapp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale_management','stock'],

    # always loaded
    'data': [
        'security/linkdanea_security.xml',
        'security/ir.model.access.csv',
        'views/linkdanea_menu.xml',
        'views/product_views.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
    'installable':True,
    'external_dependencies': {
        'python': [
            'phonenumbers'
        ]
    }

}
