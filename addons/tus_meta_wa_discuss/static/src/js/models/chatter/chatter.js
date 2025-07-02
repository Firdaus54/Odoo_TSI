/** @odoo-module **/

import {
    registerFieldPatchModel,registerInstancePatchModel
} from '@mail/model/model_core';
import { addLink, escapeAndCompactTextContent, parseAndTransform } from '@mail/js/utils';
import { clear, insertAndReplace, link, replace, unlink, unlinkAll } from '@mail/model/model_field_command';
import { attr, many2many, many2one, one2many, one2one } from '@mail/model/model_field';

registerFieldPatchModel('mail.chatter', 'mail/static/src/models/chatter/chatter.js', {
    isWaComposerView: attr({
        default: false,
    }),
    isShowSendMessage: attr({
       compute: '_computeshowSendMessage',
    }),
    isShowWaSendMessage: attr({
        compute: '_computeshowWaSendMessage',
    }),
});

registerInstancePatchModel('mail.chatter', 'mail/static/src/models/chatter/chatter.js', {
    _created() {
        this._super()
        this.onClickWaSendMessage = this.onClickWaSendMessage.bind(this);
    },
    onClickWaSendMessage(ev){
        if (this.composerView && !this.composerView.composer.isLog) {
            this.update({ composerView: clear() });
            this.thread.update({isWaMsgs:false})
            this.thread.update({isChatterWa:false})
        } else {
            this.showWaSendMessage();
        }
    },
    onClickSendMessage(ev) {
        this._super(ev)
        this.thread.update({isWaMsgs:false})
        this.thread.update({isChatterWa:false})
    },
    showWaSendMessage() {
        this.update({ composerView: insertAndReplace(), isWaComposerView:true});
        this.composerView.composer.update({ isLog: false });
        this.thread.update({isWaMsgs:true})
        this.thread.update({isChatterWa:true})
        this.focus();
    },
    showSendMessage() {
        this.update({ composerView: insertAndReplace(),isWaComposerView:false });
        this.composerView.composer.update({ isLog: false });
        this.thread.update({isWaMsgs:false})
        this.thread.update({isChatterWa:false})
        this.focus();
    },
    showLogNote() {
        this.update({ composerView: insertAndReplace() ,isWaComposerView:false});
        this.composerView.composer.update({ isLog: true });
        this.thread.update({isWaMsgs:false})
        this.thread.update({isChatterWa:false})
        this.focus();
    },
    _computeshowWaSendMessage(){
        if(this.messaging && this.messaging.currentUser && this.messaging.currentUser.not_wa_msgs_btn_in_chatter){
            var lst = this.messaging.currentUser.not_wa_msgs_btn_in_chatter.filter(r => r.model == this.threadModel)
            if(lst.length > 0){
                return false
            }
        }
        return true
    },
    _computeshowSendMessage(){
         if(this.messaging && this.messaging.currentUser && this.messaging.currentUser.not_send_msgs_btn_in_chatter){
            var lst = this.messaging.currentUser.not_send_msgs_btn_in_chatter.filter(r => r.model == this.threadModel)
            if(lst.length > 0){
                return false
            }
        }
        return true
    },

});