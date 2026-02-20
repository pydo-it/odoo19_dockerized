# 🩺 Clinic Management (Odoo 19)

Clinic Management is a professional and modular healthcare management system designed for medical clinics, private practices, and healthcare consultancies using Odoo.

The module centralizes patient information, medical records, and prescriptions, providing healthcare professionals with a secure, structured, and easy-to-use system.

---

## 🚀 Key Features

### 👤 Patient Management
- Register, update, search, and archive patient records.
- Automatic patient folio generation.
- Duplicate detection (CURP, RFC, ID, email, phone).
- Contact synchronization with `res.partner`.

### 🩺 Medical History & Clinical Encounters
- Structured clinical notes:
  - Chief complaint
  - Present illness
  - Physical exam
  - Diagnosis
  - Treatment plan
- Vital signs tracking:
  - Blood pressure
  - Heart rate
  - Temperature
  - SpO2
  - BMI (auto-calculated)
- Encounter lifecycle management:
  - `In Progress → Finalized`
- Linked prescriptions and lab results.
- Full chatter integration (mail.thread).

### 💊 Medical Prescriptions
- Linked to clinical encounters.
- Multiple medicine lines per prescription.
- Professional PDF printing (QWeb report).
- Custom paper format support.
- Automatic encounter finalization upon printing.

### 🧪 Lab Results
- Upload PDF lab results.
- Automatic preview generation (Poppler / pdftoppm).
- Embedded PDF viewer.

### 🔐 Role-Based Security
Predefined access groups:
- Clinic Admin
- Doctor
- Nurse
- Receptionist

Ensures controlled access to sensitive medical information.

### 📊 Auditability & Traceability
- Every action is tracked via Odoo chatter.
- Full traceability of medical encounters and prescriptions.
- Structured medical timeline per patient.

---

## 🔐 Security & Access Control

Clinic Management implements a role-based access model to protect sensitive medical information.

- Controlled write access to encounters.
- Read-only access when browsing from Patient view.
- Controlled state transitions.
- Secure PDF handling through Odoo attachments.

---

## 📈 Scalable & Modular

Built on top of Odoo’s modular architecture.

Easily extendable with:
- Billing & Invoicing
- Pharmacy / Inventory integration
- Accounting integration
- CRM & patient follow-up
- Online appointment booking (future roadmap)

---

## 🏥 Ideal For

- Medical clinics
- Private medical practices
- Healthcare consultancies
- Specialized medical offices

---

## ⚙️ Technical Details

- Compatible with **Odoo 19**
- Uses:
  - `mail.thread`
  - `mail.activity.mixin`
  - QWeb PDF Reports
  - Custom sequences
  - Custom paper formats
- Lab preview requires `poppler-utils` (pdftoppm)

---

## 📦 Installation

1. Copy the `clinic_management` folder into your Odoo `addons` directory.
2. Update the app list.
3. Install **Clinic Management** from the Apps menu.

---

## 🛠 Dependencies

- `base`
- `contacts`
- `calendar`
- `mail`

---

## 🗺 Roadmap

- Appointment module refinement
- E-prescription enhancements
- Multi-doctor scheduling
- Patient portal integration
- AI-assisted diagnosis (future vision)

---

## 👨‍💻 Developed by

**Luis Angel De Los Santos León**  
Odoo Developer | ERP Specialist | Healthcare IT Specialist  
📧 ldelossantos@pydo-it.com

---

## 🏢 Maintained by

**Pydo-IT Solutions & Consulting**  
Odoo Implementation & Custom Development  
🌐 https://pydo-it.com  
📧 contacto@pydo-it.com  

---