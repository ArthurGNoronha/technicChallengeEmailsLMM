import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")
        
    genai.configure(api_key=api_key)

    print("--- Modelos disponíveis ---")
    found_models = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            found_models = True
    
    if not found_models:
        print("Nenhum modelo compatível encontrado.")
    
    print("---------------------------------------------------------")

except Exception as e:
    print(f"\nOcorreu um erro ao buscar os modelos: {e}")
    print("Por favor, verifique se sua GEMINI_API_KEY no arquivo .env está correta e válida.")