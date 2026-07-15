from src.config.configuracao_banco import obter_configuracao_banco
from src.dados.cliente_repository import ClienteRepository
from src.dados.conexao_singleton import ConexaoSingleton
from src.dados.itensvenda_repository import ItensVendaRepository
from src.dados.produto_repository import ProdutoRepository
from src.dados.vendas_repository import VendasRepository
from src.negocio.cliente_service import ClienteService
from src.negocio.produto_service import ProdutoService
from src.negocio.venda_service import VendaService


def criar_servicos() -> dict:
    """
    Monta a cadeia conexao -> repositorio -> servico para cada entidade,
    reaproveitando a mesma conexao (Singleton) durante toda a vida da aplicacao.
    """
    configuracao = obter_configuracao_banco()
    conexao = ConexaoSingleton.obter_conexao(**configuracao)

    repositorio_produto = ProdutoRepository(conexao)
    repositorio_cliente = ClienteRepository(conexao)
    repositorio_venda = VendasRepository(conexao)
    repositorio_item = ItensVendaRepository(conexao)

    servico_produto = ProdutoService(repositorio_produto)
    servico_cliente = ClienteService(repositorio_cliente)
    servico_venda = VendaService(repositorio_venda, repositorio_item, repositorio_produto)

    return {
        "produto": servico_produto,
        "cliente": servico_cliente,
        "venda": servico_venda,
    }
