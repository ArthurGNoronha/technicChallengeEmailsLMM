import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = genai.types.GenerationConfig(
    response_mime_type='application/json'
)

model = genai.GenerativeModel(
    'models/gemini-2.0-flash',
    generation_config=generation_config
)

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
                
        data = json.loads(response.text)
        if isinstance(data, list) and data:
            return data[0]
        return data
    
    except (json.JSONDecodeError, Exception) as e:
        print(f"[analyzeEmail] ERRO ao analisar e-mail: {e}")
        return {
            "type": "Produtivo",
            "summary": "Não foi possível analisar este e-mail automaticamente.",
            "keyPoints": ["Erro na análise automática. Por favor, revise manualmente."],
            "urgency": 3
        }
    
    except json.JSONDecodeError as jde:
        print(f"[analyzeEmail] ERRO JSON inválido: {jde}")
        return '''
        {
            "type": "Produtivo",
            "summary": "Não foi possível analisar este e-mail automaticamente.",
            "keyPoints": ["Erro na análise automática. Por favor, revise manualmente."],
            "urgency": 3
        }
        '''

    except Exception as e:
        print(f"[analyzeEmail] ERRO ao analisar e-mail: {e}")
        return '''
        {
            "type": "Produtivo",
            "summary": "Não foi possível analisar este e-mail automaticamente.",
            "keyPoints": ["Erro na análise automática. Por favor, revise manualmente."],
            "urgency": 3
        }
        '''

def generateReply(email_content, type, tone="Profissional"):
    if type == 'Improdutivo':
        return ["Obrigado pela sua mensagem! Agradecemos o seu contato."]
        
    prompt = f"""
    Com base no e-mail abaixo, gere uma lista de 3 sugestões de respostas curtas com um tom '{tone}'.
    Retorne o resultado como um array JSON de strings. Exemplo: ["sugestão 1", "sugestão 2", "sugestão 3"]

    E-mail:
    ---
    {email_content}
    ---
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Erro ao gerar resposta: {e}")
        return ["Não foi possível gerar sugestões de resposta."]