# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class WhatsAppIrAction(models.Model):
    _name = "whatsapp.ir.actions"

    name = fields.Char(string="Action Name", required=True, translate=True)
    binding_model_id = fields.Many2one("ir.model", ondelete="cascade")
    chatbot_id = fields.Many2one(comodel_name="whatsapp.chatbot", string="Chatbot")
