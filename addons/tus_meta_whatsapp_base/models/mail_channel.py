from odoo import fields, models


class Channel(models.Model):

    _inherit = "mail.channel"

    whatsapp_channel = fields.Boolean(string="Whatsapp Channel")
