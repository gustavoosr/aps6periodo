import os
import google.generativeai as gemini
from dotenv import load_dotenv

load_dotenv()

def load_prompt(prompt_file="scripts/prompt.md"):
    """Carrega o prompt de um arquivo"""
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo {prompt_file} não encontrado")
        return None

def runChat(text, prompt_file="scripts/prompt.md"):
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Erro com a chave de API")
        return None
    
    gemini.configure(api_key=api_key)
    
    try:
        # Carrega o prompt base como system instruction
        system_instruction = load_prompt(prompt_file)
        
        if not system_instruction:
            return None
        
        # Cria o modelo com system instruction
        model = gemini.GenerativeModel(
            "gemini-2.0-flash-exp",
            system_instruction=system_instruction
        )
        
        # Envia apenas o relatório (sem repetir o prompt)
        prompt_usuario = f"Analise o seguinte relatório:\n\n{text}"
        
        response = model.generate_content(prompt_usuario)
        
        return response.text
        
    except Exception as e:
        print(f"Erro ao processar: {e}")
        return None

    resultado = runChat(relatorio)
    if resultado:
        print(resultado)