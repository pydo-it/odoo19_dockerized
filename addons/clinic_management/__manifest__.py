# -*- coding: utf-8 -*-
{
    'name': 'Clinic Management',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Patients, medical records, appointments and prescriptions for clinics.',
    'description': """
Clinic Management is a modular healthcare management system for Odoo.

Key Features:
- Patient management (create, update, archive)
- Medical history and clinical encounters
- Medical prescriptions with printable PDF format
- Appointment scheduling with calendar integration
- Role-based access control (Admin, Doctor, Nurse, Receptionist)

Designed to be scalable and easy to extend with billing, inventory, and reporting.
""",
    'author': 'Pydo-IT Solutions & Consulting',
    'website': 'https://pydo-it.com',
    'support': 'ldelossantos@pydo-it.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'calendar',
        'mail',
    ],
    'data': [
        # Security
        'security/clinic_management_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/medical_patients_sequence.xml',
        'data/medical_encounter_sequence.xml',
        'data/medical_lab_result_sequence.xml',
        'data/medical_prescription_sequence.xml',
        
        # Wizards
        'wizards/medical_lab_result_pdf_preview_wizard_views.xml',
        
        # Reports
        'reports/paperformat_medical_prescription.xml',
        'reports/medical_prescription_report.xml',
        'reports/report_medical_prescription_templates.xml',
        
        # Views
        'views/medical_encounter_actions.xml',
        'views/medical_prescription_actions.xml',
        'views/medical_encounter_views.xml',
        'views/medical_patients_views.xml',
        'views/medical_lab_result_views.xml',
        'views/medical_prescription_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        # por ahora vacío está bien
    },
    # Imágenes para Odoo Apps (icono y/o screenshots)
    'images': [
        'static/description/icon.png',
        # si luego agregas screenshots:
        # 'static/description/screenshot_01.png',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}