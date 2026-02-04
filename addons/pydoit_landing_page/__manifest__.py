# -*- coding: utf-8 -*-
{
    'name': 'Pydo-IT Landing Page',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Landing page coded from scratch for Pydo-IT Odoo consulting',
    'author': 'Pydo-IT Solutions & Consulting',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'crm',
        'website_crm',
    ],
    'data': [
        'views/hide_header.xml',
        'views/hide_footer.xml',
        'views/landing_header.xml',
        'views/landing_page.xml',
        'views/thank_you_page.xml',
        'data/website.xml',
        'views/website_menu.xml',
        'views/header_contact_button.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pydoit_landing_page/static/src/scss/pydoit_landing.scss',
            'pydoit_landing_page/static/src/js/pydoit_landing.js',
        ],
    },
    'images': [
        'static/src/img/imagotipo_3.png',
        'static/src/img/imagotipo_horizontal.png',
        'static/src/img/mascota_saludando.png',
    ],
    'application': False,
    'installable': True,
}
