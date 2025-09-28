import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('models/gemini-2.0-flash')

def analyzeEmail(email_content):
    prompt = f"""
    Analise o seguinte e-mail e forneça as seguintes informações em formato JSON:
    1.  'type': Classifique o e-mail como 'Produtivo' (requer uma ação) ou 'Improdutivo' (não requer ação imediata).
    2.  'summary': Um resumo conciso do e-mail em no máximo três frases.
    3.  'keyPoints': Uma lista dos pontos mais importantes.
    4.  'urgency': Uma pontuação de urgência de 1 (menos urgente) a 5 (mais urgente).

    E-mail:
    ---
    {email_content}
    ---
    
    Responsa APENAS com o objeto JSON, sem texto adicional ou formatação.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao analisar e-mail: {e}")
        return None

def generateReply(email_content, type, tone="Profissional"):
    if type == 'Improdutivo':
        return "Obrigado pela sua mensagem! Agradecemos o seu contato."
    prompt = f"""
    Com base no e-mail abaixo, gere uma lista de 3 sugestões de respostas curtas e com um tom '{tone}'.
    Retorne o resultado como um array JSON de strings, e nada mais. Exemplo de formato: ["sugestão 1", "sugestão 2", "sugestão 3"]

    E-mail:
    ---
    {email_content}
    ---
    """
    try:
        response = model.generate_content(prompt)
        
        text_response = response.text
        start = text_response.find('[')
        end = text_response.rfind(']') + 1
        if start == -1 or end == 0:
            return [text_response.strip()]
            
        json_str = text_response[start:end]
        
        suggestions = json.loads(json_str)
        return suggestions
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return None