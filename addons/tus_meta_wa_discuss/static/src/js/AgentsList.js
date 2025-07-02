/** @odoo-module **/

const { Component, tags, hooks} = owl;
const { useState } = hooks;
const rpc = require('web.rpc');

export class AgentsList extends Component{
     counter1 = useState({ value: 0 ,});

    constructor(WaThreadView) {
        super(...arguments);
        var self=this;
        this.WaThreadView = WaThreadView

        self.users = []
        self.agents = []
        rpc.query({
                model: 'mail.channel',
                method: 'get_channel_agent',
                args: [[],self.WaThreadView.parentWidget.threadView.thread.id],
            }).then(function (result) {
                $('#main-button').addClass('o_hidden');

                self.users = result['users']
                self.agents = result['channel_users']
                self.counter1.value++;
            });
    }
    _addAgent(){
        var self = this;
        var user_id = $("#user").val()

        rpc.query({
                model: 'mail.channel',
                method: 'add_agent',
                args: [[],user_id,self.WaThreadView.parentWidget.threadView.thread.id],
            }).then(function (result) {
                if(result){
                    self.WaThreadView.parentWidget.tab_agent()
                }
            });
    }

     _removeAgent(){
        var self = this
        var user_id = parseInt(event.currentTarget.dataset.id)

        rpc.query({
                model: 'mail.channel',
                method: 'remove_agent',
                args: [[],user_id,self.WaThreadView.parentWidget.threadView.thread.id],
            }).then(function (result) {
                if(result){
                    self.WaThreadView.parentWidget.tab_agent()
                }
            });
     }
}