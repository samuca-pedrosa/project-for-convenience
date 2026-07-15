"""
Camada de apresentacao: interface grafica em Tkinter.

Esta e' a interface principal (e unica) da aplicacao. Ela conversa com a
mesma camada de negocio (src/negocio) que ja existia, entao todas as regras
de validacao, o calculo automatico do total da venda e a baixa de estoque
continuam funcionando exatamente como antes -- so a "porta de entrada" mudou
de uma API HTTP para uma janela grafica.

Estrutura desta tela:
- uma barra lateral fixa para navegar entre Produtos, Clientes e Vendas;
- secao "Produtos" com formulario + lista (CRUD completo);
- secao "Clientes" com formulario + lista (CRUD completo);
- secao "Vendas" com montagem de carrinho, escolha da forma de pagamento na
  hora de finalizar a venda (Pix, Especie, Cartao de Debito ou Cartao de
  Credito) e uma lista das vendas ja registradas.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

import mysql.connector

from src.negocio.cliente_service import ClienteService
from src.negocio.produto_service import ProdutoService
from src.negocio.venda_service import VendaService


# Paleta de cores e fontes usadas em toda a interface

COR_FUNDO = "#eef1f7"
COR_SIDEBAR = "#131826"
COR_SIDEBAR_HOVER = "#1f2636"
COR_SIDEBAR_ATIVO = "#1f2636"
COR_SIDEBAR_TEXTO = "#c7cddb"
COR_SIDEBAR_SUBTEXTO = "#6b7284"

COR_ACCENT = "#3b6cf6"
COR_ACCENT_HOVER = "#2f57d1"
COR_ACCENT_SUAVE = "#e4ebff"

COR_SUCESSO = "#17a865"
COR_SUCESSO_HOVER = "#128a53"
COR_PERIGO = "#e5484d"
COR_PERIGO_HOVER = "#c9393e"
COR_SECUNDARIO = "#e7eaf1"
COR_SECUNDARIO_HOVER = "#d9dee9"

COR_TEXTO = "#161a23"
COR_TEXTO_SUAVE = "#6b7280"
COR_CARD = "#ffffff"
COR_BORDA = "#e3e7ef"
COR_ZEBRA = "#f6f8fc"

FONTE_BASE = ("Segoe UI", 10)
FONTE_TITULO_APP = ("Segoe UI", 13, "bold")
FONTE_TITULO_SECAO = ("Segoe UI", 19, "bold")
FONTE_SUBTITULO_SECAO = ("Segoe UI", 10)
FONTE_SECAO = ("Segoe UI", 11, "bold")
FONTE_BOTAO = ("Segoe UI", 9, "bold")
FONTE_RODAPE = ("Segoe UI", 8)
FONTE_NAV = ("Segoe UI", 10, "bold")
FONTE_TOTAL = ("Segoe UI", 15, "bold")

# Helpers de botoes coloridos (tk.Button simples, para ter controle total
# sobre cor de fundo/hover em qualquer sistema operacional)

def _criar_botao(master, texto, comando, bg, fg, hover, **extra) -> tk.Button:
    opcoes = dict(
        text=texto,
        command=comando,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        font=FONTE_BOTAO,
        relief="flat",
        bd=0,
        padx=16,
        pady=8,
        cursor="hand2",
    )
    opcoes.update(extra)
    botao = tk.Button(master, **opcoes)
    botao.bind("<Enter>", lambda e: botao.config(bg=hover))
    botao.bind("<Leave>", lambda e: botao.config(bg=bg))
    return botao


def botao_primario(master, texto, comando) -> tk.Button:
    return _criar_botao(master, texto, comando, COR_ACCENT, "white", COR_ACCENT_HOVER)


def botao_sucesso(master, texto, comando) -> tk.Button:
    return _criar_botao(master, texto, comando, COR_SUCESSO, "white", COR_SUCESSO_HOVER)


def botao_perigo(master, texto, comando) -> tk.Button:
    return _criar_botao(master, texto, comando, COR_PERIGO, "white", COR_PERIGO_HOVER)


def botao_secundario(master, texto, comando) -> tk.Button:
    return _criar_botao(master, texto, comando, COR_SECUNDARIO, COR_TEXTO, COR_SECUNDARIO_HOVER)


def _tratar_erro_servico(erro: Exception, contexto_integridade: str = "") -> None:
    """Mostra uma messagebox amigavel para os tipos de erro mais comuns."""
    if isinstance(erro, ValueError):
        messagebox.showerror("Dados invalidos", str(erro))
    elif isinstance(erro, mysql.connector.Error):
        detalhe = str(erro)
        if contexto_integridade and ("1451" in detalhe or "foreign key" in detalhe.lower()):
            messagebox.showerror("Nao foi possivel concluir", contexto_integridade + "\n\nDetalhes: " + detalhe)
        elif "1062" in detalhe or "duplicate" in detalhe.lower():
            messagebox.showerror("Registro duplicado", "Ja existe um registro com esse valor unico (ex.: CPF).\n\nDetalhes: " + detalhe)
        else:
            messagebox.showerror("Erro de banco de dados", detalhe)
    else:
        messagebox.showerror("Erro inesperado", str(erro))


def _card(master) -> tk.Frame:
    """Cria um 'cartao' branco com borda suave, usado em toda a interface."""
    return tk.Frame(master, bg=COR_CARD, highlightbackground=COR_BORDA, highlightthickness=1)


def _configurar_zebra(tabela: ttk.Treeview) -> None:
    tabela.tag_configure("par", background=COR_ZEBRA)
    tabela.tag_configure("impar", background=COR_CARD)


def _preencher_com_zebra(tabela: ttk.Treeview, linhas: list[tuple]) -> None:
    tabela.delete(*tabela.get_children())
    for indice, valores in enumerate(linhas):
        tag = "par" if indice % 2 == 0 else "impar"
        tabela.insert("", "end", values=valores, tags=(tag,))



# Dialogo de forma de pagamento

FORMAS_PAGAMENTO = [
    ("Pix", "◐  Pix", "#0ea5b7"),
    ("Especie", "$  Especie", "#17a865"),
    ("Cartao de Debito", "▤  Cartao de Debito", "#7c5cf0"),
    ("Cartao de Credito", "▥  Cartao de Credito", "#ea6b2c"),
]


def abrir_dialogo_pagamento(parent: tk.Widget, total: float) -> Optional[str]:
    """Abre uma janela modal para o usuario escolher a forma de pagamento.

    Retorna o rotulo escolhido, ou None se o usuario cancelar.
    """
    resultado: dict = {"forma": None}
    janela_pai = parent.winfo_toplevel()

    janela = tk.Toplevel(parent)
    janela.title("Forma de pagamento")
    janela.configure(bg=COR_CARD)
    janela.resizable(False, False)
    janela.transient(janela_pai)

    tk.Label(
        janela, text="Como o cliente vai pagar?", bg=COR_CARD, fg=COR_TEXTO, font=FONTE_TITULO_SECAO,
    ).pack(padx=32, pady=(28, 6))
    tk.Label(
        janela, text=f"Total da venda: R$ {total:.2f}", bg=COR_CARD, fg=COR_TEXTO_SUAVE, font=FONTE_BASE,
    ).pack(padx=32, pady=(0, 22))

    grade = tk.Frame(janela, bg=COR_CARD)
    grade.pack(padx=32, pady=(0, 8))

    def escolher(rotulo: str) -> None:
        resultado["forma"] = rotulo
        janela.destroy()

    for indice, (chave, rotulo_exibido, cor) in enumerate(FORMAS_PAGAMENTO):
        linha, coluna = divmod(indice, 2)
        botao_cor = _criar_botao(
            grade, rotulo_exibido, lambda c=chave: escolher(c), cor, "white", cor,
            width=18, height=3, font=("Segoe UI", 10, "bold"),
        )
        botao_cor.grid(row=linha, column=coluna, padx=6, pady=6)

    botao_secundario(janela, "Cancelar", janela.destroy).pack(pady=(10, 26))

    janela.update_idletasks()
    largura, altura = janela.winfo_width(), janela.winfo_height()
    x = janela_pai.winfo_rootx() + (janela_pai.winfo_width() - largura) // 2
    y = janela_pai.winfo_rooty() + (janela_pai.winfo_height() - altura) // 2
    janela.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    janela.grab_set()
    janela.wait_window(janela)
    return resultado["forma"]



# Secao de Produtos

class AbaProdutos(tk.Frame):
    def __init__(self, master: tk.Widget, servico: ProdutoService) -> None:
        super().__init__(master, bg=COR_FUNDO)
        self.servico = servico
        self.id_selecionado: Optional[int] = None
        self._todos: list = []
        self._montar_layout()
        self.atualizar_lista()

    def _montar_layout(self) -> None:
        painel = tk.Frame(self, bg=COR_FUNDO)
        painel.pack(fill="both", expand=True)
        painel.columnconfigure(1, weight=1)
        painel.rowconfigure(0, weight=1)

        card = _card(painel)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(card, text="Cadastro de produto", bg=COR_CARD, fg=COR_TEXTO, font=FONTE_SECAO).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 4)
        )
        tk.Label(
            card, text="Clique em uma linha da lista para editar ou remover.",
            bg=COR_CARD, fg=COR_TEXTO_SUAVE, font=FONTE_RODAPE,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 14))

        self.var_nome = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_preco = tk.StringVar()
        self.var_estoque = tk.StringVar()

        self._campo(card, 2, "Nome", self.var_nome)
        self._campo(card, 3, "Categoria", self.var_categoria)
        self._campo(card, 4, "Preco (R$)", self.var_preco)
        self._campo(card, 5, "Estoque", self.var_estoque)

        botoes = tk.Frame(card, bg=COR_CARD)
        botoes.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(16, 22))
        botao_primario(botoes, "Salvar", self._salvar).pack(side="left", padx=(0, 6))
        botao_secundario(botoes, "Novo", self._limpar).pack(side="left", padx=(0, 6))
        botao_perigo(botoes, "Remover", self._remover).pack(side="left")

        direita = tk.Frame(painel, bg=COR_FUNDO)
        direita.grid(row=0, column=1, sticky="nsew")
        direita.rowconfigure(1, weight=1)
        direita.columnconfigure(0, weight=1)

        topo = tk.Frame(direita, bg=COR_FUNDO)
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(topo, text="Produtos cadastrados", bg=COR_FUNDO, fg=COR_TEXTO, font=FONTE_SECAO).pack(side="left")
        tk.Label(topo, text="Filtrar:", bg=COR_FUNDO, fg=COR_TEXTO_SUAVE).pack(side="left", padx=(18, 4))
        self.var_filtro = tk.StringVar()
        self.var_filtro.trace_add("write", lambda *_: self._filtrar())
        ttk.Entry(topo, textvariable=self.var_filtro, width=24).pack(side="left")
        botao_secundario(topo, "Atualizar lista", self.atualizar_lista).pack(side="right")

        lista_card = _card(direita)
        lista_card.grid(row=1, column=0, sticky="nsew")
        lista_card.rowconfigure(0, weight=1)
        lista_card.columnconfigure(0, weight=1)

        colunas = ("id", "nome", "categoria", "preco", "estoque")
        self.tabela = ttk.Treeview(lista_card, columns=colunas, show="headings", selectmode="browse")
        titulos = {"id": "ID", "nome": "Nome", "categoria": "Categoria", "preco": "Preco (R$)", "estoque": "Estoque"}
        larguras = {"id": 55, "nome": 260, "categoria": 140, "preco": 110, "estoque": 90}
        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, width=larguras[col], anchor="w" if col == "nome" else "center")
        _configurar_zebra(self.tabela)
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        barra = ttk.Scrollbar(lista_card, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)

    def _campo(self, card, linha, rotulo, variavel) -> ttk.Entry:
        tk.Label(card, text=rotulo, bg=COR_CARD, fg=COR_TEXTO_SUAVE, font=FONTE_BASE).grid(
            row=linha, column=0, sticky="w", padx=(20, 10), pady=6
        )
        entrada = ttk.Entry(card, textvariable=variavel, width=26)
        entrada.grid(row=linha, column=1, sticky="ew", padx=(0, 20), pady=6)
        return entrada

    def _limpar(self) -> None:
        self.id_selecionado = None
        self.var_nome.set("")
        self.var_categoria.set("")
        self.var_preco.set("")
        self.var_estoque.set("")
        for item in self.tabela.selection():
            self.tabela.selection_remove(item)

    def _selecionar(self, event=None) -> None:
        selecionado = self.tabela.selection()
        if not selecionado:
            return
        valores = self.tabela.item(selecionado[0], "values")
        self.id_selecionado = int(valores[0])
        self.var_nome.set(valores[1])
        self.var_categoria.set(valores[2])
        self.var_preco.set(valores[3])
        self.var_estoque.set(valores[4])

    def _salvar(self) -> None:
        try:
            preco = float(self.var_preco.get().strip().replace(",", "."))
            estoque = int(self.var_estoque.get().strip())
        except ValueError:
            messagebox.showerror("Dados invalidos", "Preco deve ser um numero (ex: 9.90) e estoque um numero inteiro.")
            return

        try:
            if self.id_selecionado is None:
                produto = self.servico.cadastrar_produto(self.var_nome.get(), self.var_categoria.get(), preco, estoque)
                messagebox.showinfo("Sucesso", f"Produto '{produto.nome}' cadastrado com o ID {produto.id}.")
            else:
                ok = self.servico.atualizar_produto(
                    self.id_selecionado, self.var_nome.get(), self.var_categoria.get(), preco, estoque
                )
                if ok:
                    messagebox.showinfo("Sucesso", "Produto atualizado com sucesso.")
                else:
                    messagebox.showwarning("Aviso", "Nenhum produto foi atualizado. Verifique o ID.")
        except Exception as erro:
            _tratar_erro_servico(erro)
            return

        self._limpar()
        self.atualizar_lista()

    def _remover(self) -> None:
        if self.id_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um produto na lista para remover.")
            return
        if not messagebox.askyesno("Confirmar remocao", "Tem certeza que deseja remover este produto?"):
            return
        try:
            ok = self.servico.remover_produto(self.id_selecionado)
            if ok:
                messagebox.showinfo("Sucesso", "Produto removido com sucesso.")
            else:
                messagebox.showwarning("Aviso", "Nenhum produto foi removido.")
        except Exception as erro:
            _tratar_erro_servico(
                erro,
                contexto_integridade="Este produto nao pode ser removido porque ja esta associado a uma venda registrada.",
            )
            return
        self._limpar()
        self.atualizar_lista()

    def atualizar_lista(self) -> None:
        self._todos = self.servico.listar_produtos()
        self._preencher(self._todos)

    def _filtrar(self) -> None:
        termo = self.var_filtro.get().strip().lower()
        if not termo:
            self._preencher(self._todos)
            return
        filtrados = [p for p in self._todos if termo in p.nome.lower() or termo in p.categoria.lower()]
        self._preencher(filtrados)

    def _preencher(self, produtos) -> None:
        linhas = [(p.id, p.nome, p.categoria, f"{p.preco:.2f}", p.estoque) for p in produtos]
        _preencher_com_zebra(self.tabela, linhas)



# Secao de Clientes
class AbaClientes(tk.Frame):
    def __init__(self, master: tk.Widget, servico: ClienteService) -> None:
        super().__init__(master, bg=COR_FUNDO)
        self.servico = servico
        self.id_selecionado: Optional[int] = None
        self._todos: list = []
        self._montar_layout()
        self.atualizar_lista()

    def _montar_layout(self) -> None:
        painel = tk.Frame(self, bg=COR_FUNDO)
        painel.pack(fill="both", expand=True)
        painel.columnconfigure(1, weight=1)
        painel.rowconfigure(0, weight=1)

        card = _card(painel)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(card, text="Cadastro de cliente", bg=COR_CARD, fg=COR_TEXTO, font=FONTE_SECAO).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 4)
        )
        tk.Label(
            card, text="CPF pode ser digitado com ou sem mascara.",
            bg=COR_CARD, fg=COR_TEXTO_SUAVE, font=FONTE_RODAPE,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 14))

        self.var_nome = tk.StringVar()
        self.var_cpf = tk.StringVar()
        self.var_telefone = tk.StringVar()
        self.var_email = tk.StringVar()

        self._campo(card, 2, "Nome", self.var_nome)
        self._campo(card, 3, "CPF", self.var_cpf)
        self._campo(card, 4, "Telefone (opcional)", self.var_telefone)
        self._campo(card, 5, "Email (opcional)", self.var_email)

        botoes = tk.Frame(card, bg=COR_CARD)
        botoes.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(16, 22))
        botao_primario(botoes, "Salvar", self._salvar).pack(side="left", padx=(0, 6))
        botao_secundario(botoes, "Novo", self._limpar).pack(side="left", padx=(0, 6))
        botao_perigo(botoes, "Remover", self._remover).pack(side="left")

        direita = tk.Frame(painel, bg=COR_FUNDO)
        direita.grid(row=0, column=1, sticky="nsew")
        direita.rowconfigure(1, weight=1)
        direita.columnconfigure(0, weight=1)

        topo = tk.Frame(direita, bg=COR_FUNDO)
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(topo, text="Clientes cadastrados", bg=COR_FUNDO, fg=COR_TEXTO, font=FONTE_SECAO).pack(side="left")
        tk.Label(topo, text="Filtrar:", bg=COR_FUNDO, fg=COR_TEXTO_SUAVE).pack(side="left", padx=(18, 4))
        self.var_filtro = tk.StringVar()
        self.var_filtro.trace_add("write", lambda *_: self._filtrar())
        ttk.Entry(topo, textvariable=self.var_filtro, width=24).pack(side="left")
        botao_secundario(topo, "Atualizar lista", self.atualizar_lista).pack(side="right")

        lista_card = _card(direita)
        lista_card.grid(row=1, column=0, sticky="nsew")
        lista_card.rowconfigure(0, weight=1)
        lista_card.columnconfigure(0, weight=1)

        colunas = ("id", "nome", "cpf", "telefone", "email", "data")
        self.tabela = ttk.Treeview(lista_card, columns=colunas, show="headings", selectmode="browse")
        titulos = {"id": "ID", "nome": "Nome", "cpf": "CPF", "telefone": "Telefone", "email": "Email", "data": "Cadastro"}
        larguras = {"id": 45, "nome": 190, "cpf": 110, "telefone": 100, "email": 170, "data": 95}
        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, width=larguras[col], anchor="w" if col in ("nome", "email") else "center")
        _configurar_zebra(self.tabela)
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        barra = ttk.Scrollbar(lista_card, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)

    def _campo(self, card, linha, rotulo, variavel) -> ttk.Entry:
        tk.Label(card, text=rotulo, bg=COR_CARD, fg=COR_TEXTO_SUAVE, font=FONTE_BASE).grid(
            row=linha, column=0, sticky="w", padx=(20, 10), pady=6
        )
        entrada = ttk.Entry(card, textvariable=variavel, width=26)
        entrada.grid(row=linha, column=1, sticky="ew", padx=(0, 20), pady=6)
        return entrada

    def _limpar(self) -> None:
        self.id_selecionado = None
        self.var_nome.set("")
        self.var_cpf.set("")
        self.var_telefone.set("")
        self.var_email.set("")
        for item in self.tabela.selection():
            self.tabela.selection_remove(item)

    def _selecionar(self, event=None) -> None:
        selecionado = self.tabela.selection()
        if not selecionado:
            return
        valores = self.tabela.item(selecionado[0], "values")
        self.id_selecionado = int(valores[0])
        self.var_nome.set(valores[1])
        self.var_cpf.set(valores[2])
        self.var_telefone.set("" if valores[3] == "-" else valores[3])
        self.var_email.set("" if valores[4] == "-" else valores[4])

    def _salvar(self) -> None:
        try:
            if self.id_selecionado is None:
                cliente = self.servico.cadastrar_cliente(
                    self.var_nome.get(), self.var_cpf.get(), self.var_telefone.get(), self.var_email.get()
                )
                messagebox.showinfo("Sucesso", f"Cliente '{cliente.nome}' cadastrado com o ID {cliente.id}.")
            else:
                ok = self.servico.atualizar_cliente(
                    self.id_selecionado, self.var_nome.get(), self.var_cpf.get(), self.var_telefone.get(), self.var_email.get()
                )
                if ok:
                    messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso.")
                else:
                    messagebox.showwarning("Aviso", "Nenhum cliente foi atualizado. Verifique o ID.")
        except Exception as erro:
            _tratar_erro_servico(erro)
            return

        self._limpar()
        self.atualizar_lista()

    def _remover(self) -> None:
        if self.id_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um cliente na lista para remover.")
            return
        if not messagebox.askyesno("Confirmar remocao", "Tem certeza que deseja remover este cliente?"):
            return
        try:
            ok = self.servico.remover_cliente(self.id_selecionado)
            if ok:
                messagebox.showinfo("Sucesso", "Cliente removido com sucesso.")
            else:
                messagebox.showwarning("Aviso", "Nenhum cliente foi removido.")
        except Exception as erro:
            _tratar_erro_servico(
                erro,
                contexto_integridade="Este cliente nao pode ser removido porque ja possui vendas associadas.",
            )
            return
        self._limpar()
        self.atualizar_lista()

    def atualizar_lista(self) -> None:
        self._todos = self.servico.listar_clientes()
        self._preencher(self._todos)

    def _filtrar(self) -> None:
        termo = self.var_filtro.get().strip().lower()
        if not termo:
            self._preencher(self._todos)
            return
        filtrados = [c for c in self._todos if termo in c.nome.lower() or termo in (c.cpf or "")]
        self._preencher(filtrados)

    def _preencher(self, clientes) -> None:
        linhas = [(c.id, c.nome, c.cpf, c.telefone or "-", c.email or "-", c.data_cadastro) for c in clientes]
        _preencher_com_zebra(self.tabela, linhas)



# Secao de Vendas

class AbaVendas(tk.Frame):
    def __init__(
        self,
        master: tk.Widget,
        servico_venda: VendaService,
        servico_produto: ProdutoService,
        servico_cliente: ClienteService,
        app: "AplicacaoPrincipal",
    ) -> None:
        super().__init__(master, bg=COR_FUNDO)
        self.servico_venda = servico_venda
        self.servico_produto = servico_produto
        self.servico_cliente = servico_cliente
        self.app = app
        self.carrinho: list[dict] = []
        self.mapa_produtos: dict = {}
        self.mapa_clientes: dict = {}
        self._montar_layout()
        self.atualizar_combos()
        self.atualizar_lista_vendas()

    def _montar_layout(self) -> None:
        topo = _card(self)
        topo.pack(fill="x", pady=(0, 14))

        tk.Label(topo, text="Registrar nova venda", bg=COR_CARD, font=FONTE_SECAO, fg=COR_TEXTO).grid(
            row=0, column=0, columnspan=7, sticky="w", padx=20, pady=(16, 10)
        )

        tk.Label(topo, text="Cliente:", bg=COR_CARD, fg=COR_TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(20, 4))
        self.combo_cliente = ttk.Combobox(topo, state="readonly", width=28)
        self.combo_cliente.grid(row=1, column=1, sticky="w", padx=(0, 18))

        tk.Label(topo, text="Produto:", bg=COR_CARD, fg=COR_TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 4))
        self.combo_produto = ttk.Combobox(topo, state="readonly", width=34)
        self.combo_produto.grid(row=1, column=3, sticky="w", padx=(0, 18))

        tk.Label(topo, text="Qtd:", bg=COR_CARD, fg=COR_TEXTO_SUAVE).grid(row=1, column=4, sticky="w")
        self.var_quantidade = tk.StringVar(value="1")
        tk.Spinbox(topo, from_=1, to=99999, textvariable=self.var_quantidade, width=6).grid(
            row=1, column=5, sticky="w", padx=(4, 12)
        )

        botao_primario(topo, "Adicionar item", self._adicionar_item).grid(row=1, column=6, padx=(0, 20), pady=(0, 16))

        meio = tk.Frame(self, bg=COR_FUNDO)
        meio.pack(fill="both", expand=False, pady=(0, 14))

        carrinho_card = _card(meio)
        carrinho_card.pack(side="left", fill="both", expand=True)
        colunas = ("produto", "quantidade", "preco_unit", "subtotal")
        self.tabela_carrinho = ttk.Treeview(carrinho_card, columns=colunas, show="headings", height=5, selectmode="browse")
        titulos = {"produto": "Produto", "quantidade": "Quantidade", "preco_unit": "Preco unit. (R$)", "subtotal": "Subtotal (R$)"}
        for col in colunas:
            self.tabela_carrinho.heading(col, text=titulos[col])
            self.tabela_carrinho.column(col, anchor="w" if col == "produto" else "center", width=220 if col == "produto" else 150)
        _configurar_zebra(self.tabela_carrinho)
        self.tabela_carrinho.pack(fill="both", expand=True, padx=1, pady=1)

        lateral = tk.Frame(meio, bg=COR_FUNDO)
        lateral.pack(side="left", fill="y", padx=(14, 0))
        botao_perigo(lateral, "Remover item", self._remover_item).pack(fill="x", pady=(0, 12))

        total_card = tk.Frame(lateral, bg=COR_ACCENT_SUAVE, highlightbackground=COR_ACCENT, highlightthickness=1)
        total_card.pack(fill="x", pady=(0, 12))
        tk.Label(total_card, text="TOTAL DA VENDA", bg=COR_ACCENT_SUAVE, fg=COR_ACCENT, font=FONTE_RODAPE).pack(
            anchor="w", padx=14, pady=(10, 0)
        )
        self.label_total = tk.Label(total_card, text="R$ 0,00", bg=COR_ACCENT_SUAVE, fg=COR_TEXTO, font=FONTE_TOTAL)
        self.label_total.pack(anchor="w", padx=14, pady=(0, 12))

        botao_sucesso(lateral, "Finalizar venda", self._finalizar_venda).pack(fill="x")

        baixo = tk.Frame(self, bg=COR_FUNDO)
        baixo.pack(fill="both", expand=True)

        cabecalho_baixo = tk.Frame(baixo, bg=COR_FUNDO)
        cabecalho_baixo.pack(fill="x", pady=(0, 10))
        tk.Label(cabecalho_baixo, text="Vendas registradas", bg=COR_FUNDO, font=FONTE_SECAO, fg=COR_TEXTO).pack(side="left")
        botao_secundario(cabecalho_baixo, "Atualizar", self.atualizar_lista_vendas).pack(side="right")
        botao_perigo(cabecalho_baixo, "Remover venda", self._remover_venda).pack(side="right", padx=(0, 8))
        botao_secundario(cabecalho_baixo, "Ver itens", self._ver_itens).pack(side="right", padx=(0, 8))

        vendas_card = _card(baixo)
        vendas_card.pack(fill="both", expand=True)
        vendas_card.rowconfigure(0, weight=1)
        vendas_card.columnconfigure(0, weight=1)

        colunas_v = ("id", "cliente", "pagamento", "data", "total")
        self.tabela_vendas = ttk.Treeview(vendas_card, columns=colunas_v, show="headings")
        titulos_v = {"id": "ID", "cliente": "Cliente", "pagamento": "Pagamento", "data": "Data", "total": "Total (R$)"}
        larguras_v = {"id": 50, "cliente": 220, "pagamento": 150, "data": 160, "total": 110}
        for col in colunas_v:
            self.tabela_vendas.heading(col, text=titulos_v[col])
            self.tabela_vendas.column(col, width=larguras_v[col], anchor="w" if col == "cliente" else "center")
        _configurar_zebra(self.tabela_vendas)
        self.tabela_vendas.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        barra_v = ttk.Scrollbar(vendas_card, orient="vertical", command=self.tabela_vendas.yview)
        self.tabela_vendas.configure(yscrollcommand=barra_v.set)
        barra_v.grid(row=0, column=1, sticky="ns")

    def atualizar_combos(self) -> None:
        selecao_produto_atual = self.combo_produto.get()
        selecao_cliente_atual = self.combo_cliente.get()

        produtos = self.servico_produto.listar_produtos()
        self.mapa_produtos = {
            f"{p.nome} - R$ {p.preco:.2f} (estoque: {p.estoque})": p for p in produtos
        }
        self.combo_produto["values"] = list(self.mapa_produtos.keys())
        if selecao_produto_atual in self.mapa_produtos:
            self.combo_produto.set(selecao_produto_atual)
        elif self.mapa_produtos:
            self.combo_produto.current(0)
        else:
            self.combo_produto.set("")

        clientes = self.servico_cliente.listar_clientes()
        self.mapa_clientes = {"Sem cliente identificado": None}
        self.mapa_clientes.update({f"{c.nome} (CPF {c.cpf})": c.id for c in clientes})
        self.combo_cliente["values"] = list(self.mapa_clientes.keys())
        if selecao_cliente_atual in self.mapa_clientes:
            self.combo_cliente.set(selecao_cliente_atual)
        else:
            self.combo_cliente.current(0)

    def _adicionar_item(self) -> None:
        chave_produto = self.combo_produto.get()
        if not chave_produto or chave_produto not in self.mapa_produtos:
            messagebox.showwarning("Aviso", "Selecione um produto.")
            return
        try:
            quantidade = int(self.var_quantidade.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Dados invalidos", "Quantidade deve ser um numero inteiro maior que zero.")
            return

        produto = self.mapa_produtos[chave_produto]

        for item in self.carrinho:
            if item["id_produto"] == produto.id:
                item["quantidade"] += quantidade
                break
        else:
            self.carrinho.append(
                {"id_produto": produto.id, "nome": produto.nome, "quantidade": quantidade, "preco_unit": produto.preco}
            )
        self._redesenhar_carrinho()

    def _remover_item(self) -> None:
        selecionado = self.tabela_carrinho.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item do carrinho para remover.")
            return
        indice = self.tabela_carrinho.index(selecionado[0])
        del self.carrinho[indice]
        self._redesenhar_carrinho()

    def _calcular_total_carrinho(self) -> float:
        return round(sum(item["quantidade"] * item["preco_unit"] for item in self.carrinho), 2)

    def _redesenhar_carrinho(self) -> None:
        linhas = [
            (item["nome"], item["quantidade"], f"{item['preco_unit']:.2f}", f"{item['quantidade'] * item['preco_unit']:.2f}")
            for item in self.carrinho
        ]
        _preencher_com_zebra(self.tabela_carrinho, linhas)
        self.label_total.config(text=f"R$ {self._calcular_total_carrinho():.2f}")

    def _finalizar_venda(self) -> None:
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Adicione ao menos um item antes de finalizar a venda.")
            return

        total_atual = self._calcular_total_carrinho()
        forma_pagamento = abrir_dialogo_pagamento(self, total_atual)
        if forma_pagamento is None:
            return  # usuario cancelou a escolha da forma de pagamento

        chave_cliente = self.combo_cliente.get()
        id_cliente = self.mapa_clientes.get(chave_cliente)
        itens = [{"id_produto": item["id_produto"], "quantidade": item["quantidade"]} for item in self.carrinho]

        try:
            venda = self.servico_venda.registrar_venda(itens, id_cliente, forma_pagamento)
        except Exception as erro:
            _tratar_erro_servico(erro)
            return

        messagebox.showinfo(
            "Venda registrada",
            f"Venda #{venda.id_venda} registrada com sucesso!\n"
            f"Forma de pagamento: {venda.forma_pagamento}\nTotal: R$ {venda.total:.2f}",
        )
        self.carrinho.clear()
        self._redesenhar_carrinho()
        self.atualizar_combos()
        self.atualizar_lista_vendas()
        self.app.aba_produtos.atualizar_lista()

    def atualizar_lista_vendas(self) -> None:
        vendas = self.servico_venda.listar_vendas()
        clientes = {c.id: c.nome for c in self.servico_cliente.listar_clientes()}
        linhas = []
        for v in vendas:
            nome_cliente = clientes.get(v.id_cliente, "Sem cliente") if v.id_cliente else "Sem cliente"
            linhas.append((v.id_venda, nome_cliente, v.forma_pagamento, v.data_venda, f"{v.total:.2f}"))
        _preencher_com_zebra(self.tabela_vendas, linhas)

    def _venda_selecionada_id(self) -> Optional[int]:
        selecionado = self.tabela_vendas.selection()
        if not selecionado:
            return None
        valores = self.tabela_vendas.item(selecionado[0], "values")
        return int(valores[0])

    def _ver_itens(self) -> None:
        id_venda = self._venda_selecionada_id()
        if id_venda is None:
            messagebox.showwarning("Aviso", "Selecione uma venda na lista.")
            return
        try:
            itens = self.servico_venda.listar_itens_da_venda(id_venda)
            venda = self.servico_venda.buscar_venda_por_id(id_venda)
        except Exception as erro:
            _tratar_erro_servico(erro)
            return

        produtos = {p.id: p.nome for p in self.servico_produto.listar_produtos()}

        janela = tk.Toplevel(self)
        janela.title(f"Itens da venda #{id_venda}")
        janela.geometry("520x360")
        janela.configure(bg=COR_FUNDO)
        janela.transient(self.winfo_toplevel())

        tk.Label(janela, text=f"Itens da venda #{id_venda}", bg=COR_FUNDO, font=FONTE_SECAO, fg=COR_TEXTO).pack(
            anchor="w", padx=20, pady=(20, 2)
        )
        if venda is not None:
            tk.Label(
                janela, text=f"Pagamento: {venda.forma_pagamento}  |  Total: R$ {venda.total:.2f}",
                bg=COR_FUNDO, fg=COR_TEXTO_SUAVE, font=FONTE_RODAPE,
            ).pack(anchor="w", padx=20, pady=(0, 12))

        card = _card(janela)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        card.rowconfigure(0, weight=1)
        card.columnconfigure(0, weight=1)

        colunas = ("produto", "quantidade", "preco_unit", "subtotal")
        tabela = ttk.Treeview(card, columns=colunas, show="headings")
        titulos = {"produto": "Produto", "quantidade": "Qtd", "preco_unit": "Preco unit.", "subtotal": "Subtotal"}
        for col in colunas:
            tabela.heading(col, text=titulos[col])
            tabela.column(col, anchor="w" if col == "produto" else "center")
        _configurar_zebra(tabela)
        tabela.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        if not itens:
            tk.Label(janela, text="Esta venda nao possui itens.", bg=COR_FUNDO, fg=COR_TEXTO_SUAVE).pack()
        linhas = []
        for item in itens:
            nome_produto = produtos.get(item.id_produto, f"Produto #{item.id_produto}")
            subtotal = item.quantidade * item.preco_unit
            linhas.append((nome_produto, item.quantidade, f"{item.preco_unit:.2f}", f"{subtotal:.2f}"))
        _preencher_com_zebra(tabela, linhas)

    def _remover_venda(self) -> None:
        id_venda = self._venda_selecionada_id()
        if id_venda is None:
            messagebox.showwarning("Aviso", "Selecione uma venda na lista para remover.")
            return
        if not messagebox.askyesno("Confirmar remocao", f"Remover a venda #{id_venda}? Esta acao nao pode ser desfeita."):
            return
        try:
            ok = self.servico_venda.remover_venda(id_venda)
            if ok:
                messagebox.showinfo("Sucesso", "Venda removida com sucesso.")
            else:
                messagebox.showwarning("Aviso", "Nenhuma venda foi removida.")
        except Exception as erro:
            _tratar_erro_servico(
                erro,
                contexto_integridade="Esta venda nao pode ser removida porque ainda possui itens vinculados a ela.",
            )
            return
        self.atualizar_lista_vendas()



# Botao de navegacao da barra lateral
class BotaoNavegacao(tk.Frame):
    def __init__(self, master: tk.Widget, texto: str, icone: str, comando) -> None:
        super().__init__(master, bg=COR_SIDEBAR, cursor="hand2")
        self.comando = comando
        self.ativo = False

        self.indicador = tk.Frame(self, bg=COR_SIDEBAR, width=4)
        self.indicador.pack(side="left", fill="y")

        self.label = tk.Label(
            self, text=f"  {icone}   {texto}", bg=COR_SIDEBAR, fg=COR_SIDEBAR_TEXTO,
            font=FONTE_NAV, anchor="w", padx=8, pady=13,
        )
        self.label.pack(side="left", fill="both", expand=True)

        for widget in (self, self.label):
            widget.bind("<Button-1>", lambda e: self.comando())
            widget.bind("<Enter>", self._ao_entrar)
            widget.bind("<Leave>", self._ao_sair)

    def _ao_entrar(self, event=None) -> None:
        if not self.ativo:
            self.label.config(bg=COR_SIDEBAR_HOVER)
            self.config(bg=COR_SIDEBAR_HOVER)

    def _ao_sair(self, event=None) -> None:
        if not self.ativo:
            self.label.config(bg=COR_SIDEBAR)
            self.config(bg=COR_SIDEBAR)

    def marcar_ativo(self, ativo: bool) -> None:
        self.ativo = ativo
        cor = COR_SIDEBAR_ATIVO if ativo else COR_SIDEBAR
        self.config(bg=cor)
        self.label.config(bg=cor, fg="white" if ativo else COR_SIDEBAR_TEXTO)
        self.indicador.config(bg=COR_ACCENT if ativo else COR_SIDEBAR)



# Janela principal

class AplicacaoPrincipal(tk.Tk):
    def __init__(self, servicos: dict, configuracao: dict) -> None:
        super().__init__()
        self.servicos = servicos
        self.configuracao = configuracao

        self.title("Sistema de Conveniencia - Produtos, Clientes e Vendas")
        self.geometry("1220x720")
        self.minsize(1060, 640)
        self.configure(bg=COR_FUNDO)

        self._configurar_estilo()
        self._montar_layout_geral()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Treeview",
            font=FONTE_BASE,
            rowheight=28,
            background=COR_CARD,
            fieldbackground=COR_CARD,
            foreground=COR_TEXTO,
            borderwidth=0,
        )
        estilo.configure(
            "Treeview.Heading", font=FONTE_SECAO, background=COR_SECUNDARIO, foreground=COR_TEXTO,
            relief="flat", padding=8,
        )
        estilo.map("Treeview.Heading", background=[("active", COR_SECUNDARIO_HOVER)])
        estilo.map("Treeview", background=[("selected", COR_ACCENT)], foreground=[("selected", "white")])

        estilo.configure("TEntry", padding=6, relief="flat")
        estilo.configure("TCombobox", padding=6)
        estilo.configure("TScrollbar", background=COR_SECUNDARIO, troughcolor=COR_FUNDO, borderwidth=0)

    def _montar_layout_geral(self) -> None:
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True)

        # --- Barra lateral -------------------------------------------------
        sidebar = tk.Frame(corpo, bg=COR_SIDEBAR, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        cabecalho_sidebar = tk.Frame(sidebar, bg=COR_SIDEBAR)
        cabecalho_sidebar.pack(fill="x", pady=(30, 26))
        selo = tk.Frame(cabecalho_sidebar, bg=COR_ACCENT, width=40, height=40)
        selo.pack()
        selo.pack_propagate(False)
        tk.Label(selo, text="CP", bg=COR_ACCENT, fg="white", font=("Segoe UI", 12, "bold")).pack(expand=True)
        tk.Label(
            cabecalho_sidebar, text="Conveniencia\ndo Posto", bg=COR_SIDEBAR, fg="white",
            font=FONTE_TITULO_APP, justify="center",
        ).pack(pady=(10, 0))

        self.botoes_nav: dict[str, BotaoNavegacao] = {
            "produtos": BotaoNavegacao(sidebar, "Produtos", "▣", lambda: self._mostrar_secao("produtos")),
            "clientes": BotaoNavegacao(sidebar, "Clientes", "◍", lambda: self._mostrar_secao("clientes")),
            "vendas": BotaoNavegacao(sidebar, "Vendas", "▤", lambda: self._mostrar_secao("vendas")),
        }
        for botao in self.botoes_nav.values():
            botao.pack(fill="x", pady=1)

        separador = tk.Frame(sidebar, bg=COR_SIDEBAR_HOVER, height=1)
        separador.pack(fill="x", side="bottom", pady=(0, 0))
        rodape_sidebar = tk.Label(
            sidebar,
            text=(
                f"MySQL\n{self.configuracao['host']}:{self.configuracao['porta']}\n"
                f"banco '{self.configuracao['banco']}'"
            ),
            bg=COR_SIDEBAR, fg=COR_SIDEBAR_SUBTEXTO, font=FONTE_RODAPE, justify="left",
        )
        rodape_sidebar.pack(side="bottom", pady=16, padx=20, anchor="w")

        # --- Area de conteudo ------------------------------------------------
        area = tk.Frame(corpo, bg=COR_FUNDO)
        area.pack(side="left", fill="both", expand=True)

        cabecalho = tk.Frame(area, bg=COR_FUNDO)
        cabecalho.pack(fill="x", padx=30, pady=(26, 16))
        self.titulo_secao = tk.Label(cabecalho, text="", bg=COR_FUNDO, fg=COR_TEXTO, font=FONTE_TITULO_SECAO)
        self.titulo_secao.pack(anchor="w")
        self.subtitulo_secao = tk.Label(cabecalho, text="", bg=COR_FUNDO, fg=COR_TEXTO_SUAVE, font=FONTE_SUBTITULO_SECAO)
        self.subtitulo_secao.pack(anchor="w", pady=(2, 0))

        self.container_conteudo = tk.Frame(area, bg=COR_FUNDO)
        self.container_conteudo.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        self.aba_produtos = AbaProdutos(self.container_conteudo, self.servicos["produto"])
        self.aba_clientes = AbaClientes(self.container_conteudo, self.servicos["cliente"])
        self.aba_vendas = AbaVendas(
            self.container_conteudo, self.servicos["venda"], self.servicos["produto"], self.servicos["cliente"], self
        )

        self.secoes = {"produtos": self.aba_produtos, "clientes": self.aba_clientes, "vendas": self.aba_vendas}
        self.titulos_secao = {
            "produtos": ("Produtos", "Cadastro e controle de estoque"),
            "clientes": ("Clientes", "Cadastro de clientes da conveniencia"),
            "vendas": ("Vendas", "Monte o carrinho, escolha a forma de pagamento e finalize"),
        }

        self._mostrar_secao("produtos")

    def _mostrar_secao(self, nome: str) -> None:
        for frame in self.secoes.values():
            frame.pack_forget()
        self.secoes[nome].pack(fill="both", expand=True)

        for chave, botao in self.botoes_nav.items():
            botao.marcar_ativo(chave == nome)

        titulo, subtitulo = self.titulos_secao[nome]
        self.titulo_secao.config(text=titulo)
        self.subtitulo_secao.config(text=subtitulo)

        if nome == "vendas":
            self.aba_vendas.atualizar_combos()
        elif nome == "produtos":
            self.aba_produtos.atualizar_lista()
        elif nome == "clientes":
            self.aba_clientes.atualizar_lista()



# Ponto de entrada da interface

def iniciar_aplicacao() -> None:
    from src.apresentacao.fabrica_servicos import criar_servicos
    from src.config.configuracao_banco import obter_configuracao_banco
    from src.dados.conexao_singleton import ConexaoSingleton

    configuracao = obter_configuracao_banco()

    try:
        servicos = criar_servicos()
    except Exception as erro:
        _mostrar_erro_conexao(configuracao, erro)
        return

    app = AplicacaoPrincipal(servicos, configuracao)
    try:
        app.mainloop()
    finally:
        ConexaoSingleton.fechar_conexao()


def _mostrar_erro_conexao(configuracao: dict, erro: Exception) -> None:
    raiz = tk.Tk()
    raiz.withdraw()
    messagebox.showerror(
        "Nao foi possivel conectar ao MySQL",
        "Nao foi possivel conectar ao banco de dados MySQL.\n\n"
        f"Host: {configuracao['host']}:{configuracao['porta']}\n"
        f"Banco: {configuracao['banco']}\n"
        f"Usuario: {configuracao['usuario']}\n\n"
        "Verifique se o container do MySQL esta no ar. A partir da raiz do "
        "projeto, rode:\n\n"
        "    docker compose up -d\n\n"
        f"Detalhes tecnicos: {erro}",
    )
    raiz.destroy()
