# Estágio 1: Build - Usando uma imagem Python completa para instalar dependências
FROM python:3.11-slim as builder

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências em um ambiente virtual para manter o sistema limpo
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Estágio 2: Produção - Usando uma imagem Python mínima para rodar a aplicação
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o ambiente virtual com as dependências instaladas do estágio de build
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação
COPY main.py .
# O arquivo .env não é copiado. As variáveis de ambiente serão injetadas pela Litegix.

# Expõe a porta que o Gunicorn vai usar (a Litegix vai mapear isso automaticamente)
EXPOSE 8080

# Define o PATH para incluir o ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

# Comando para iniciar a aplicação com Gunicorn
# A variável de ambiente $PORT será fornecida pela Litegix
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
