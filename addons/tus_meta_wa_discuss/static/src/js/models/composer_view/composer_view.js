/** @odoo-module **/

import {
    registerFieldPatchModel,registerInstancePatchModel, registerClassPatchModel
} from '@mail/model/model_core';
import { addLink, escapeAndCompactTextContent, parseAndTransform } from '@mail/js/utils';
import { clear, insertAndReplace, link, replace, unlink, unlinkAll } from '@mail/model/model_field_command';
import { attr, many2many, many2one, one2many, one2one } from '@mail/model/model_field';


registerInstancePatchModel('mail.composer_view', 'mail/static/src/models/composer_view/composer_view.js', {

    async postMessage() {
        const composer = this.composer;
        if (composer.thread.model === 'mail.channel') {
            const command = this._getCommandFromText(composer.textInputContent);
            if (command) {
                await command.execute({ channel: composer.thread, body: composer.textInputContent });
                if (composer.exists()) {
                    composer._reset();
                }
                return;
            }
        }
        if (this.messaging.currentPartner) {
            composer.thread.unregisterCurrentPartnerIsTyping({ immediateNotify: true });
        }
        const escapedAndCompactContent = escapeAndCompactTextContent(composer.textInputContent);
        let body = escapedAndCompactContent.replace(/&nbsp;/g, ' ').trim();
        // This message will be received from the mail composer as html content
        // subtype but the urls will not be linkified. If the mail composer
        // takes the responsibility to linkify the urls we end up with double
        // linkification a bit everywhere. Ideally we want to keep the content
        // as text internally and only make html enrichment at display time but
        // the current design makes this quite hard to do.
        body = this._generateMentionsLinks(body);
        body = parseAndTransform(body, addLink);
        body = this._generateEmojisOnHtml(body);

        let postData;
        if(composer.thread.isWaMsgs){
            postData = {
                attachment_ids: composer.attachments.map(attachment => attachment.id),
                body,
                message_type: 'wa_msgs',
                partner_ids: composer.recipients.map(partner => partner.id),
            };
        }
        else{
            postData = {
                attachment_ids: composer.attachments.map(attachment => attachment.id),
                body,
                message_type: 'comment',
                partner_ids: composer.recipients.map(partner => partner.id),
            };
        }
        const params = {
            'post_data': postData,
            'thread_id': composer.thread.id,
            'thread_model': composer.thread.model,
        };
        try {
            composer.update({ isPostingMessage: true });
            if (composer.thread.model === 'mail.channel') {
                Object.assign(postData, {
                    subtype_xmlid: 'mail.mt_comment',
                });
            } else {
                Object.assign(postData, {
                    subtype_xmlid: composer.isLog ? 'mail.mt_note' : 'mail.mt_comment',
                });
                if (!composer.isLog) {
                    params.context = { mail_post_autofollow: true };
                }
            }
            if (this.threadView && this.threadView.replyingToMessageView && this.threadView.thread !== this.messaging.inbox) {
                postData.parent_id = this.threadView.replyingToMessageView.message.id;
            }
            const { threadView = {} } = this;
            const { thread: chatterThread } = this.chatter || {};
            const { thread: threadViewThread } = threadView;
            const messageData = await this.env.services.rpc({ route: `/mail/message/post`, params });
            if (!this.messaging) {
                return;
            }
            const message = this.messaging.models['mail.message'].insert(
                this.messaging.models['mail.message'].convertData(messageData)
            );
            for (const threadView of message.originThread.threadViews) {
                // Reset auto scroll to be able to see the newly posted message.
                threadView.update({ hasAutoScrollOnMessageReceived: true });
            }
            if (chatterThread) {
                if (this.exists()) {
                    this.delete();
                }
                if (chatterThread.exists()) {
                    chatterThread.refreshFollowers();
                    chatterThread.fetchAndUpdateSuggestedRecipients();
                }
            }
            if (threadViewThread) {
                if (threadViewThread === this.messaging.inbox) {
                    if (this.exists()) {
                        this.delete();
                    }
                    this.env.services['notification'].notify({
                        message: _.str.sprintf(this.env._t(`Message posted on "%s"`), message.originThread.displayName),
                        type: 'info',
                    });
                }
                if (threadView && threadView.exists()) {
                    threadView.update({ replyingToMessageView: clear() });
                }
            }
            if (composer.exists()) {
                composer._reset();
            }
        } finally {
            if (composer.exists()) {
                composer.update({ isPostingMessage: false });
            }
        }
    },

    async openFullComposer() {
            var action;
            if(this.composer.composerViews && this.composer.composerViews[0].chatter && this.composer.composerViews[0].chatter.isWaComposerView){
                const attachmentIds = this.composer.attachments.map(attachment => attachment.id);
                const context = {
                    default_attachment_ids: attachmentIds,
                    default_model: this.composer.activeThread.model,
                    default_partner_ids: this.composer.recipients.map(partner => partner.id),
                    default_res_id: this.composer.activeThread.id,
                };
                action = {
                    type: 'ir.actions.act_window',
                    res_model: 'wa.compose.message',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: context,
                };
            }
            else{
                const attachmentIds = this.composer.attachments.map(attachment => attachment.id);
                const context = {
                    default_attachment_ids: attachmentIds,
                    default_body: escapeAndCompactTextContent(this.composer.textInputContent),
                    default_is_log: this.composer.isLog,
                    default_model: this.composer.activeThread.model,
                    default_partner_ids: this.composer.recipients.map(partner => partner.id),
                    default_res_id: this.composer.activeThread.id,
                    mail_post_autofollow: true,
                };

                action = {
                    type: 'ir.actions.act_window',
                    res_model: 'mail.compose.message',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: context,
                };
            }
            const composer = this.composer;
            const options = {
                on_close: () => {
                    if (!composer.exists()) {
                        return;
                    }
                    composer._reset();
                    if (composer.activeThread) {
                        composer.activeThread.loadNewMessages();
                    }
                },
            };
            await this.env.bus.trigger('do-action', { action, options });
        }

});

/**
 * Here, add custom placeholder for both send message and whatsapp message button at sidebar
 */

//var ComposerTextInput = require('mail/static/src/components/composer_text_input/composer_text_input');
//
//    ComposerTextInput.Textarea.include({
//        // override the existing textareaPlaceholder method
//        get textareaPlaceholder() {
//            console.log("mail.composer_text_input calleddddddddddddddddddddddddddddddd",this);
//            if (!this.composerView) {
//                return "";
//            }
//            if (!this.composerView.composer.thread) {
//                return "";
//            }
//            if (this.composerView.composer.thread.model === 'mail.channel') {
//                if (this.composerView.composer.thread.correspondent) {
//                    return _.str.sprintf(this.env._t("Message %s..."), this.composerView.composer.thread.correspondent.nameOrDisplayName);
//                }
//                return _.str.sprintf(this.env._t("Message #%s..."), this.composerView.composer.thread.displayName);
//            }
//            if (this.composerView.composer.isLog) {
//                return this.env._t("Log an internal note...");
//            }
//            if (this.composerView.composer.thread.isWaMsgs) {
//                return this.env._t("Send a WhatsApp Message...");
//            }
//            return this.env._t("Send a message to followers...");
//        }
//    });
//
//registerClassPatchModel('mail.composer_text_input', 'tus_meta_wa_discuss/static/src/js/models/composer_view/composer_view.js', {
//
//    get textareaPlaceholder() {
//        console.log("mail.composer_text_input calleddddddddddddddddddddddddddddddd",this);
//        if (!this.composerView) {
//            return "";
//        }
//        if (!this.composerView.composer.thread) {
//            return "";
//        }
//        if (this.composerView.composer.thread.model === 'mail.channel') {
//            if (this.composerView.composer.thread.correspondent) {
//                return _.str.sprintf(this.env._t("Message %s..."), this.composerView.composer.thread.correspondent.nameOrDisplayName);
//            }
//            return _.str.sprintf(this.env._t("Message #%s..."), this.composerView.composer.thread.displayName);
//        }
//        if (this.composerView.composer.isLog) {
//            return this.env._t("Log an internal note...");
//        }
//        if (this.composerView.composer.thread.isWaMsgs) {
//            return this.env._t("Send a WhatsApp Message...");
//        }
//        return this.env._t("Send a message to followers...");
//    }
//
//});