from odoo import models, fields, api
from datetime import datetime

class SkemaXMS(models.Model):
    _name = 'skema.xms'
    _description = 'Data Skema XMS'
    _order          = 'id DESC'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('skema.xms') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(SkemaXMS, self).create(vals)
        return result

class SkemaFood(models.Model):
    _name = 'skema.food'
    _description = 'Data Skema Food'
    _order          = 'id DESC'

    # @api.model
    # def _get_upload(self):
    #     return self.env.user.name

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Document Number")
    upload_date = fields.Datetime(string="Issued Date", default=datetime.today())
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    # document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    document_size = fields.Float(string='Document Size', compute='_compute_document_size', store=True)
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('skema.food') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(SkemaFood, self).create(vals)
        return result

class SkemaLvv(models.Model):
    _name = 'skema.lvv'
    _description = 'Data Skema LVV'
    _order          = 'id DESC'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('skema.lvv') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(SkemaLvv, self).create(vals)
        return result

class SkemaICT(models.Model):
    _name = 'skema.ict'
    _description = 'Data Skema ICT'
    _order          = 'id DESC'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('skema.ict') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(SkemaICT, self).create(vals)
        return result

class SustainabilitySkema(models.Model):
    _name = 'sustainability.skema'
    _description = 'Data Sustainability'
    _order          = 'id DESC'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('sustainability.skema') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(SustainabilitySkema, self).create(vals)
        return result

class Manual(models.Model):
    _name = 'tsi.manual'
    _description = 'Data Manual'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.manual') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Manual, self).create(vals)
        return result

class Manual17065(models.Model):
    _name = 'tsi.manual.17065'
    _description = 'Data Manual 17065'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.manual.17065') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Manual17065, self).create(vals)
        return result


class ManualOthers(models.Model):
    _name = 'tsi.manual.others'
    _description = 'Data Manual Others'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.manual.others') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(ManualOthers, self).create(vals)
        return result
    

class Form(models.Model):
    _name = 'tsi.form'
    _description = 'Data Form'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.form') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Form, self).create(vals)
        return result

class Form17065(models.Model):
    _name = 'tsi.form.17065'
    _description = 'Data Form 17065'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.form.17065') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Form17065, self).create(vals)
        return result


class FormOthers(models.Model):
    _name = 'tsi.form.others'
    _description = 'Data Form Others'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.form.others') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(FormOthers, self).create(vals)
        return result

class Prosedur(models.Model):
    _name = 'tsi.prosedur'
    _description = 'Data Prosedur'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.prosedur') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Prosedur, self).create(vals)
        return result

class Prosedur17065(models.Model):
    _name = 'tsi.prosedur.17065'
    _description = 'Data Prosedur'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.prosedur.17065') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Prosedur17065, self).create(vals)
        return result

class ProsedurOthers(models.Model):
    _name = 'tsi.prosedur.others'
    _description = 'Data Prosedur Others'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.prosedur.others') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(ProsedurOthers, self).create(vals)
        return result

class Police(models.Model):
    _name = 'tsi.pd.policy'
    _description = 'Data Policy'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    # authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.pd.policy') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Police, self).create(vals)
        return result

class Letter(models.Model):
    _name = 'tsi.pd.letter'
    _description = 'Data Letter'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    # authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.pd.letter') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Letter, self).create(vals)
        return result


class Others(models.Model):
    _name = 'tsi.pd.others'
    _description = 'Data Others'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Upload PDF')
    attachment_1 = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    file_name_1       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    # authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('tsi.pd.others') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(Others, self).create(vals)
        return result