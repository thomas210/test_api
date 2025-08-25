FROM python:3.9-slim

WORKDIR /app


# Copia o resto do código para o contêiner.
COPY . .

# Instala as dependências.
RUN pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente para que o Flask saiba qual arquivo executar.
ENV FLASK_APP=app.py

# Expõe a porta que o aplicativo Flask irá usar (a porta padrão é 5000).
EXPOSE 5000

# Comando para iniciar o servidor Gunicorn.
# O Gunicorn é um servidor de produção mais robusto que o servidor de desenvolvimento do Flask.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]