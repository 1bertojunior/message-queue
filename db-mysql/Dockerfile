FROM mysql:latest

COPY init.sql /docker-entrypoint-initdb.d/

# Copie o arquivo my.cnf personalizado para a pasta correta dentro do contêiner
COPY my.cnf /etc/mysql/my.cnf