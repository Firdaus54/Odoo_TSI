from odoo import api, fields, models, _

class ResPartnerClient(models.Model):
    _inherit        = "res.partner"

    contact_client_ids = fields.One2many('res.partner.contact.client', 'partner_id', string="Custom Contacts")


    hide_contact_franchise = fields.Boolean(compute='_compute_hide_contact_franchise', store=True)
    
    @api.depends('is_company', 'contact_client')
    def _compute_hide_contact_franchises(self):
        for record in self:
            record.hide_contact_franchises = record.is_company and record.contact_client


    def open_contact_client_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Contact Wizard',
            'res_model': 'contact.client.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }

class ResPartnerContactClient(models.Model):
    _name = 'res.partner.contact.client'
    _description = 'Custom Contact'

    name_client = fields.Many2one('res.partner', string="PIC", domain="[('is_company', '=', False)]",readonly=True)
    phone_client = fields.Char(string="Phone",readonly=True, related="partner_id.phone")
    email_client = fields.Char(string="Email",readonly=True, related="partner_id.email")
    address_client = fields.Char(string="Address",readonly=True)
    jabatan         = fields.Char(string="Position", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Partner",readonly=True)

class ContactClientWizard(models.TransientModel):
    _name = 'contact.client.wizard'
    _description = 'Custom Contact Wizard'

    associate_id = fields.Many2one('res.partner', string="Associate", domain="[('is_company', '=', False)]")
    phone_client = fields.Char(string="Phone")
    email_client = fields.Char(string="Email")
    address_client = fields.Char(string="Address")

    @api.onchange('associate_id')
    def _onchange_name_client(self):
        if self.associate_id:
            self.address_client = self.associate_id.office_address
            self.phone_client = self.associate_id.phone
            self.email_client = self.associate_id.email
        else:
            self.address_client = False
            self.phone_client = False
            self.email_client = False

    def action_save(self):
        partner_id = self.env.context.get('default_partner_id')
        if partner_id:
            # Ambil partner yang sedang aktif
            partner = self.env['res.partner'].browse(partner_id)
            phone = partner.phone
            email = partner.email
            office_address = partner.office_address
            function = partner.function
            
            # Update data res.partner dengan data dari wizard
            if self.associate_id:
                self.associate_id.write({
                    'phone': self.phone_client,
                    'email': self.email_client,
                    'office_address': self.address_client,
                    'function': self.jabatan,
                })
            
            # Buat entri baru di res.partner.custom.contacts
            self.env['res.partner.contact.client'].create({
                'name_client': self.associate_id.id,
                'phone_client': self.phone_client,
                'email_client': self.email_client,
                'address_client': self.address_client,
                'jabatan': self.jabatan,
                'partner_id': partner.id,
            })
            
            # Buat entri baru di res.partner.custom.contact
            partner = self.env['res.partner'].browse(partner_id)
            self.env['res.partner.contact.client'].create({
                'name_client': partner.id,
                'phone_client': phone,
                'email_client': email,
                'address_client': office_address,
                'jabatan': function,
                'partner_id': self.associate_id.id,
            })

