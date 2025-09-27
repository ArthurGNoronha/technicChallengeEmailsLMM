from flask import Blueprint, request, jsonify
from utils.AI_API import analyzeEmail, generateReply
from utils.extractor import extractText
import json

api = Blueprint('api', __name__)

def getContent():
    parts = []
    
    email_body = request.form.get('text', '').strip()
    if email_body:
        parts.append(f"Corpo do E-mail:\n{email_body}")

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        attachment_content = extractText(file)
        if attachment_content:
            if parts:
                parts.append("\n---\n")
            parts.append(f"Conteúdo do Anexo ({file.filename}):\n{attachment_content}")
    
    return "".join(parts)

@api.route('/analyze', methods=['POST'])
def handleAnalyze():
    emailContent = getContent()
    if not emailContent:
        return jsonify({'error': 'No content provided'}), 400
    
    analysis_text = analyzeEmail(emailContent)
    if not analysis_text:
        return jsonify({'error': 'Failed to analyze email'}), 500
    
    try:
        start = analysis_text.find('{')
        end = analysis_text.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("JSON não encontrado na resposta da IA")
        
        json_str = analysis_text[start:end]
        
        analysis_data = json.loads(json_str)
        
        analysis_data['original_content'] = emailContent

    except (ValueError, json.JSONDecodeError) as e:
        print(f"Erro ao processar resposta da IA: {e}")
        return jsonify({'error': 'Formato de resposta da IA inválido.'}), 500

    return jsonify(analysis_data)

@api.route('/reply', methods=['POST'])
def handleReply():
    data = request.json
    if not data or 'email' not in data or 'type' not in data:
        return jsonify({'error': 'Email and type are required'}), 400
    
    reply = generateReply(data['email'], data['type'])
    if not reply:
        return jsonify({'error': 'Failed to generate reply'}), 500
    
    return jsonify({'reply': reply})