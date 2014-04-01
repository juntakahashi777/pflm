import requests, json, urllib

mandrill_url = "https://mandrillapp.com/api/1.0/messages/send.json"

params = {
    "key": "CP0ZcMEThOjYt4UwbVkE1w",
    "message": {
        "html": "<p>Example <b>HTML</b> content</p>",
        "text": "Example text content",
        "subject": "testing out mandrill",
        "from_email": "match@passesforlatemeal.com",
        "from_name": "PFLM Match",
        "to": [
            {
                "email": "madhavan@princeton.edu",
                "name": "Nihar",
                "type": "to"
            },
            {
                "email": "jtaskahas@princeton.edu",
                "name": "j",
                "type": "to"
            },
            {
                "email": "usikder@princeton.edu",
                "name": "u",
                "type": "to"
            }
        ],
        "headers": {
            "Reply-To": "message.reply@example.com"
        },
        "important": False,
        "track_opens": True,
        "track_clicks": True,
        "auto_text": False,
        "auto_html": False,
        "inline_css": False,
        "url_strip_qs": False,
        "preserve_recipients": True,
        "view_content_link": False,
        "bcc_address": "message.bcc_address@example.com",
        "tracking_domain": False,
        "signing_domain": False,
        "return_path_domain": False,
        "merge": True,
    },
    "async": False,
    "ip_pool": "Main Pool",
}

data = json.dumps(params)
r = requests.post(mandrill_url, data)