/** @odoo-module **/

import { ActionDialog } from "@web/webclient/actions/action_dialog";
import { patch } from 'web.utils';
import { useEffect } from "@web/core/utils/hooks";

const LEGACY_SIZE_CLASSES = {
    "extra-large": "modal-xl",
    large: "modal-lg",
    small: "modal-sm",
};

patch(ActionDialog.prototype, 'tus_meta_wa_discuss/static/src/js/action_dialog.js', {
    setup() {
        this._super();
        if(this.props.actionProps.action.main_form || $('#main-form-view').length > 0){
        useEffect(
            () => {
                    // Retrieve the widget climbing the wrappers
                    const componentController = this.actionRef.comp;
                    const controller = componentController.componentRef.comp;
                    const viewAdapter = controller.controllerRef.comp;
                    const widget = viewAdapter.widget;
                    // Render legacy footer buttons
                    const footer = this.modalRef.el.querySelector("footer");
                    if(this.props.actionProps.action.main_form || $('#main-form-view').length){
                        widget.renderButtons($('.modal-footer'));
                    }
            },
            () => []
        ); // TODO: should this depend on actionRef.comp?
        }
    },
    mounted(){
        if(this.props.actionProps.action.main_form || $('#main-form-view').length > 0){
            if(typeof(this.props.actionProps.action.main_form) == 'undefined' ){
                $('.back_btn').removeClass('o_hidden')
            }
            $('#main-form-view').html($(this.el).find('.modal-body'));
            $('#main-buttons-view').html($(this.el).find('.modal-footer'));
            $(document.body).find('.o_dialog_container').remove();
            $(document.body).find('.o_effects_manager').after('<div class="o_dialog_container"></div>');
        }
    }
});
