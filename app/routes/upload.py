from flask import Blueprint, request, jsonify
from pypdf import PdfReader


upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier trouvé"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nom de fichier vide"}), 400

    try:
        
        reader = PdfReader(file)
        texts = [p.extract_text().strip() for p in reader.pages if p.extract_text()]

        
        extracted_text = "\n".join(texts)

    
        return jsonify({
            "filename": file.filename,
            "text": extracted_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


