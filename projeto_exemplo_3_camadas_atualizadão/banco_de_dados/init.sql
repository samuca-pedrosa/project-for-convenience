CREATE DATABASE IF NOT EXISTS aplicacao;
USE aplicacao;

CREATE TABLE IF NOT EXISTS produtos (
    id_produto   INT            NOT NULL AUTO_INCREMENT,
    nome         VARCHAR(100)   NOT NULL,
    categoria    VARCHAR(50)    NOT NULL,
    preco        DECIMAL(10, 2) NOT NULL,
    estoque      INT            NOT NULL DEFAULT 0,
    PRIMARY KEY (id_produto)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente    INT          NOT NULL AUTO_INCREMENT,
    nome          VARCHAR(100) NOT NULL,
    cpf           VARCHAR(14)  NOT NULL UNIQUE,
    telefone      VARCHAR(15),
    email         VARCHAR(100),
    data_cadastro DATE         NOT NULL DEFAULT (CURRENT_DATE),
    PRIMARY KEY (id_cliente)
);

CREATE TABLE IF NOT EXISTS vendas (
    id_venda         INT            NOT NULL AUTO_INCREMENT,
    id_cliente       INT,
    data_venda       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total            DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    forma_pagamento  VARCHAR(30)    NOT NULL DEFAULT 'Nao informado',
    PRIMARY KEY (id_venda),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE IF NOT EXISTS itens_venda (
    id_item      INT            NOT NULL AUTO_INCREMENT,
    id_venda     INT            NOT NULL,
    id_produto   INT            NOT NULL,
    quantidade   INT            NOT NULL,
    preco_unit   DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_item),
    FOREIGN KEY (id_venda)   REFERENCES vendas(id_venda),
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
);
