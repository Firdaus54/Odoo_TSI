/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;
const { useRef } = owl.hooks;

export class ThreadViewNav extends Component {
    setup() {
        super.setup();
    }
    mounted(){
        super.mounted()
        if(this.threadViewNav &&  this.threadViewNav.thread && this.threadViewNav.thread.correspondent && this.threadViewNav.thread.correspondent.user){
            if(this.threadViewNav.thread.isWaMsgs){
                this.onClickWhatsapp()
            }
            else{
                this.onClickLive()
            }
        }
        else{
            this.onClickWhatsapp();
        }
    }
    render(){
        super.render()
        if(this.threadViewNav &&  this.threadViewNav.thread && this.threadViewNav.thread.correspondent && this.threadViewNav.thread.correspondent.user){
            if(this.threadViewNav.thread.isWaMsgs){
                this.onClickWhatsapp()
            }
            else{
                this.onClickLive()
            }
        }
        else{
            this.onClickWhatsapp();
        }
        if(this.messaging && this.messaging.wa_thread_view){
            this.messaging.wa_thread_view.tabPartner();
        }
        function test(){
            var tabsNewAnim = $('#navbarSupportedContent');
            var selectorNewAnim = $('#navbarSupportedContent').find('li').length;
            var activeItemNewAnim = tabsNewAnim.find('.active');
            var activeWidthNewAnimHeight = activeItemNewAnim.innerHeight();
            var activeWidthNewAnimWidth = activeItemNewAnim.innerWidth() ;
            var itemPosNewAnimTop = activeItemNewAnim.position();
            var itemPosNewAnimLeft = activeItemNewAnim.position();
            if(itemPosNewAnimTop){
                  $(".hori-selector").css({
                    "top":itemPosNewAnimTop.top + "px",
                    "left":itemPosNewAnimLeft.left + "px",
                    "height": activeWidthNewAnimHeight + "px",
                    "width": activeWidthNewAnimWidth + "px"
                  });
            }

              $("#navbarSupportedContent").on("click","li",function(e){
                $('#navbarSupportedContent ul li').removeClass("active");
                $(this).addClass('active');
                var activeWidthNewAnimHeight = $(this).innerHeight();
                var activeWidthNewAnimWidth = $(this).innerWidth();
                var itemPosNewAnimTop = $(this).position();
                var itemPosNewAnimLeft = $(this).position();
                $(".hori-selector").css({
                  "top":itemPosNewAnimTop.top + "px",
                  "left":itemPosNewAnimLeft.left + "px",
                  "height": activeWidthNewAnimHeight + "px",
                  "width": activeWidthNewAnimWidth + "px"
                });
              });
        }
        $(document).ready(function(){
          setTimeout(function(){ test(); });
        });

        $(window).on('resize', function(){
          setTimeout(function(){ test(); }, 500);
        });
        $(".navbar-toggler").click(function(){
          setTimeout(function(){ test(); });
        });
    }
    get threadViewNav() {
        return this.messaging && this.messaging.models['mail.thread_view_topbar'].get(this.props.localId);
    }

    onClickLive(){
        if(this.threadViewNav &&  this.threadViewNav.thread){
            this.threadViewNav.thread.update({isWaMsgs:false})
            this.threadViewNav.thread.refresh();
            $('#navbarSupportedContent').click();
        }
    }
    onClickWhatsapp(){
        if(this.threadViewNav &&  this.threadViewNav.thread){
            this.threadViewNav.thread.update({isWaMsgs:true})
            this.threadViewNav.thread.refresh()
            $('#navbarSupportedContent').click();
        }
    }

}

Object.assign(ThreadViewNav, {
    props: {
        localId: String,
    },
    template: 'tus_meta_whatsapp_base.ThreadViewNav',
});

registerMessagingComponent(ThreadViewNav);
