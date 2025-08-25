import os
import json
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do cliente da Groq
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível inicializar o cliente da Groq. Verifique a GROQ_API_KEY. Erro: {e}")
    groq_client = None

# Rota principal do chatbot
@app.route('/chat', methods=['POST'])
def chat_handler():
    if not groq_client:
        return jsonify({"error": "Servidor não configurado corretamente. API Key da Groq ausente."}), 500

    # Pega os dados enviados pelo BDFD
    data = request.json
    if not data:
        return jsonify({"error": "Request body deve ser um JSON."}), 400

    # Extrai os dados necessários (com valores padrão para segurança)
    system_prompt = data.get('system_prompt', 'Você é um assistente prestativo.')
    history = data.get('history', [])
    user_message = data.get('user_message', '')
    model = data.get('model', 'llama3-8b-8192')

    if not user_message:
        return jsonify({"error": "O campo 'user_message' é obrigatório."}), 400

    # Monta a estrutura de mensagens para a API da Groq
    messages = [
        {"role": "system", "content": system_prompt},
        *history,  # Desempacota o histórico recebido
        {"role": "user", "content": user_message}
    ]

    try:
        # Faz a chamada para a API da Groq
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=model,
        )
        # Extrai e retorna apenas o texto da resposta
        response_text = chat_completion.choices[0].message.content
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"ERRO na chamada da API da Groq: {e}")
        return jsonify({"error": f"Ocorreu um erro ao processar a solicitação: {str(e)}"}), 500

# Rota de health check para a Litegix saber que o app está vivo
@app.route('/', methods=['GET'])
def health_check():
    return "Proxy do Chatbot está online!", 200

if __name__ == "__main__":
    # A Litegix vai usar um servidor de produção como o Gunicorn, mas isso é para testes locais
    app.run(host='0.0.0.0', port=8080)
