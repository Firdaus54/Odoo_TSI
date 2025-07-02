from odoo import models, fields, api
from datetime import datetime
import base64
import io
import csv

# HR Kompetensi QMS
class comp_values(models.Model):
    _name           = 'itsec.comp_values'
    _description    = 'Assesment Competency QMS'
    _rec_name       = 'name'
    _order          = 'id DESC'

    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
            domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS'])]"
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
        ('ABMS', 'ABMS'),
        ('HACCP', 'HACCP'),
        ('FSMS', 'FSMS'),
    ], string='Type Schema', store=True)
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    line_assesment_qms   = fields.One2many('itsec.line_assesment_qms', 'assesment_qms_id')

    @api.onchange('type_schema')
    def _onchange_type_schema(self):
        if self.type_schema:
            standard_kompetensi = self.env['itsec.standard.kompetensi'].search([
                ('type_schema', '=', self.type_schema)
            ], limit=1)

            self.line_assesment_qms = [(5, 0, 0)]
            lines = []

            evidence_training = ""
            evidence_experience = ""
            evidence_education = ""

            if self.name and self.type_schema:
                training_list = [
                    f"{t.name} - {t.periode}" for t in self.name.training_ids
                    if t.type_schema == self.type_schema
                ]
                experience_list = [
                    f"{e.name} - {e.periode}" for e in self.name.experience_ids
                    if e.type_schema == self.type_schema
                ]
                education_list = [
                    f"{ed.name} - {ed.periode}" for ed in self.name.education_ids
                ]

                evidence_training = "\n".join(training_list)
                evidence_experience = "\n".join(experience_list)
                evidence_education = "\n".join(education_list)

            for line in standard_kompetensi.line_standard_kompetensi:
                lines.append((0, 0, {
                    'nomor': line.no,
                    'standard': line.standard,
                    'requirement': line.requierement,
                    'evidence_training': evidence_training,
                    'evidence_experience': evidence_experience,
                    'evidence_education': evidence_education,
                }))

            self.line_assesment_qms = lines




    def set_to_running(self):
        self.write({'state': 'approval'})
        return action
# Kompetensi General
class kompetensi(models.Model):
    _name           = 'itsec.kompetensi'
    _inherit        = 'mail.thread'
    _description    = 'Kompetensi Karyawan'
    _rec_name       = 'name'
    _order          = 'id DESC'

    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    line_assesment   = fields.One2many('itsec.line_assesment_general', 'assesment_competency_id')
    hardskill_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id1')
    softskill_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id2')
    education_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id7')
    training_ids    = fields.One2many('itsec.qms_extra', 'qms_extra_id9')

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action
    
    @api.model
    def create(self, vals):
        record = super(kompetensi, self).create(vals)

        # Ambil employee yang dipilih dari field 'name'
        employee = record.name

        # Siapkan isi evidence gabungan dari employee
        evidence_combined = []

        # Pastikan 'name' (hr.employee) ada
        if employee:
            # Ambil data training, experience, dan education
            training_list = [f"Training: {t.name} - {t.periode}" for t in employee.training_ids]
            experience_list = [f"Experience: {e.name} - {e.periode}" for e in employee.experience_ids]
            education_list = [f"Education: {ed.name} - {ed.periode}" for ed in employee.education_ids]

            # Gabungkan semua evidence menjadi satu list
            evidence_combined.extend(training_list)
            evidence_combined.extend(experience_list)
            evidence_combined.extend(education_list)

        # Gabungkan semua evidence dalam satu string, dipisahkan dengan newline
        evidence_string = "\n".join(evidence_combined)

        default_lines = [
            {
                "nomor": 1,
                "requirement": "Knowledge of audit principles, practices and technique",
                "standard": (
                    "Education:\n"
                    "Has professional education which an equivalent level of university education\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year in management system practitioner as consultant or "
                    "internal auditor or Management Representative\n\n"
                    "Training:\n"
                    "Has successfully completed at least five days of training, the scope of which "
                    "covers audit management based on ISO 19011 and specific standard of management "
                    "system (e.g. QMS, EMS, FSMS)"
                )
            },
            {
                "nomor": 2,
                "requirement": "Knowledge of specific management system standard/normative document",
                "standard": (
                    "Education:\n"
                    "Has professional education which an equivalent level of university education\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year in management system practitioner as consultant or "
                    "internal auditor or Management Representative\n\n"
                    "Training:\n"
                    "Has successfully completed at least five days of training, the scope of which "
                    "covers audit management based on ISO 19011 and specific standard of management "
                    "system (e.g. QMS, EMS, FSMS)"
                )
            },
            {
                "nomor": 3,
                "requirement": "Knowledge certification Body Processes",
                "standard": (
                    "Education, Experience and training is the same with above  \n"
                    "Additional  Training  (mandatory)  :  Knowledge  about  ISO/IEC  17021-1 latest version \n\n"
                )
            },
            {
                "nomor": 4,
                "requirement": "Knowledge of business management practices",
                "standard": (
                    "Education Background :\n"
                    "Has professional  education  which    an equivalent  level  of  university education  and  Has  the  majoring related  the scope of accreditation\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year  in  the  company  with  the  same sector/business"
                    "Has at least 10 mandays as 2nd / 3rd party auditor in management system (auditexperience may be from other CB’s)\n\n"
                    "Training:\n"
                    "Has successfully completed specific training in the business/sector related the scope of accreditation."
                )
            },
            {
                "nomor": 5,
                "requirement": "Knowledge client business/sector",
                "standard": (
                    "Education Background :\n"
                    "Has professional  education  which    an equivalent  level  of  university education  and  Has  the  majoring related  the scope of accreditation\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year  in  the  company  with  the  same sector/business"
                    "Has at least 10 mandays as 2nd / 3rd party auditor in management system (auditexperience may be from other CB’s)\n\n"
                    "Training:\n"
                    "Has successfully completed specific training in the business/sector related the scope of accreditation."
                )
            },
            {
                "nomor": 6,
                "requirement": "Knowledge client product/processes and organization",
                "standard": (
                    "Education Background :\n"
                    "Has professional  education  which    an equivalent  level  of  university education  and  Has  the  majoring related  the scope of accreditation\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year  in  the  company  with  the  same sector/business"
                    "Has at least 10 mandays as 2nd / 3rd party auditor in management system (auditexperience may be from other CB’s)\n\n"
                    "Training:\n"
                    "Has successfully completed specific training in the business/sector related the scope of accreditation."
                )
            },
            {
                "nomor": 7,
                "requirement": "Language skill appropriate to all levels within the client organization",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 8,
                "requirement": "Note talking and report writing skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 9,
                "requirement": "Presentation skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 10,
                "requirement": "Interviewing skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 11,
                "requirement": "Audit Management skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            # Tambahkan baris lain jika perlu...
        ]

        for line in default_lines:
            # Buat baris 'line_assesment_general'
            line_assesment = self.env['itsec.line_assesment_general'].create({
                'assesment_competency_id': record.id,
                'nomor': line['nomor'],
                'requirement': line['requirement'],
                'standard': line['standard'],
            })

            # Buat satu record untuk evidence gabungan dalam satu line
            evidence_vals = [
                (0, 0, {
                    'training': evidence_string,  # Semua evidence digabungkan dalam satu string untuk training
                    'experience': "",  # Kosongkan karena kita sudah gabungkan dalam string 'training'
                    'education': "",  # Kosongkan karena kita sudah gabungkan dalam string 'education'
                })
            ]

            # Relasikan evidence ke 'line_assesment_general'
            line_assesment.write({
                'line_evidence_ids': evidence_vals
            })

        return record
    
    # @api.model
    # def create(self, vals):
    #     if not vals.get('line_assesment'):
    #         default_requirements = [
    #             "Knowledge of audit principles, practices and technique",
    #             "Knowledge of specific management system standard/normative document",
    #             "Knowledge certification Body Processes",
    #             "Knowledge of business management practices",
    #             "Knowledge client business/sector",
    #             "Knowledge client product/processes and organization",
    #             "Language skill appropriate to all levels within the client organization",
    #             "Note talking and report writing skills",
    #             "Presentation skills",
    #             "Interviewing skills",
    #             "Audit Management skills"
    #         ]
    #         vals['line_assesment'] = [(0, 0, {
    #             'nomor': i + 1,
    #             'requirement': req
    #         }) for i, req in enumerate(default_requirements)]
    #     return super(kompetensi, self).create(vals)

class qms_extra(models.Model):
    _name           = 'itsec.qms_extra'
    _description    = 'Extra Info'
    description     = fields.Char(string="description")
    periode         = fields.Char(string="periode")
    name            = fields.Char(string="name")
    iso_standard_ids = fields.Many2many('tsi.standard.employee', string="Standard")
    ea_code         = fields.Many2many('tsi.employee.ea_code', string="Ea Code")
    auditor         = fields.Boolean('Auditor')
    lead_auditor    = fields.Boolean('Lead Auditor')
    auditor         = fields.Boolean('Auditor')
    pk              = fields.Boolean('PK')
    keterangan      = fields.Char('Keterangan')
    compval         = fields.Many2one('itsec.comp_values', ondelete='cascade')
    qms_extra_id1   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id2   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id7   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id9   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id3   = fields.Many2one('hr.employee', ondelete='cascade')
    qms_extra_id4   = fields.Many2one('hr.employee', ondelete='cascade')
    qms_extra_id5   = fields.Many2one('hr.employee', ondelete='cascade')
    qms_extra_id6   = fields.Many2one('hr.employee', ondelete='cascade')
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
        ('ABMS', 'ABMS'),
        ('HACCP', 'HACCP'),
        ('FSMS', 'FSMS'),
    ], string='Type Schema', store=True)

#standard
class ISOStandardEmployee(models.Model):
    _name           = 'tsi.standard.employee'
    _description    = 'Standard'

    name            = fields.Char(string='Nama')
    description     = fields.Char(string='Description')
    standard        = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',  'ISPO'),
                        ], string='Standard', index=True)

class EACodeEmployee(models.Model):
    _name           = 'tsi.employee.ea_code'
    _description    = 'EA Code'

    name            = fields.Char(string='Nama', )
    description     = fields.Char(string='Description', )
    iso_standard_ids = fields.Many2many('tsi.standard.employee', string='Standards', )
    
# HR Employee
class itsec_employee(models.Model):
    _inherit        = 'hr.employee'
    _description    = 'Personnel'
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    file_bin1       = fields.Binary('NDA')
    file_name1      = fields.Char('Filename NDA')
    file_bin2       = fields.Binary('Background Checking')
    file_name2      = fields.Char('Filename Background')
    file_bin3       = fields.Binary('Exit Clearance')
    file_name3      = fields.Char('Filename Clearance')
    file_bin4       = fields.Binary('Access Privilege')
    file_name4      = fields.Char('Filename Provilege')
    file_bin5       = fields.Binary('Certificate')
    file_name5      = fields.Char('Filename Certificate')
    training_ids    = fields.One2many('itsec.qms_extra', 'qms_extra_id3')
    experience_ids  = fields.One2many('itsec.qms_extra', 'qms_extra_id4')
    education_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id5')
    skill_ids       = fields.One2many('itsec.qms_extra', 'qms_extra_id6')
    audit_exp_ids   = fields.One2many('itsec.emp_audit', 'emp_audit_id')
    consultat_log_ids   = fields.One2many('itsec.consultan.log', 'emp_consultant_id')
    site_mandays_ids   = fields.One2many('itsec.site_mandays', 'site_mandays_id')
    # ass_competency_ids  = fields.One2many('itsec.assesment_general','assesment_competency_id')
    auditor = fields.Selection([
                            ('Yes', 'Yes'),
                            ('No', 'No'),
                        ], string='Auditor', index=True, tracking=True,)
    
    def action_import_personal_information(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Data Wizard',
            'res_model': 'tsi.wizard.personal.information',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id
            }
        }

    # def action_import_audit_exp(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Import Audit Log',
    #         'res_model': 'tsi.wizard.audit.log',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'default_emp_audit_id': self.id}
    #     }
    
    # def action_import_auditor_skill(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Import Auditor Skill',
    #         'res_model': 'tsi.wizard.audit.skill',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'default_qms_extra_id6': self.id}
    #     }

class emp_audit(models.Model):
    _name           = 'itsec.emp_audit'
    _description    = 'Employee Audit'

    emp_audit_id    = fields.Many2one('hr.employee', ondelete='cascade')
    comp_name       = fields.Char(string="Client Name")
    standard        = fields.Char(string="standard")
    audit_date      = fields.Date(string="Audit Date")
    mandays         = fields.Char(string="Mandays")
    role            = fields.Char(string="role")
    audit_type      = fields.Char(string="Audit Type")
    ea_code         = fields.Many2many('tsi.employee.ea_code', string="Ea Code")
    audit_behalf    = fields.Char(string="Audit on Behalf")

class emp_site_mandays(models.Model):
    _name           = 'itsec.site_mandays'
    _description    = 'Mandays Auditor'

    site_mandays_id     = fields.Many2one('hr.employee', ondelete='cascade')
    mandays             = fields.Char(string="Mandays")
    harga_mandays       = fields.Float(string="Harga Mandays")

class assesment_scope(models.Model):
    _name           = 'itsec.assesment_scope'
    _description    = 'Assesment Scoper'

    assesment_scope_id    = fields.Many2one('itsec.jobdesc', ondelete='cascade')
    ass_scope_food_id    = fields.Many2one('itsec.assesment_scope_food', ondelete='cascade')
    ass_scope_haccp_id    = fields.Many2one('itsec.assesment_scope_food_haccp', ondelete='cascade')
    ass_scope_eoms_id    = fields.Many2one('itsec.assesment_scope_eoms', ondelete='cascade')
    nomor                 = fields.Char(string="Nomor")
    requirement           = fields.Text(string="REQUIREMENT")
    standard              = fields.Text(string="STANDARD")
    ass_method            = fields.Char(string="ASSESMENT METHOD")
    evaluator_comment     = fields.Char(string="EVALUATOR COMMENT")
    line_evidence_ids = fields.One2many('itsec.line_evidence', 'reference_id1')
    evidence_education = fields.Text(string="Evidence - Education", compute="_compute_evidence_fields")
    evidence_experience = fields.Text(string="Evidence - Experience", compute="_compute_evidence_fields")
    evidence_training = fields.Text(string="Evidence - Training", compute="_compute_evidence_fields")

    @api.depends('line_evidence_ids')
    def _compute_evidence_fields(self):
        for rec in self:
            education_list = [str(e) for e in rec.line_evidence_ids.mapped('education') if e]
            experience_list = [str(e) for e in rec.line_evidence_ids.mapped('experience') if e]
            training_list = [str(e) for e in rec.line_evidence_ids.mapped('training') if e]

            rec.evidence_education = ', '.join(education_list)
            rec.evidence_experience = ', '.join(experience_list)
            rec.evidence_training = ', '.join(training_list)

# class assesment_general(models.Model):
#     _name           = 'itsec.assesment_general'
#     _description    = 'Assesment General'

#     assesment_competency_id = fields.Many2one(
#         'itsec.kompetensi', ondelete='cascade'
#     )
#     nomor                   = fields.Char(string="No")
#     requirement             = fields.Char(string="Requirement")
#     standard                = fields.Char(string="Standard")
#     evaluator_comment       = fields.Char(string="Evaluator Comment")
#     ass_method              = fields.Char(string="Assesment Method")
#     line_evidence_ids       = fields.One2many('itsec.evidence','evidence_ids')
#     evidence_education = fields.Char(string="Evidence - Education", compute="_compute_evidence_fields")
#     evidence_experience = fields.Char(string="Evidence - Experience", compute="_compute_evidence_fields")
#     evidence_training = fields.Char(string="Evidence - Training", compute="_compute_evidence_fields")

#     @api.depends('line_evidence_ids')
#     def _compute_evidence_fields(self):
#         for rec in self:
#             rec.evidence_education = ', '.join(rec.line_evidence_ids.mapped('education'))
#             rec.evidence_experience = ', '.join(rec.line_evidence_ids.mapped('experience'))
#             rec.evidence_training = ', '.join(rec.line_evidence_ids.mapped('training'))

class AssesmentCompetencyGeneral(models.Model):
    _name           = 'itsec.line_assesment_general'
    _description    = 'Assesment Kompetensi General'

    assesment_competency_id = fields.Many2one(
        'itsec.kompetensi', ondelete='cascade'
    )
    nomor                   = fields.Char(string="No")
    requirement             = fields.Text(string="Requirement")
    standard                = fields.Text(string="Standard")
    evaluator_comment       = fields.Char(string="Evaluator Comment")
    ass_method              = fields.Char(string="Assesment Method")
    line_evidence_ids       = fields.One2many('itsec.line_evidence','evidence_ids')
    evidence_education = fields.Text(string="Evidence - Education", compute="_compute_evidence_fields")
    evidence_experience = fields.Text(string="Evidence - Experience", compute="_compute_evidence_fields")
    evidence_training = fields.Text(string="Evidence - Training", compute="_compute_evidence_fields")

    @api.depends('line_evidence_ids')
    def _compute_evidence_fields(self):
        for rec in self:
            education_list = [str(e) for e in rec.line_evidence_ids.mapped('education') if e]
            experience_list = [str(e) for e in rec.line_evidence_ids.mapped('experience') if e]
            training_list = [str(e) for e in rec.line_evidence_ids.mapped('training') if e]

            rec.evidence_education = ', '.join(education_list)
            rec.evidence_experience = ', '.join(experience_list)
            rec.evidence_training = ', '.join(training_list)


class AssesmentCompetencyQMS(models.Model):
    _name           = 'itsec.line_assesment_qms'
    _description    = 'Assesment Kompetensi QMS'

    assesment_qms_id = fields.Many2one(
        'itsec.comp_values', ondelete='cascade'
    )
    nomor                   = fields.Char(string="No")
    requirement             = fields.Text(string="Requirement")
    standard                = fields.Text(string="Standard")
    evaluator_comment       = fields.Char(string="Evaluator Comment")
    ass_method              = fields.Char(string="Assesment Method")
    line_evidence_ids       = fields.One2many('itsec.line_evidence','reference_id')
    evidence_education = fields.Text(string="Evidence - Education", compute="_compute_evidence_fields")
    evidence_experience = fields.Text(string="Evidence - Experience", compute="_compute_evidence_fields")
    evidence_training = fields.Text(string="Evidence - Training", compute="_compute_evidence_fields")
    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
    ], string='Type Schema', related="assesment_qms_id.type_schema")

    @api.depends('assesment_qms_id.name')
    def _compute_evidence_fields(self):
        for rec in self:
            emp = rec.assesment_qms_id.name
            if emp:
                rec.evidence_education = '\n'.join([
                    f"{edu.name} ({edu.periode})" if edu.periode else edu.name
                    for edu in emp.education_ids
                ])
                rec.evidence_experience = '\n'.join([
                    f"{exp.name} ({exp.periode})" if exp.periode else exp.name
                    for exp in emp.experience_ids
                ])
                rec.evidence_training = '\n'.join([
                    f"{train.name} ({train.periode})" if train.periode else train.name
                    for train in emp.training_ids
                ])
            else:
                rec.evidence_education = ""
                rec.evidence_experience = ""
                rec.evidence_training = ""

    @api.depends('line_evidence_ids')
    def _compute_evidence_fields(self):
        for rec in self:
            education_list = [str(e) for e in rec.line_evidence_ids.mapped('education') if e]
            experience_list = [str(e) for e in rec.line_evidence_ids.mapped('experience') if e]
            training_list = [str(e) for e in rec.line_evidence_ids.mapped('training') if e]

            rec.evidence_education = ', '.join(education_list)
            rec.evidence_experience = ', '.join(experience_list)
            rec.evidence_training = ', '.join(training_list)

    # @api.depends('line_evidence_ids')
    # def _compute_evidence_fields(self):
    #     for rec in self:
    #         education_list = [str(e) for e in rec.line_evidence_ids.mapped('education') if e]
    #         experience_list = [str(e) for e in rec.line_evidence_ids.mapped('experience') if e]
    #         training_list = [str(e) for e in rec.line_evidence_ids.mapped('training') if e]

    #         rec.evidence_education = ', '.join(education_list)
    #         rec.evidence_experience = ', '.join(experience_list)
    #         rec.evidence_training = ', '.join(training_list)
    

class StandardKompetensi(models.Model):
    _name           = 'itsec.standard.kompetensi'
    _description    = 'Standard Kompetensi'
    _rec_name       = 'type_schema'
    _order          = 'id DESC'

    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
        ('ABMS', 'ABMS'),
        ('HACCP', 'HACCP'),
        ('FSMS', 'FSMS'),
    ], string='Type Schema', store=True)
    # standard          = fields.Char(string="Education")
    # requierement      = fields.(string="Experience")
    line_standard_kompetensi = fields.One2many('itsec.line.standard.kompetensi', 'standard_kompetensi_id')

class LineStandardKompetensi(models.Model):
    _name           = 'itsec.line.standard.kompetensi'
    _description    = 'Line Standard Kompetensi'

    standard_kompetensi_id = fields.Many2one(
         'itsec.standard.kompetensi', ondelete='cascade'
    )
    no = fields.Char(string="No")
    standard          = fields.Text(string="Standard")
    requierement      = fields.Text(string="Requierement")

class ConsultanLog(models.Model):
    _name           = 'itsec.consultan.log'
    _description    = 'Consultan Log'

    emp_consultant_id   = fields.Many2one('hr.employee', ondelete='cascade')
    comp_name           = fields.Char(string="Company Name")
    standard            = fields.Char(string="Schema")
    duration            = fields.Char(string="Duration")
    busines             = fields.Char(string="Business Sector")


class AssmentEvidence(models.Model):
    _name           = 'itsec.line_evidence'
    _description    = 'Lines Assesment Evidence'

    evidence_ids    = fields.Many2one('itsec.line_assesment_general', ondelete='cascade')
    reference_id    = fields.Many2one('itsec.line_assesment_qms', ondelete='cascade')
    reference_id1    = fields.Many2one('itsec.assesment_scope', ondelete='cascade')
    education       = fields.Text(string="Education")
    experience      = fields.Text(string="Experience")
    training        = fields.Text(string="Training")

class JobPosition(models.Model):
    _name           = 'itsec.position'
    _description    = 'JOb Position'

    name               = fields.Char(string="Name")
    description        = fields.Char(string="Description")

class qms_jobdesc(models.Model):
    _name = 'itsec.jobdesc'
    _inherit        = 'mail.thread'
    _description    = 'Assesment Competency Scoper'
    _rec_name       = 'name'

    ass_scope_ids   = fields.One2many('itsec.assesment_scope', 'assesment_scope_id')
    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
            domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS'])]"
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    # Ini untuk Technical Scope
    conclusion = fields.Text(string="Conclusion")
    agriculture = fields.Boolean(string="01 Agriculture, forestry and fishing")
    mining = fields.Boolean(string="02 Mining & Quarrying")
    food_products = fields.Boolean(string="03 Food products, beverages and tobacco")
    textiles = fields.Boolean(string="04 Textiles and textile products")
    leather = fields.Boolean(string="05 Leather and leather products")
    wood = fields.Boolean(string="06 Wood and wood products")
    pulp_paper = fields.Boolean(string="07 Pulp, paper and paper products")
    publishing = fields.Boolean(string="08 Publishing companies")
    printing = fields.Boolean(string="09 Printing companies")
    petroleum = fields.Boolean(string="10 Manufacture of coke and refined petroleum products")
    nuclear_fuel_1 = fields.Boolean(string="11 Nuclear fuel")
    chemical = fields.Boolean(string="12 Chemical, Chemicals product and fibres")
    nuclear_fuel_2 = fields.Boolean(string="13 Nuclear fuel")
    rubber = fields.Boolean(string="14 Rubber and plastic products")
    non_metallic = fields.Boolean(string="15 Non-metallic mineral products")
    concrete = fields.Boolean(string="16 Concrete, cement, lime plaster, etc")
    basic_metal = fields.Boolean(string="17 Basic metal and fabricated metal products")
    machinery = fields.Boolean(string="18 Machinery and equipment")
    electrical_equipment = fields.Boolean(string="19 Electrical and optical equipment")
    shipbuilding = fields.Boolean(string="20 Shipbuilding")
    aerospace = fields.Boolean(string="21 Aerospace")
    other_transport = fields.Boolean(string="22 Other transport equipment")
    manufacturing_other = fields.Boolean(string="23 Manufacturing not elsewhere classified")
    recycling = fields.Boolean(string="24 Recycling")
    electricity_supply = fields.Boolean(string="25 Electricity supply")
    gas_supply = fields.Boolean(string="26 Gas supply")
    water_supply = fields.Boolean(string="27 Water supply")
    construction = fields.Boolean(string="28 Construction")
    wholesale_repair = fields.Boolean(string="29 Wholesale and retail trade; Repair of motor vehicles, motorcycles and personal and household goods")
    hotels_restaurants = fields.Boolean(string="30 Hotels and restaurants")
    transport_storage = fields.Boolean(string="31 Transport, storage and communication")
    financial_realestate = fields.Boolean(string="32 Financial intermediation; real estate; renting")
    information_tech = fields.Boolean(string="33 Information technology")
    engineering_services = fields.Boolean(string="34 Engineering services")
    other_services = fields.Boolean(string="35 Other services")
    public_admin = fields.Boolean(string="36 Public administration")
    education = fields.Boolean(string="37 Education")
    health_social = fields.Boolean(string="38 Health and social work")
    social_services = fields.Boolean(string="39 Other social services")

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action

class AssesnmentScopeFood(models.Model):
    _name = 'itsec.assesment_scope_food'
    _inherit        = 'mail.thread'
    _description    = 'Assesment Competency Scope FSMS'
    _rec_name       = 'name'

    ass_scope_food_ids   = fields.One2many('itsec.assesment_scope', 'ass_scope_food_id')
    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
            domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS'])]"
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    # Ini untuk Technical Scope
    conclusion = fields.Text(string="Conclusion")
    # A - Farming
    farming_animals = fields.Boolean(string="A I Farming of Animals for meat/milk/eggs/honey")
    farming_fish = fields.Boolean(string="A II Farming of fish and Seafood")

    # B - Plant Farming
    farming_plants = fields.Boolean(string="B I Farming – Handling of Plants (other than grains and pulses)")
    farming_grains = fields.Boolean(string="B II Farming – Handling of Grains and pulses")
    preprocess_plant = fields.Boolean(string="B III Pre-process Handling of Plant Products")

    # C - Processing
    animal_primary_conversion = fields.Boolean(string="C 0 Animal-Primary Conversion")
    processing_animal = fields.Boolean(string="C I Processing of perishable animal products")
    processing_plant = fields.Boolean(string="C II Processing of perishable plant-based products")
    processing_mixed = fields.Boolean(string="C III Processing of perishable animal and plant products (mixed product)")
    processing_ambient = fields.Boolean(string="C IV Processing of ambient stable products")

    # D to K - Other Sectors
    feed_processing = fields.Boolean(string="D Feed and Animal Food Processing")
    catering_services = fields.Boolean(string="E Catering / Food Services")
    retail = fields.Boolean(string="F I Retail / Wholesale")
    brokering = fields.Boolean(string="F II Brokering / Trading")
    transport_storage = fields.Boolean(string="G Transport and Storage Services")
    services = fields.Boolean(string="H Services")
    packaging_production = fields.Boolean(string="I Production of Packaging Material")
    equipment = fields.Boolean(string="J Equipment")
    bio_chemicals = fields.Boolean(string="K Production of (Bio) Chemicals")

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action

class AssesnmentScopeFoodHACCP(models.Model):
    _name = 'itsec.assesment_scope_food_haccp'
    _inherit        = 'mail.thread'
    _description    = 'Assesment Competency Scope HACCP'
    _rec_name       = 'name'

    ass_scope_food_haccp_ids   = fields.One2many('itsec.assesment_scope', 'ass_scope_haccp_id')
    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
            domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS'])]"
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    # Ini untuk Technical Scope
    conclusion = fields.Text(string="Conclusion")
    product_milk = fields.Boolean(string="01.0 Products of milk and its analogs")
    fats_oils = fields.Boolean(string="02.0 Fats, oils, and emulsions of oil")
    ice_cream = fields.Boolean(string="03.0 Ice to eat")
    fruit_veg = fields.Boolean(string="04.0 Fruit and Vegetable")
    flower_sugar = fields.Boolean(string="05.0 Flower sugar / candy and chocolate")
    cereal_products = fields.Boolean(string="06.0 Cereals and cereal products")
    bakery_products = fields.Boolean(string="07.0 Bakery products")
    meat_products = fields.Boolean(string="08.0 Meat and meat products")
    fish_products = fields.Boolean(string="09.0 Fish and fishery products")
    eggs_products = fields.Boolean(string="10.0 Eggs and egg products")
    sugar_honey = fields.Boolean(string="11.0 Sugar and Sweeteners, including honey")
    salt_sauces = fields.Boolean(string="12.0 Salt, spices, soups, sauces, salads, protein products")
    special_nutrition = fields.Boolean(string="13.0 Processed food for special nutritional needs")
    beverages = fields.Boolean(string="14.0 Beverages, not including the products of milk")
    snack = fields.Boolean(string="15.0 Ready to eat snack")
    ready_food = fields.Boolean(string="16.0 Ready to eat food (packed)")
    food_contact = fields.Boolean(string="17.0 Food Contact material")
    feed_animals = fields.Boolean(string="18.0 Production of Feed Animals")
    catering = fields.Boolean(string="19.0 Catering")
    distribution = fields.Boolean(string="20.0 Distribution")
    transport_services = fields.Boolean(string="21.0 Provider of transportation and storage services")
    supporting_services = fields.Boolean(string="22.0 Supporting services")
    food_packaging = fields.Boolean(string="23.0 Production of food packaging and food packaging materials")
    equipment_fabrication = fields.Boolean(string="24.0 Fabrication of equipment")
    bio_chemical = fields.Boolean(string="25.0 Production of materials (bio) chemical")

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action

class AssesnmentScopeEOMS(models.Model):
    _name = 'itsec.assesment_scope_eoms'
    _inherit        = 'mail.thread'
    _description    = 'Assesment Competency Scope EOMS'
    _rec_name       = 'name'

    ass_scope_eoms_ids   = fields.One2many('itsec.assesment_scope', 'ass_scope_eoms_id')
    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
            domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS'])]"
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    # Ini untuk Technical Scope
    conclusion = fields.Text(string="Conclusion")
    early = fields.Boolean(string="01 Early Childhood Education")
    primary = fields.Boolean(string="02 Primary and Secondary Education")
    high_education = fields.Boolean(string="03 Higher Education")
    educational = fields.Boolean(string="04 Educational Organizations (other than 1, 2, 3)")

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action


# Worker Representative
class qms_worker_rep(models.Model):
    _name = 'itsec.qms_worker_rep'
    _inherit        = 'mail.thread'
    _description    = 'Worker Representative'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    name            = fields.Char(string="name")
    pic             = fields.Char(string="pic")
    address         = fields.Text(string="address")
    phone           = fields.Char(string="phone")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Worker Representative Contract
class qms_worker_rep_contract(models.Model):
    _name = 'itsec.qms_worker_rep_contract'
    _inherit        = 'mail.thread'
    _description    = 'Worker Representative Contract'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    worker_rep      = fields.Many2one('itsec.qms_worker_rep', ondelete='cascade', string="Representative", required=True)
    contract_title  = fields.Char(string="contract_title")
    contract_date   = fields.Date(default=datetime.today())
    expired_date    = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Worker Representative Meeting
class qms_worker_rep_meet(models.Model):
    _name = 'itsec.qms_worker_rep_meet'
    _inherit        = 'mail.thread'
    _description    = 'Worker Representative Meeting'
    name            = fields.Char(required=True)
    worker_rep      = fields.Many2one('itsec.qms_worker_rep', ondelete='cascade', string="Representative", required=True)
    tanggal         = fields.Date(default=datetime.today())
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

