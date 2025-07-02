/** @odoo-module **/

import {
    registerFieldPatchModel,registerInstancePatchModel, registerClassPatchModel
} from '@mail/model/model_core';
import { attr, many2many, many2one, one2many, one2one } from '@mail/model/model_field';
import { link, replace, unlink, unlinkAll } from '@mail/model/model_field_command';

import { MessageList } from '@mail/components/message_list/message_list';
import { patch } from 'web.utils';


registerFieldPatchModel('mail.thread', 'mail/static/src/models/thread/thread.js', {
    isWaMsgs: attr({
        default: false,
    }),
    isChatterWa: attr({
        default: false,
    }),
});

registerInstancePatchModel('mail.thread', 'mail/static/src/models/thread/thread.js', {
    _computeCorrespondent() {
        if (this.channel_type === 'channel') {
            return unlink();
        }
        var correspondents = this.members.filter(partner =>
            partner !== this.messaging.currentPartner
        );
        var partner = correspondents.filter(r => typeof(r.user) == "undefined")
        if (correspondents.length > 0) {
            // 2 members chat
            if(partner.length > 0){
                return link(partner[0]);
            }
            return link(correspondents[0]);
        }
        if (this.members.length === 1) {
            // chat with oneself
            return link(this.members[0]);
        }
        return unlink();
    }
});

/**
 * Error Message showing in Chat isInChatWindow and isInDiscuss
*/
registerClassPatchModel('mail.message', 'mail/static/src/models/message/message.js', {
    /**
     * @override
     */
    convertData(data) {
        const data2 = this._super(data);

        if ('wa_delivery_status' in data) {
            data2.wa_delivery_status = data.wa_delivery_status;
        }
        if ('wa_error_message' in data) {
            data2.wa_error_message = data.wa_error_message;
        }
        if ('wp_status' in data) {
            data2.wp_status = data.wp_status;
        }
//        console.log("registerClassPatchModel*********convertData*********Message*****", data2);
        return data2;
    },
});

registerFieldPatchModel('mail.message', 'mail/static/src/models/message/message.js', {
    /**
     * Add new custom fields in message.js
     */
        wa_delivery_status: attr({
            default: false,
        }),
        wa_error_message: attr({
            default: false,
        }),
        wp_status: attr({
            default: false,
        }),
});