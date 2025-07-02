from odoo import models, fields, api

class ContactFranchise(models.Model):
    _inherit = 'res.partner'
    
    contact_franchise_ids = fields.One2many('res.partner.contact.franchise', 'partner_id', string="Contacts Franchise")
    
    contact_client   = fields.Boolean(string='Franchise',default=True)  
    
    hide_contact_franchisess = fields.Boolean(compute='_compute_hide_contact_franchisess', store=True)
    @api.depends('is_company', 'contact_client')
    def _compute_hide_contact_franchisess(self):
        for record in self:
            record.hide_contact_franchisess = record.is_company and record.contact_client
   
    hide_contact_fr = fields.Boolean(compute='_compute_hide_contact_fr', store=True)
    @api.depends('is_company', 'contact_client')
    def _compute_hide_contact_fr(self):
        for record in self:
            record.hide_contact_fr = record.is_company and not record.contact_client
    
    def open_contact_franchise_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact Franchise Wizard',
            'res_model': 'contact.franchise.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }
    
class ResPartnerContactFranchise(models.Model):
    _name        = 'res.partner.contact.franchise'
    _description = 'Contact Franchise'

    partner_id  = fields.Many2one('res.partner', string="Partner",readonly=True)
    name_franchise        = fields.Many2one('res.partner', string="Company", domain="[('is_company', '=', True)]",readonly=True)
    address_franchise     = fields.Char(string="Address",readonly=True)
    phone_franchise       = fields.Char(string="Phone",readonly=True)
    email_franchise       = fields.Char(string="Email",readonly=True)

    def unlink(self):
        for record in self:
            if not self.env.context.get('from_contact_unlink'):
                corresponding_contact = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.name_franchise.id)
                ])
                if corresponding_contact:
                    corresponding_contact.with_context(from_contact_unlink=True).unlink()
                corresponding_contacts = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.partner_id.id)
                ])
                if corresponding_contacts:
                    corresponding_contacts.with_context(from_contact_unlink=True).unlink()
        return super(ResPartnerContactFranchise, self).unlink()
    
    
    
class ContactFranchiseWizard(models.TransientModel):
    _name = 'contact.franchise.wizard'
    _description = 'Contact Franchise Wizard'

    company_id = fields.Many2one('res.partner', string="Company", domain="[('is_company', '=', True)]")
    phone_franchise = fields.Char(string="Phone")
    email_franchise = fields.Char(string="Email")
    address_franchise = fields.Char(string="Address")

    @api.onchange('company_id')
    def _onchange_name_franchise(self):
        if self.company_id:
            self.address_franchise = self.company_id.office_address
            self.phone_franchise = self.company_id.phone
            self.email_franchise = self.company_id.email
        else:
            self.address_franchise = False
            self.phone_franchise = False
            self.email_franchise = False

    def action_save_franchise(self):
        partner_id = self.env.context.get('active_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            self.env['res.partner.contact.franchise'].create({
                'name_franchise': self.company_id.id,
                'phone_franchise': self.phone_franchise,
                'email_franchise': self.email_franchise,
                'address_franchise': self.address_franchise,
                'partner_id': partner.id,
            })
            self.company_id.write({'contact_client': False})
        
        partner_ids = self.env.context.get('default_partner_id')
        if partner_ids:
            partners = self.env['res.partner'].browse(partner_ids)
            self.env['res.partner.contact.franchise'].create({
                'name_franchise': partner_ids,
                'partner_id': self.company_id.id,
                'phone_franchise': self.phone_franchise,
                'email_franchise': self.email_franchise,
                'address_franchise': self.address_franchise,
            })
            partners.write({'contact_client': True})
    
