<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:131826,100:3B6CF6&height=220&section=header&text=Bem-vindos!&fontSize=55&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Sistema%20de%20Convenien%20cia%20-%20Arquitetura%20em%203%20Camadas&descAlignY=55&descSize=18" width="100%"/>

<a href="https://readme-typing-svg.demolab.com">
  <img src="https://readme-typing-svg.demolab.com/?font=Fira+Code&size=20&pause=1200&color=3B6CF6&center=true&vCenter=true&width=650&lines=Interface+Desktop+em+Tkinter;Banco+de+Dados+MySQL;Padr%C3%B5es+Factory+%2B+Singleton;Produtos+%C2%B7+Clientes+%C2%B7+Vendas" alt="Typing SVG" />
</a>

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3B6CF6?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-17A865?style=for-the-badge&logo=mysql&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-8B7CF6?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-17A865?style=for-the-badge)
![License](https://img.shields.io/badge/licen%C3%A7a-MIT-131826?style=for-the-badge)

</div>

<br/>

## Sobre o projeto

Sistema de gestão para uma **conveniência de posto**, com cadastro de produtos, clientes e registro de vendas — incluindo carrinho de compras, escolha de forma de pagamento e baixa automática de estoque.

Construído como exercício de **arquitetura em 3 camadas** (Apresentação → Negócio → Dados), com os padrões de projeto **Factory** e **Singleton** aplicados na camada de acesso a dados.

<br/>

## Índice

- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Padrões de projeto](#padrões-de-projeto)
- [Tecnologias](#tecnologias)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Como rodar](#como-rodar)
- [Banco de dados](#banco-de-dados)
- [Metodologia](#metodologia)
- [Equipe](#equipe)

<br/>

## Funcionalidades

- 📦 **Produtos** — cadastrar, listar, filtrar, editar e remover, com controle de estoque
- 👤 **Clientes** — cadastrar, listar, filtrar, editar e remover, com validação de CPF
- 🧾 **Vendas** — montar carrinho, escolher forma de pagamento (Pix, Espécie, Cartão de Débito ou Cartão de Crédito), finalizar venda com baixa automática de estoque, consultar itens de uma venda e removê-la

<br/>

## Arquitetura

O sistema segue o padrão de **3 camadas**, onde cada camada só conversa com a vizinha logo abaixo:

```
Apresentação (Tkinter)  →  Negócio (regras)  →  Dados (SQL)  →  MySQL
```

| Camada | Pasta | Responsabilidade |
|---|---|---|
| 🖥️ Apresentação | `src/apresentacao/` | Telas, botões, tabelas — tudo que o usuário vê e clica |
| ⚙️ Negócio | `src/negocio/` | Validações e regras (preço não pode ser negativo, CPF válido, estoque suficiente...) |
| 🗄️ Dados | `src/dados/` | Monta e executa comandos SQL no MySQL |
| 🧩 Domínio | `src/dominio/` | Classes simples que representam os dados, sem lógica |
| 🔧 Config | `src/config/` | Lê host/porta/usuário/senha do banco a partir de variáveis de ambiente |

> A interface **nunca** executa SQL nem fala com o banco diretamente — todo clique de botão chama um método de um *service*, que só então aciona um *repository*.

<br/>

## Padrões de projeto

<table>
<tr>
<td width="50%" valign="top">

### 🏭 Factory
`src/dados/conexao_factory.py`

Sabe **criar** a conexão certa com o banco a partir da configuração recebida.

</td>
<td width="50%" valign="top">

### 🔂 Singleton
`src/dados/conexao_singleton.py`

Garante que **só existe uma** conexão ativa, reaproveitada por todos os repositórios da aplicação.

</td>
</tr>
</table>

<br/>

## Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-3776AB?style=flat-square&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Projects](https://img.shields.io/badge/GitHub%20Projects-Kanban-181717?style=flat-square&logo=github&logoColor=white)

<br/>

## Estrutura de pastas

```text
projeto_exemplo_3_camadas_atualizado/
├── banco_de_dados/
│   └── init.sql                 # cria o banco e as 4 tabelas
├── docker-compose.yml           # sobe o MySQL automaticamente
├── requirements.txt
├── README.md
└── src/
    ├── apresentacao/
    │   ├── interface_tkinter.py # janela principal + abas
    │   └── fabrica_servicos.py  # monta conexão → repositório → service
    ├── config/
    │   └── configuracao_banco.py
    ├── dados/
    │   ├── conexao_factory.py
    │   ├── conexao_singleton.py
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
    │   └── venda_service.py
    └── main.py                  # ponto de entrada
```

<br/>

## Como rodar

### Pré-requisitos
- Python 3.10+
- MySQL 8.0 (via Docker **ou** instalado localmente)

### 1. Subir o banco de dados

**Com Docker (recomendado):**
```bash
docker compose up -d
```

**Sem Docker:** instale o MySQL localmente e crie o banco `aplicacao`; as tabelas são criadas automaticamente na primeira execução da aplicação.

### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 3. Rodar a aplicação
```bash
python -m src.main
```

> Se a senha do seu MySQL for diferente do padrão (`labinfo`), defina `DB_PASSWORD` (e demais variáveis, se necessário) antes de rodar — veja a tabela completa no código de `src/config/configuracao_banco.py`.

<br/>

## Banco de dados

| Tabela | Principais campos |
|---|---|
| `produtos` | `id_produto`, `nome`, `categoria`, `preco`, `estoque` |
| `clientes` | `id_cliente`, `nome`, `cpf` (único), `telefone`, `email`, `data_cadastro` |
| `vendas` | `id_venda`, `id_cliente` (FK), `data_venda`, `total`, `forma_pagamento` |
| `itens_venda` | `id_item`, `id_venda` (FK), `id_produto` (FK), `quantidade`, `preco_unit` |

<br/>

## Metodologia

O desenvolvimento foi organizado em um quadro **Kanban no GitHub Projects**, com colunas `ALL` → `In Progress` → `In Review` → `Done`, partindo de um levantamento de casos de uso até a entrega de cada funcionalidade.

<br/>

## Equipe


| Nome | GitHub |
|---|---|
|Samuca | [@usuario]((https://github.com/samuca-pedrosa/)) |
| _nome do colega_ | [@usuario](https://github.com/odavigonzaga) |

<br/>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:3B6CF6,100:131826&height=120&section=footer" width="100%"/>

Feito com 💙 para fins acadêmicos

</div>
