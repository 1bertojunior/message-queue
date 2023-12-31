-- Criação do banco de dados
CREATE DATABASE mydb;

-- Seleção do banco de dados
USE mydb;

-- Criação da tabela
CREATE TABLE coin (
  id INT PRIMARY KEY AUTO_INCREMENT,
  BRL DECIMAL(10, 2) NOT NULL,
  USD DECIMAL(10, 2) NOT NULL,
  EUR DECIMAL(10, 2) NOT NULL,
  JPY DECIMAL(10, 2) NOT NULL,
  GBP DECIMAL(10, 2) NOT NULL,
  CAD DECIMAL(10, 2) NOT NULL,
  ip_address_sender VARCHAR(15)  NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INSERT TEST
--INSERT INTO coin (BRL, USD, EUR, JPY, GBP, CAD)
--VALUES (0, 1.04, 0.96, 148.1, 0.82, 1.38);
