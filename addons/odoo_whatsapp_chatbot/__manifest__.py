# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Odoo Whatsapp Chatbot Integration",
    "version": "15.0.0.1",
    "author": "TechUltra Solutions",
    "category": "Discuss",
    "live_test_url": "https://www.youtube.com/playlist?list=PL8o8i9mlxsWivZfvRKeNHP_sXrgvEYD59",
    "website": "www.techultrasolutions.com",
    "summary": "Odoo Whatsapp Chatbot Integration, Interactive Templates, Buttons send through odoo on WhatsApp and Message Automation",
    "description": """
        Odoo Whatsapp Chatbot Integration,
        Interactive Templates,
        Buttons send through odoo on WhatsApp and Message Automation
        Odoo Chatbot
        Chatbot
        Odoo
        ERP
        Odoo ERP
        WhatsApp
        Whats-App
        Discuss
        App
        Enterprise
        Odoo Whatsapp Chatbot
        Whatsapp Chatbot
    """,
    "depends": ["tus_meta_whatsapp_base", "tus_meta_wa_discuss"],
    "data": [
        "security/ir.model.access.csv",
        "data/wa_template.xml",
        "data/whatsapp_chatbot.xml",
        "views/whatsapp_chatbot_script_views.xml",
        "views/mail_channel_views.xml",
        "views/whatsapp_chatbot_views.xml",
        "views/whatsapp_ir_action_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/odoo_whatsapp_chatbot/static/src/scss/kanban_view.scss"
        ],
    },
    "images": ["static/description/banner.gif"],
    "price": 145,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
}
