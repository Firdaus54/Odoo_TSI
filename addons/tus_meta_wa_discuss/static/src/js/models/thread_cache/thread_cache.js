/** @odoo-module **/

import {
    registerFieldPatchModel,registerInstancePatchModel
} from '@mail/model/model_core';
import { attr, many2many, many2one, one2many, one2one } from '@mail/model/model_field';
import { link, replace, unlink, unlinkAll } from '@mail/model/model_field_command';

import { MessageList } from '@mail/components/message_list/message_list';
import { patch } from 'web.utils';

registerInstancePatchModel('mail.thread_cache', 'mail/static/src/models/thread_cache/thread_cache.js', {
    _computeOrderedNonEmptyMessages() {
        if(this.thread.isWaMsgs && !this.thread.isChatterWa){
            return replace(this.orderedMessages.filter(message => !message.isEmpty && message.message_type=='wa_msgs'));
        }
        else{
            return replace(this.orderedMessages.filter(message => !message.isEmpty && message.message_type!='wa_msgs'));
        }
    }
});