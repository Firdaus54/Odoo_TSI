/** @odoo-module **/

import {
    registerFieldPatchModel,registerInstancePatchModel, registerClassPatchModel
} from '@mail/model/model_core';
import { insert, link, unlinkAll,insertAndReplace } from '@mail/model/model_field_command';

registerClassPatchModel('mail.partner', 'mail/static/src/models/partner/partner.js', {
    convertData(data) {
        const data2 = this._super(data);

        // relation
        if ('user_id' in data) {
            if (!data.user_id) {
                data2.user = unlinkAll();
            } else {
                let user = {};
                if (Array.isArray(data.user_id)) {
                    user = {
                        id: data.user_id[0],
                        display_name: data.user_id[1],
                    };
                } else {
                    user = {
                        id: data.user_id,
                    };
                }
                user.isInternalUser = data.is_internal_user;
                user.isWhatsappUser = data.is_whatsapp_user;
                user.not_send_msgs_btn_in_chatter = insertAndReplace(data.not_send_msgs_btn_in_chatter.map(attachmentData =>
                        this.messaging.models['ir.model'].convertData(attachmentData)
                    ));
                user.not_wa_msgs_btn_in_chatter = insertAndReplace(data.not_wa_msgs_btn_in_chatter.map(attachmentData =>
                        this.messaging.models['ir.model'].convertData(attachmentData)
                    ));
                data2.user = insert(user);
            }
        }

        return data2;
    }
});


registerInstancePatchModel('mail.partner', 'mail/static/src/models/partner/partner.js', {
    async getChat() {
        if (!this.user && !this.hasCheckedUser) {
            await this.async(() => this.checkIsUser());
        }
        // prevent chatting with non-users
        if (!this.user) {
                let chat = this.messaging.models['mail.thread'].find(thread =>
                thread.channel_type === 'chat' &&
                thread.correspondent === this &&
                thread.model === 'mail.channel' &&
                thread.public === 'private'
            );
            if (!chat || !chat.isPinned) {
                // if chat is not pinned then it has to be pinned client-side
                // and server-side, which is a side effect of following rpc
                chat = await this.async(() =>
                    this.messaging.models['mail.thread'].performRpcCreateChat({
                        partnerIds: [this.id],
                    })
                );
            }
            if (!chat) {
                this.env.services['notification'].notify({
                    message: this.env._t("An unexpected error occurred during the creation of the chat."),
                    type: 'warning',
                });
                return;
            }
            return chat;
        }
        return this.user.getChat();
    }
});