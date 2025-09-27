from flask import Blueprint, request, jsonify
from utils.AI_API import analyzeEmail, generateReply
from utils.extractor import extractText
from utils.nlp import preprocessText
import json

api = Blueprint('api', __name__)

def getContent():
    parts = []
    
    emailBody = request.form.get('text', '').strip()
    if emailBody:
        parts.append(f"Corpo do E-mail:\n{emailBody}")

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        attachedContent = extractText(file)
        if attachedContent:
            if parts:
                parts.append("\n---\n")
            parts.append(f"Conteúdo do Anexo ({file.filename}):\n{attachedContent}")

    return "".join(parts)

@api.route('/analyze', methods=['POST'])
def handleAnalyze():
    emailContent = getContent()
    if not emailContent:
        return jsonify({'error': 'No content provided'}), 400
    
    preprocessedContent = preprocessText(emailContent)
    analysisText = analyzeEmail(preprocessedContent)
    if not analysisText:
        return jsonify({'error': 'Failed to analyze email'}), 500
    
    try:
        start = analysisText.find('{')
        end = analysisText.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("JSON não encontrado na resposta da IA")

        jsonStr = analysisText[start:end]

        analysisData = json.loads(jsonStr)

        analysisData['originalContent'] = emailContent

    except (ValueError, json.JSONDecodeError) as e:
        print(f"Erro ao processar resposta da IA: {e}")
        return jsonify({'error': 'Formato de resposta da IA inválido.'}), 500

    return jsonify(analysisData)

@api.route('/reply', methods=['POST'])
def handleReply():
    data = request.json
    if not data or 'email' not in data or 'type' not in data:
        return jsonify({'error': 'Email and type are required'}), 400
    
    reply = generateReply(data['email'], data['type'])
    if not reply:
        return jsonify({'error': 'Failed to generate reply'}), 500
    
    return jsonify({'reply': reply})