from odoo import api, fields, models, _

class ResPartnerAssociate(models.Model):
    _inherit        = "res.partner"

    custom_contact_ids = fields.One2many('res.partner.custom.contact', 'partner_id', string="Custom Contacts")
    custom_contact_idss = fields.One2many('res.partner.custom.contacts', 'partner_ids', string="Custom Contactss")
    
    show_internal_notess = fields.Boolean(compute='_compute_show_internal_notess', store=True)
    
    @api.depends('is_company', 'contact_client')
    def _compute_show_internal_notess(self):
        for record in self:
            record.show_internal_notess = record.is_company and record.contact_client
            

    def open_custom_contact_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Contact Wizard',
            'res_model': 'custom.contact.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }
        
    def open_custom_contact_wizards(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Contact Wizards',
            'res_model': 'custom.contact.wizards',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }

class ResPartnerCustomContact(models.Model):
    _name = 'res.partner.custom.contact'
    _description = 'Custom Contact'

    name_associate = fields.Many2one('res.partner', string="Client", domain="[('is_company', '=', True)]",readonly=True)
    phone_associate = fields.Char(string="Phone",readonly=True)
    email_associate = fields.Char(string="Email",readonly=True)
    address_associate = fields.Char(string="Address",readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner",readonly=True)

class CustomContactWizard(models.TransientModel):
    _name = 'custom.contact.wizard'
    _description = 'Custom Contact Wizard'

    company_id = fields.Many2one('res.partner', string="Company", domain="[('is_company', '=', True)]")
    phone_associate = fields.Char(string="Phone")
    email_associate = fields.Char(string="Email")
    address_associate = fields.Char(string="Address")

    @api.onchange('company_id')
    def _onchange_name_associate(self):
        if self.company_id:
            self.address_associate = self.company_id.office_address
            self.phone_associate = self.company_id.phone
            self.email_associate = self.company_id.email
        else:
            self.address_associate = False
            self.phone_associate = False
            self.email_associate = False

    def action_save(self):
        partner_id = self.env.context.get('active_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            phone = partner.phone
            email = partner.email
            office_address = partner.office_address
            self.env['res.partner.custom.contact'].create({
                'name_associate': self.company_id.id,
                'phone_associate': self.phone_associate,
                'email_associate': self.email_associate,
                'address_associate': self.address_associate,
                'partner_id': partner.id,
            })
            partners = self.env['res.partner'].browse(partner_id)
            self.env['res.partner.custom.contacts'].create({
                'name_associates': partners.id,
                'phone_associates': phone,
                'email_associates': email,
                'address_associates': office_address,
                'partner_ids': self.company_id.id,
            })


class ResPartnerCustomContacts(models.Model):
    _name = 'res.partner.custom.contacts'
    _description = 'Custom Contacts'

    name_associates = fields.Many2one('res.partner', string="Associate", domain="[('is_company', '=', False)]",readonly=True)
    phone_associates = fields.Char(string="Phone",readonly=True)
    email_associates = fields.Char(string="Email",readonly=True)
    address_associates = fields.Char(string="Address",readonly=True)
    partner_ids = fields.Many2one('res.partner', string="Partner",readonly=True)

    @api.model
    def create(self, vals):
        record = super(ResPartnerCustomContacts, self).create(vals)
        # record.update_associate_history_kontrak()
        partner = record.partner_ids
        partner.message_post(body=f"Created Associate: {record.name_associates.name}, Phone: {record.phone_associates}, Email: {record.email_associates}, Address: {record.address_associates}")
        return record

    def write(self, vals):
        res = super(ResPartnerCustomContacts, self).write(vals)
        for record in self:
            # record.update_associate_history_kontrak()
            partner = record.partner_ids
            partner.message_post(body=f"Updated Associate: {record.name_associates.name}, Phone: {record.phone_associates}, Email: {record.email_associates}, Address: {record.address_associates}")
        return res

    # def update_associate_history_kontrak(self):
    #     for record in self:
    #         if record.name_associates:
    #             existing_history_kontrak = self.env['tsi.history_kontrak'].search([
    #                 ('partner_id', '=', record.partner_ids.id),
    #             ], limit=1)
                
    #             if existing_history_kontrak:
    #                 existing_history_kontrak.write({
    #                     'associate': record.name_associates.id,
    #                 })
    #             else:
    #                 self.env['tsi.history_kontrak'].create({
    #                     'partner_id': record.partner_ids.id,
    #                     'associate': record.name_associates.id,
    #                 })
    
    # def unlink(self):
    #     for record in self:
    #         partner = record.partner_ids
    #         partner.message_post(body=f"Deleted Associate: {record.name_associates.name}, Phone: {record.phone_associates}, Email: {record.email_associates}, Address: {record.address_associates}")
    #         history_kontrak = self.env['tsi.history_kontrak'].search([
    #             ('partner_id', '=', record.partner_ids.id),
    #             ('associate', '=', record.name_associates.id),
    #         ])
    #         if history_kontrak:
    #             history_kontrak.unlink()
    #         if not self.env.context.get('from_contact_unlink'):
    #             corresponding_contact = self.env['res.partner.custom.contact'].search([
    #                 ('partner_id', '=', record.name_associates.id)
    #             ])
    #             if corresponding_contact:
    #                 corresponding_contact.with_context(from_contact_unlink=True).unlink()
    #     return super(ResPartnerCustomContacts, self).unlink()

class CustomContactWizards(models.TransientModel):
    _name = 'custom.contact.wizards'
    _description = 'Custom Contact Wizards'

    company_ids = fields.Many2one('res.partner', string="Associate", domain="[('is_company', '=', False)]")
    phone_associates = fields.Char(string="Phone")
    email_associates = fields.Char(string="Email")
    address_associates = fields.Char(string="Address")

    @api.onchange('company_ids')
    def _onchange_name_associates(self):
        if self.company_ids:
            self.address_associates = self.company_ids.office_address
            self.phone_associates = self.company_ids.phone
            self.email_associates = self.company_ids.email
        else:
            self.address_associates = False
            self.phone_associates = False
            self.email_associates = False

    def action_saves(self):
        partner_ids = self.env.context.get('active_id')
        if partner_ids:
            # Ambil partner yang sedang aktif
            partnerr = self.env['res.partner'].browse(partner_ids)
            phone = partnerr.phone
            email = partnerr.email
            office_address = partnerr.office_address
            
            # Update data res.partner dengan data dari wizard
            if self.company_ids:
                self.company_ids.write({
                    'phone': self.phone_associates,
                    'email': self.email_associates,
                    'office_address': self.address_associates,
                })
            
            # Buat entri baru di res.partner.custom.contacts
            self.env['res.partner.custom.contacts'].create({
                'name_associates': self.company_ids.id,
                'phone_associates': self.phone_associates,
                'email_associates': self.email_associates,
                'address_associates': self.address_associates,
                'partner_ids': partnerr.id,
            })
            
            # Buat entri baru di res.partner.custom.contact
            partners = self.env['res.partner'].browse(partner_ids)
            self.env['res.partner.custom.contact'].create({
                'name_associate': partners.id,
                'phone_associate': phone,
                'email_associate': email,
                'address_associate': office_address,
                'partner_id': self.company_ids.id,
            })