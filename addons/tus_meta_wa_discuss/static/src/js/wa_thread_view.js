/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;
const { useRef } = owl.hooks;
import Dialog from 'web.Dialog';
import OwlDialog from 'web.OwlDialog';
import core from 'web.core';
import { AgentsList } from './AgentsList.js';
import { MessagesList } from './MessagesList.js';
const { ComponentWrapper, WidgetAdapterMixin } = require('web.OwlCompatibility');


export class WaThreadView extends Component {
    setup() {
        super.setup();
        this.messaging.wa_thread_view = this
        this.state = owl.hooks.useState({
             nav_active:'partner'
        })
    }


    mounted(){
        super.mounted();
         if(this.state.nav_active == 'partner'){
            this.tabPartner();
        }
    }

    get threadView() {
        return this.messaging && this.messaging.models['mail.thread_view'].get(this.props.threadViewLocalId);
    }

    render(){
        super.render();
        if(this.state.nav_active == 'partner'){
            this.tabPartner();
        }
    }

    onClickBack(){
        if(this.state.nav_active == 'partner'){
            this.tabPartner();
        }
    }

    tabPartner(){
        var self= this
        this.state.nav_active = 'partner'
        if(self.threadView && self.threadView.thread && self.threadView.thread.correspondent){
            if(self.threadView.thread.correspondent){
                var partner = self.env.bus.trigger('do-action', {action: {
                        context: {create: false},
                        name: 'Partner',
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.threadView.thread.correspondent.id,
                        views: [[false, 'form']],
                        target: 'new',
                        flags: {mode: 'edit'},
                            main_form: true,
                    }, options: {main_form: true,}
                });
            }
        }
        $('.main-button').removeClass('o_hidden');
        $('.back_btn').addClass('o_hidden');
    }

    tab_agent(){
        $('.main-button').addClass('o_hidden');
        $('#main-form-view').replaceWith("<div id='main-form-view'></div>")
        const AgentsListComponent=new ComponentWrapper(this, AgentsList);
        AgentsListComponent.mount($('#main-form-view')[0]);
    }

    tab_message_templates(){
        var self= this
        this.state.nav_active = 'message_templates'
        $('.main-button').addClass('o_hidden');
        $('#main-form-view').replaceWith("<div id='main-form-view'></div>")
        const MessageWaListComponent = new ComponentWrapper(this, MessagesList);
        MessageWaListComponent.mount($('#main-form-view')[0]);
    }

}

Object.assign(WaThreadView, {
    props: {
        threadViewLocalId: String,
    },
    template: 'tus_meta_wa_discuss.WaThreadView',
});

registerMessagingComponent(WaThreadView);
