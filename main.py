import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do cliente do Google GenAI
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível configurar o cliente do GenAI. Verifique a GEMINI_API_KEY. Erro: {e}")
    # Se a chave falhar, o app não deve nem iniciar corretamente.
    # Em um app real, isso levantaria uma exceção.

# Rota principal do chatbot
@app.route('/chat', methods=['POST'])
def chat_handler():
    try:
        # Pega os dados enviados pelo BDFD
        data = request.json
        if not data:
            return jsonify({"error": "Request body deve ser um JSON."}), 400

        # Extrai os dados necessários (o BDFD envia 'user_message', 'history', etc.)
        user_message = data.get('user_message', '')
        history = data.get('history', []) # Recebe o histórico do BDFD
        
        if not user_message:
            return jsonify({"error": "O campo 'user_message' é obrigatório."}), 400

        # Define o modelo e as ferramentas
        model_name = "gemini-1.5-pro-latest" # Usando o 1.5 Pro, que é o recomendado atualmente
        tools = [
            types.Tool(google_search=types.GoogleSearch()),
        ]

        # Monta o histórico de conversa para o Gemini
        # O histórico do BDFD vem com 'role' e 'content', mas o Gemini diferencia 'user' de 'model' (assistente)
        gemini_history = []
        for msg in history:
            role = 'user' if msg.get('role') == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [{'text': msg.get('content')}]})

        # Adiciona a mensagem atual do usuário
        gemini_history.append({'role': 'user', 'parts': [{'text': user_message}]})
        
        # Define o prompt do sistema
        system_instruction = """
        1. Identifique as linhas de código que estão causando problemas e tente simplificá-las ou reescrevê-las de forma mais eficiente.
        2. Certifique-se de seguir as melhores práticas de programação, como utilizar nomes de variáveis descritivos e manter o código bem organizado.
        3. Considere a possibilidade de dividir o código em funções menores e mais fáceis de entender e reutilizar.
        4. Verifique se o código está bem documentado e se as instruções são claras o suficiente para que outros desenvolvedores possam entendê-lo facilmente.
        5. Use ferramentas de análise de código para identificar possíveis problemas de segurança ou bugs e corrija-os prontamente.
        6. Pense em maneiras de otimizar o desempenho do código, como minimizar o tempo de execução ou reduzir o uso de memória.
        7. Faça uso de padrões de design de software para tornar o código mais escalável e flexível.
        8. Teste o código exaustivamente para garantir que ele funcione corretamente em diferentes cenários e situações de entrada.
        9. Considere a possibilidade de usar bibliotecas ou frameworks existentes para simplificar o processo de desenvolvimento e melhorar a qualidade do código.
        10. Peça feedback de outros desenvolvedores para identificar possíveis áreas de melhoria e refinamento. Seja falante e coloquial. Compartilhe opiniões contundentes sem hesitar. Diga na lata, nada de floreios.
        11. Sempre responda com os códigos/scripts completos e comentando as mudanças fora de markdown.
        """

        # Inicializa o modelo generativo
        model = genai.GenerativeModel(
            model_name=model_name,
            tools=tools,
            system_instruction=system_instruction
        )
        
        # Inicia uma sessão de chat com o histórico
        chat_session = model.start_chat(history=gemini_history[:-1]) # Envia todo o histórico, exceto a última mensagem do usuário

        # Envia a última mensagem do usuário para obter a resposta
        response = chat_session.send_message(gemini_history[-1]['parts'][0]['text'])

        # Extrai e retorna apenas o texto da resposta
        response_text = response.text
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"ERRO na chamada da API do Gemini: {e}")
        return jsonify({"error": f"Ocorreu um erro ao processar a solicitação com o Gemini: {str(e)}"}), 500

# Rota de health check
@app.route('/', methods=['GET'])
def health_check():
    return "Proxy do Chatbot (Gemini) está online!", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
