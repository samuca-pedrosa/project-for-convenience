# Projeto exemplo: conveniência de posto em 3 camadas, com interface Tkinter

Aplicação em Python organizada em três camadas (apresentação, negócio e
dados), usando Factory e Singleton para a conexão com o banco. O exemplo
simula o sistema de uma conveniência de posto: produtos, clientes e vendas
(com itens de venda e baixa automática de estoque).

A aplicação é uma **interface gráfica de desktop feita com Tkinter**
(`src/main.py`), com abas para Produtos, Clientes e Vendas. O banco de dados
é **MySQL**, rodando em um container Docker.

## O que o exemplo faz

- cadastrar, listar, buscar (via filtro), atualizar e remover **produtos**
  (nome, categoria, preço, estoque);
- cadastrar, listar, buscar (via filtro), atualizar e remover **clientes**
  (nome, CPF, telefone, email);
- registrar **vendas** com um ou mais itens (montando um carrinho na tela),
  escolhendo a **forma de pagamento** (Pix, Espécie, Cartão de Débito ou
  Cartão de Crédito) em uma janela dedicada ao finalizar a venda, validando
  estoque disponível, calculando o total automaticamente e dando baixa no
  estoque dos produtos vendidos;
- listar vendas (com a forma de pagamento de cada uma), ver os itens de uma
  venda e removê-la.

## Estrutura de pastas

```text
projeto_exemplo_3_camadas_atualizado/
├── banco_de_dados/
│   └── init.sql                    # cria o banco e as 4 tabelas
├── docker-compose.yml               # sobe o MySQL
├── README.md
├── requirements.txt
└── src/
    ├── apresentacao/
    │   ├── interface_tkinter.py     # interface gráfica (janela principal e as 3 abas)
    │   └── fabrica_servicos.py      # monta conexão -> repositório -> serviço
    ├── config/
    │   └── configuracao_banco.py    # lê host/porta/usuário/senha do ambiente
    ├── dados/
    │   ├── conexao_factory.py       # Factory: cria a conexão MySQL
    │   ├── conexao_singleton.py     # Singleton: reaproveita a conexão
    │   ├── produto_repository.py
    │   ├── cliente_repository.py
    │   ├── vendas_repository.py
    │   └── itensvenda_repository.py
    ├── dominio/
    │   ├── produtos.py
    │   ├── cliente.py
    │   ├── venda.py
    │   └── itens_venda.py
    ├── negocio/
    │   ├── produto_service.py
    │   ├── cliente_service.py
    │   └── venda_service.py         # orquestra venda + itens + baixa de estoque
    └── main.py                      # ponto de entrada (abre a janela Tkinter)
```

## Pré-requisitos

- Python 3.10 ou superior (o Tkinter já vem embutido no Python na maioria
  das instalações; no Linux, se faltar, instale o pacote `python3-tk` pelo
  gerenciador de pacotes do seu sistema, ex.: `sudo apt install python3-tk`);
- Docker e Docker Compose;
- opcionalmente o DBeaver para acessar o MySQL.

## Subir o MySQL

```bash
docker compose up -d
```

O container sobe com:

- host: `127.0.0.1`
- porta: `3306`
- usuário: `root`
- senha: `labinfo`
- banco: `aplicacao`

As tabelas (`produtos`, `clientes`, `vendas`, `itens_venda`) são criadas
automaticamente pelo `init.sql` na primeira subida do container, e também são
garantidas por cada repositório ao iniciar a aplicação (`CREATE TABLE IF NOT
EXISTS`), então não há passo manual de migração.

## Instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

A única dependência externa é o `mysql-connector-python`. O Tkinter faz parte
da biblioteca padrão do Python.

## Configuração da conexão com o banco

A conexão é lida de variáveis de ambiente (com valores padrão iguais aos do
`docker-compose.yml`, então **funciona sem configurar nada** se você só subiu
o Docker padrão). Para customizar, defina antes de rodar:

| Variável      | Padrão        | Descrição                  |
|---------------|---------------|-----------------------------|
| `DB_HOST`     | `127.0.0.1`   | host do MySQL               |
| `DB_PORT`     | `3306`        | porta do MySQL              |
| `DB_USER`     | `root`        | usuário                     |
| `DB_PASSWORD` | `labinfo`     | senha                       |
| `DB_NAME`     | `aplicacao`   | nome do banco                |

Exemplo (Linux/macOS):

```bash
export DB_HOST=127.0.0.1
export DB_PASSWORD=labinfo
```

## Executar a aplicação

Com o MySQL no ar (`docker compose up -d`) e as dependências instaladas:

```bash
python -m src.main
```

Isso abre a janela do sistema, com uma barra lateral para navegar entre
**Produtos**, **Clientes** e **Vendas**.

Se o MySQL não estiver acessível, a aplicação mostra uma caixa de diálogo
explicando o problema (host/porta/banco configurados e o comando para subir
o Docker) em vez de travar ou fechar sem explicação.

### Aba Produtos / Aba Clientes

- formulário à esquerda para cadastrar um novo registro;
- clique em uma linha da lista à direita para carregar os dados no
  formulário — os botões **Salvar** (atualiza) e **Remover** passam a agir
  sobre aquele registro;
- botão **Novo** limpa o formulário e volta ao modo de cadastro;
- campo **Filtrar** faz busca em tempo real por nome (produtos e clientes) e
  categoria (produtos);
- tentar remover um produto ou cliente que já tem vendas associadas mostra
  um aviso explicando o motivo, em vez de um erro técnico.

### Aba Vendas

- escolha um cliente (opcional) e um produto, informe a quantidade e clique
  em **Adicionar item** para montar o carrinho da venda;
- o total é calculado automaticamente à medida que os itens são adicionados
  e fica destacado em um cartão de total;
- ao clicar em **Finalizar venda**, abre uma janela para escolher a
  **forma de pagamento** (Pix, Espécie, Cartão de Débito ou Cartão de
  Crédito); a venda só é gravada depois dessa escolha — cancelar a janela
  cancela a finalização e mantém o carrinho intacto;
- a venda e os itens são gravados no banco e o estoque dos produtos vendidos
  é reduzido automaticamente (a aba Produtos reflete o novo estoque assim
  que você a visita novamente);
- a lista de vendas registradas fica na parte inferior da tela, já com a
  forma de pagamento de cada uma; selecione uma venda e use **Ver itens**
  para abrir uma janela com o detalhamento, ou **Remover venda** para
  excluí-la.

## Conexão no DBeaver

Use estes dados:

- host: `localhost`
- porta: `3306`
- database: `aplicacao`
- username: `root`
- password: `labinfo`

## Como o projeto se organiza

### `src/apresentacao`
Camada de interface com o usuário. `interface_tkinter.py` contém a janela
principal (`AplicacaoPrincipal`) e as três abas (`AbaProdutos`,
`AbaClientes`, `AbaVendas`), que conversam apenas com a camada de negócio —
nunca diretamente com o banco.

### `src/negocio`
Camada de regras de negócio. Valida nome, preço, estoque, CPF, e orquestra a
criação de vendas (verificação de estoque, cálculo de total, baixa de
estoque).

### `src/dados`
Camada de acesso a dados. Cria a conexão, executa SQL e persiste produtos,
clientes, vendas e itens de venda.

### `src/dominio`
Entidades do domínio da aplicação (dataclasses simples).

### `src/config`
Centraliza a leitura da configuração de conexão a partir de variáveis de
ambiente.

## Factory e Singleton

### Factory

Arquivo: `src/dados/conexao_factory.py`

Centraliza a criação da conexão com o MySQL.

### Singleton

Arquivo: `src/dados/conexao_singleton.py`

Garante que a aplicação reutilize uma única conexão durante a execução. A
conexão é fechada automaticamente quando a janela é encerrada.

## Observações

- As tabelas são criadas pelo `init.sql` do container e também são
  garantidas por cada repositório ao iniciar a aplicação.
- O exemplo mantém SQL cru para facilitar o uso em aula e a comparação entre
  as camadas.
- A camada de apresentação anterior (API Flask e versão em terminal) foi
  removida; a interface gráfica em Tkinter reaproveita integralmente as
  camadas de negócio e dados já existentes, sem nenhuma mudança de regra de
  negócio ou de schema do banco.
- Erros de integridade do banco (ex.: remover um produto que já tem vendas,
  ou cadastrar um CPF duplicado) são convertidos em mensagens amigáveis na
  tela, em vez de mostrar o erro técnico do MySQL cru.
- Se você já tinha um banco criado antes da forma de pagamento existir, não
  precisa recriar nada: a aplicação detecta a ausência da coluna
  `forma_pagamento` na tabela `vendas` e a adiciona automaticamente na
  primeira execução.
