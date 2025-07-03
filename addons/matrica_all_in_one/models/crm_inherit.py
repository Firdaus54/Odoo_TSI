from odoo import models, fields

class SegmentProduct(models.Model):
    _name = 'segment.product'
    _description = 'Segment Product'

    name = fields.Char('Product Segment', required=True)


class CrmLeadTask(models.Model):
    _name = 'crm.lead.task'
    _description = 'Task Progress CRM'

    lead_id = fields.Many2one('crm.lead', string='Pipeline')
    task = fields.Char(string='Task', required=True)
    deadline = fields.Date(string='Deadline')
    status = fields.Selection([
        ('todo', 'To Do'),
        ('progress', 'Progress'),
        ('done', 'Done')
    ], string='Status', default='todo')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    pelanggan_baru = fields.Boolean(string='Pelanggan Baru?')
    segment_pelanggan = fields.Selection([
        ('kontruksi', 'Kontruksi'),
        ('perbankan', 'Perbankan'),
        ('pemerintah', 'Pemerintah'),
        ('bumn', 'BUMD/BUMN'),
        ('kementrian', 'Kementrian'),
        ('swasta', 'Swasta Lainnya'),
    ], string='Segment Pelanggan')
    segment_product_id = fields.Many2one('segment.product', string='Segment Product')
    task_ids = fields.One2many('crm.lead.task', 'lead_id', string='Task Progress')