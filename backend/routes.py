from flask import Blueprint, request, jsonify
from utils.AI_API import analyzeEmail, generateReply
from utils.extractor import extractText
from utils.nlp import preprocessText
from utils.database import add_history_entry, get_history, delete_history_entry, patch_history_entry

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
        print("[handleAnalyze] ERRO: Nenhum conteúdo fornecido")
        return jsonify({'error': 'No content provided'}), 400
    
    sender_email = request.form.get('senderEmail', '').strip() or None
    
    preprocessedContent = preprocessText(emailContent)
    
    analysisData = analyzeEmail(preprocessedContent)
    
    if not analysisData:
        print("[handleAnalyze] ERRO: Falha na análise do e-mail (resposta vazia)")
        return jsonify({'error': 'Failed to analyze email'}), 500
    
    try:
        analysisData['originalContent'] = emailContent

        if sender_email:
            analysisData['sender_email'] = sender_email
        
        add_history_entry(emailContent, analysisData, sender_email)

    except Exception as e:
        print(f"[handleAnalyze] ERRO ao processar ou salvar no histórico: {e}")
        return jsonify({'error': f'Erro ao processar ou salvar a análise: {str(e)}'}), 500

    return jsonify(analysisData)

@api.route('/reply', methods=['POST'])
def handleReply():
    data = request.json
    if not data or 'email' not in data or 'type' not in data:
        return jsonify({'error': 'Email and type are required'}), 400

    suggestions = generateReply(data['email'], data['type'], data.get('tone', 'Profissional'))
    if not suggestions:
        return jsonify({'error': 'Failed to generate reply'}), 500
    
    return jsonify({'reply': suggestions})

@api.route('/history', methods=['GET'])
def handleHistory():
    try: 
        history = get_history()
        return jsonify(history), 200
    except Exception as e:
        print(f"Erro ao recuperar histórico: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500
    
@api.route('/history/<int:entryId>', methods=['DELETE'])
def handleDeleteHistoryEntry(entryId):
    try:
        delete_history_entry(entryId)
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
        patch_history_entry(entryId, data)
        return jsonify({'message': 'Entry updated successfully'}), 200
    except Exception as e:
        print(f"Erro ao atualizar entrada do histórico: {e}")
        return jsonify({'error': 'Failed to update history entry'}), 500