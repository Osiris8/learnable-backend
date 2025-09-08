from flask import Blueprint, request, jsonify
from pypdf import PdfReader


upload_bp = Blueprint("upload", __name__)

# --- Upload PDF et indexation ---
@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier trouvé"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nom de fichier vide"}), 400

    try:
        # 1. Lire le PDF
        reader = PdfReader(file)
        texts = [p.extract_text().strip() for p in reader.pages if p.extract_text()]

        # 2. Concaténer le texte extrait
        extracted_text = "\n".join(texts)

        # 3. Retourner le texte extrait au frontend
        return jsonify({
            "filename": file.filename,
            "text": extracted_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


