import os
import google.generativeai as gemini
from dotenv import load_dotenv


load_dotenv()

def runChat(text):

    api_key = os.getenv("API_KEY")

    if not api_key:
        print("Erro com a chave de API")
        return
    
    gemini.configure(api_key=api_key)


    try:
        model = gemini.GenerativeModel("gemini-2.5-flash")
        prompt = os.getenv("PROMPTS")

        while True:
            test
    except Exception as e:
        print("Não foi possível carregar o modelo")
        return