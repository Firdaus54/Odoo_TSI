from odoo import _, api, fields, models, modules, tools
import json

class Channel(models.Model):

    _inherit = 'mail.channel'

    @api.model
    def channel_get(self, partners_to, pin=True):
        """ Get the canonical private channel between some partners, create it if needed.
            To reuse an old channel (conversation), this one must be private, and contains
            only the given partners.
            :param partners_to : list of res.partner ids to add to the conversation
            :param pin : True if getting the channel should pin it for the current user
            :returns: channel_info of the created or existing channel
            :rtype: dict
        """
        # Multi Companies and Multi Providers Code Here
        # provider_id = self.env.user.provider_ids.filtered(
        #     lambda x: x.company_id == self.env.company and x.chat_api_authenticated)

        partner_info = False
        if self.env.user.partner_id.id not in partners_to:
            partner_info = self.env['res.partner'].sudo().search([('id', 'in', partners_to)])
            partners_to.append(self.env.user.partner_id.id)
        # determine type according to the number of partner in the channel
        else:
            partner_info = self.env['res.partner'].sudo().search([('id', 'in', partners_to)])
        self.flush()
        provider_channel_id = partner_info.channel_provider_line_ids.filtered(lambda s: s.provider_id == self.env.user.provider_id)
        if provider_channel_id:
            # get the existing channel between the given partners
            channel = self.browse(provider_channel_id.channel_id.id)
            # pin up the channel for the current partner
            if pin:
                self.env['mail.channel.partner'].search(
                    [('partner_id', '=', self.env.user.partner_id.id), ('channel_id', '=', channel.id)]).write(
                    {'is_pinned': True})
            channel._broadcast(self.env.user.partner_id.ids)
        else:
            # create a new one
            channel = self.create({
                'channel_partner_ids': [(4, partner_id) for partner_id in partners_to],
                'public': 'private',
                'channel_type': 'chat',
                # 'email_send': False,
                'name': ', '.join(self.env['res.partner'].sudo().browse(partners_to).mapped('name')),
            })
            have_user = self.env['res.users'].search([('partner_id','in',partner_info.ids)])
            if not have_user:
                channel.whatsapp_channel = True
            if partner_info:
                # partner_info.channel_id = channel.id
                partner_info.write({'channel_provider_line_ids': [
                    (0, 0, {'channel_id': channel.id, 'provider_id': self.env.user.provider_id.id})]})
            mail_channel_partner = self.env['mail.channel.partner'].sudo().search(
                [('channel_id', '=', channel.id), ('partner_id', '=', self.env.user.partner_id.id)])
            mail_channel_partner.write({'is_pinned': True})
            channel._broadcast(partners_to)
        return channel.channel_info()[0]

    def get_channel_agent(self, channel_id):
        if self.env.user:
            # Multi Companies and Multi Providers Code Here
            # provider_id = self.env.user.provider_ids.filtered(
            #     lambda x: x.company_id == self.env.company and x.chat_api_authenticated)

            channel = self.env['mail.channel'].sudo().browse(int(channel_id))
            partner_lst = channel.channel_partner_ids.ids
            channel_users = self.env['res.users'].sudo().search_read([('partner_id.id', 'in', partner_lst)],
                                                                     ['id', 'name'])
            users = self.env['res.users'].sudo().search([('partner_id.id', 'not in', partner_lst)])
            users_lst = []
            for user in users:
                # Multi Companies and Multi Providers Code Here
                # if user.has_group('tus_meta_whatsapp_base.whatsapp_group_user') and provider_id and provider_id.id in self.env.user.provider_ids.ids:
                if user.has_group('tus_meta_whatsapp_base.whatsapp_group_user') and user.provider_id and user.provider_id == self.env.user.provider_id:
                    users_lst.append({'name': user.name, 'id': user.id})
            dict = {'channel_users': channel_users, 'users': users_lst}
            return dict

    def add_agent(self, user_id, channel_id):
        user = self.env['res.users'].sudo().browse(int(user_id))
        channel = self.env['mail.channel'].sudo().browse(int(channel_id))
        if channel.whatsapp_channel:
            channel.write({'channel_partner_ids': [(4, user.partner_id.id)]})
            mail_channel_partner = self.env['mail.channel.partner'].sudo().search(
                [('channel_id', '=', channel_id),
                 ('partner_id', '=', user.partner_id.id)])
            mail_channel_partner.write({'is_pinned': True})
            return True

    def remove_agent(self, user_id, channel_id):
        user = self.env['res.users'].sudo().browse(int(user_id))
        channel = self.env['mail.channel'].sudo().browse(int(channel_id))
        if channel.whatsapp_channel:
            channel.write({'channel_partner_ids': [(3, user.partner_id.id)]})
            return True

    @api.constrains('channel_last_seen_partner_ids', 'channel_partner_ids')
    def _constraint_partners_chat(self):
        pass

    def _set_last_seen_message(self, last_message):
        """
        When Message Seen/Read in odoo, Double Blue Tick (Read Receipts) in WhatsApp
        """
        res = super(Channel, self)._set_last_seen_message(last_message)
        last_message.write({'isWaMsgsRead': True})
        if last_message.isWaMsgsRead == True:
            channel_company_line_id = self.env['channel.provider.line'].search(
                [('channel_id', '=', last_message.res_id)])
            if channel_company_line_id.provider_id:
                provider_id = channel_company_line_id.provider_id
                if provider_id:
                    answer = provider_id.graph_api_wamsg_mark_as_read(last_message.wa_message_id)
                    if answer.status_code == 200:
                        dict = json.loads(answer.text)
                        if provider_id.provider == 'graph_api':  # if condition for Graph API
                            if 'success' in dict and dict.get('success'):
                                last_message.write({'isWaMsgsRead': True})
        return res        
