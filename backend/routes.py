from flask import Blueprint, request, jsonify
from utils.AI_API import analyzeEmail, generateReply
from utils.extractor import extractText
from utils.nlp import preprocessText
from utils.database import addHistoryEntry, getHistory, deleteHistoryEntry, patchHistoryEntry
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

        addHistoryEntry(emailContent, analysisData)

    except (ValueError, json.JSONDecodeError) as e:
        print(f"Erro ao processar resposta da IA: {e}")
        return jsonify({'error': 'Formato de resposta da IA inválido.'}), 500

    return jsonify(analysisData)

@api.route('/reply', methods=['POST'])
def handleReply():
    data = request.json
    if not data or 'email' not in data or 'type' not in data:
        return jsonify({'error': 'Email and type are required'}), 400

    reply = generateReply(data['email'], data['type'], data['tone'])
    if not reply:
        return jsonify({'error': 'Failed to generate reply'}), 500
    
    return jsonify({'reply': reply})

@api.route('/history', methods=['GET'])
def handleHistory():
    try: 
        history = getHistory()
        return jsonify(history), 200
    except Exception as e:
        print(f"Erro ao recuperar histórico: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500
    
@api.route('/history/<int:entryId>', methods=['DELETE'])
def handleDeleteHistoryEntry(entryId):
    try:
        deleteHistoryEntry(entryId)
        return jsonify({'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        print(f"Erro ao deletar entrada do histórico: {e}")
        return jsonify({'error': 'Failed to delete history entry'}), 500

@api.route('/history/<int:entryId>', methods=['PATCH'])
def handlePatchHistoryEntry(entryId):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        patchHistoryEntry(entryId, data)
        return jsonify({'message': 'Entry updated successfully'}), 200
    except Exception as e:
        print(f"Erro ao atualizar entrada do histórico: {e}")
        return jsonify({'error': 'Failed to update history entry'}), 500