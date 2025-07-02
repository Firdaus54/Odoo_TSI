# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import humanize
import os

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
    attachment = fields.Binary('Attachment')
    # document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    document_size = fields.Float(string='Document Size', compute='_compute_document_size', store=True)
    file_name       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')


    # @api.depends('attachment')
    # def _compute_document_size(self):
    #     for record in self:
    #         if record.attachment:
    #             # Menghitung ukuran file dalam KB
    #             record.document_size = len(record.attachment) / (1024.0)
    #         else:
    #             record.document_size = 0.0

    # @api.depends('attachment')
    # def _compute_document_size(self):
    #     for record in self:
    #         if record.attachment:
    #             # Menghitung ukuran file dalam byte
    #             size_in_bytes = len(record.attachment)
    #             # Mengkonversi ukuran file ke KB
    #             size_in_kb = size_in_bytes / 1024.0
    #             record.document_size = size_in_kb
    #         else:
    #             record.document_size = 0.0

    @api.onchange('attachment')
    def onchange_attachment(self):
        if self.attachment:
            # Mendapatkan record attachment
            attachment = self.env['ir.attachment'].search([('res_model', '=', 'skema.food'), ('res_id', '=', self.id)], limit=1)
            if attachment:
                # Mendapatkan nama file attachment
                attachment_name = attachment.name
                filename, extension = os.path.splitext(attachment_name)
                if extension.lower() == '.pdf':
                    self.document_type = 'pdf'
                elif extension.lower() == '.docx':
                    self.document_type = 'docx'
                elif extension.lower() == '.xls' or extension.lower() == '.xlsx':
                    self.document_type = 'xls'
                else:
                    self.document_type = False

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

    def send_email(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_food', False):
                template_id = ir_model_data._xmlid_lookup('keluarga.email_template_edi_food')[2]
            else:
                template_id = ir_model_data._xmlid_lookup('keluarga.email_template_edi_food_done')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'skema.food',
            'active_model': 'skema.food',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

        self = self.with_context(lang=lang)

        return {
            'name': _('Food Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     @api.model
#     def write(self, vals):
#         # Panggil fungsi write dari superclass
#         res = super(ResUsers, self).write(vals)

#         # Ambil user yang login saat ini
#         current_user = self.env.user

#         # Cari catatan skema.food yang uploader-nya adalah user yang saat ini login
#         foods = self.env['skema.food'].sudo().search([('uploader', '=', False)])

#         # Isi field uploader dengan user yang saat ini login
#         if current_user and foods:
#             foods.write({'uploader': current_user.id})

#         return res