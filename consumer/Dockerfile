# Define a imagem base
FROM python:3

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos de código-fonte para o diretório de trabalho
COPY . /app

# Instala as dependências do aplicativo (arquivo requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Define o comando padrão a ser executado quando o contêiner for iniciado
CMD [ "python", "consume.py" ]