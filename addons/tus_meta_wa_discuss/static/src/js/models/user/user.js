/** @odoo-module **/

import {
    registerFieldPatchModel,registerInstancePatchModel
} from '@mail/model/model_core';
import { attr, many2many, many2one, one2many, one2one } from '@mail/model/model_field';
import { link, replace, unlink, unlinkAll } from '@mail/model/model_field_command';

import { MessageList } from '@mail/components/message_list/message_list';
import { patch } from 'web.utils';


registerFieldPatchModel('mail.user', 'mail/static/src/models/user/user.js', {
    isWhatsappUser: attr(),
     not_send_msgs_btn_in_chatter: many2many('ir.model', {
        }),
        not_wa_msgs_btn_in_chatter: many2many('ir.model', {
        })
});