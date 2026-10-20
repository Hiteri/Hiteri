import os
import logging

NOME_RELATORIO = "relatorio.txt"
NOME_LOG = "auditoria.log"

# Usa a localização deste arquivo, e não o diretório de execução.
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
PASTA_LOGS = os.path.join(PASTA_PROJETO, "logs")

CAMINHO_LOG = os.path.join(PASTA_LOGS, NOME_LOG)
CAMINHO_RELATORIO = os.path.join(PASTA_PROJETO, NOME_RELATORIO)


def preparar_ambiente():
    """Prepara os diretórios necessários para a auditoria."""
    print("Preparando ambiente...")
    os.makedirs(PASTA_LOGS, exist_ok=True)
    print("Ambiente preparado.")


def configurar_log():
    """Configura o arquivo de log da execução."""
    logging.basicConfig(
        filename=CAMINHO_LOG,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )
    logging.info("Programa iniciado.")

def deve_ignorar_arquivo(caminho):
    """Ignora os arquivos produzidos pela própria auditoria."""
    caminho = os.path.abspath(caminho)
    return caminho in {
        os.path.abspath(CAMINHO_RELATORIO),
        os.path.abspath(CAMINHO_LOG),
    }


def obter_tamanho(caminho):
    """Retorna o tamanho do arquivo em bytes."""
    try:
        return os.path.getsize(caminho)
    except OSError:
        logging.exception("Não foi possível obter o tamanho de %s", caminho)
        return 0


def analisar_diretorios():
    """
    Percorre toda a estrutura e retorna:
    quantidade, tamanho total, caminho do maior arquivo e tamanho do maior.
    """
    quantidade_arquivos = 0
    tamanho_total = 0
    maior_arquivo = ""
    maior_tamanho = 0

    logging.info("Iniciando análise dos diretórios.")

    for pasta_atual, subpastas, arquivos in os.walk(PASTA_PROJETO):
        # Mantém a contagem consistente com o verificador.
        subpastas[:] = sorted(
            pasta for pasta in subpastas if pasta != "__pycache__"
        )
        logging.info("Analisando diretório: %s", pasta_atual)

        for nome_arquivo in arquivos:
            caminho_completo = os.path.abspath(
                os.path.join(pasta_atual, nome_arquivo)
            )

            if deve_ignorar_arquivo(caminho_completo):
                continue

            tamanho = obter_tamanho(caminho_completo)
            quantidade_arquivos += 1
            tamanho_total += tamanho

            if tamanho > maior_tamanho:
                maior_tamanho = tamanho
                maior_arquivo = caminho_completo

    logging.info("Análise dos diretórios finalizada.")
    return quantidade_arquivos, tamanho_total, maior_arquivo, maior_tamanho


def validar_resultados(quantidade_arquivos, tamanho_total):
    """Verifica condições mínimas antes de gerar o relatório."""
    assert quantidade_arquivos > 0, (
        "Nenhum arquivo foi encontrado durante a auditoria."
    )
    assert tamanho_total >= 0, (
        "O tamanho total dos arquivos não pode ser negativo."
    )
    logging.info("Validações internas concluídas.")


def gerar_relatorio(
    quantidade_arquivos, tamanho_total, maior_arquivo, maior_tamanho
):
    """Grava os resultados da auditoria em um relatório novo."""
    logging.info("Gerando relatório.")

    # O modo w evita duplicar relatórios em execuções sucessivas.
    with open(CAMINHO_RELATORIO, "w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO DE AUDITORIA\n")
        arquivo.write("=" * 50 + "\n")
        arquivo.write(f"Quantidade de arquivos: {quantidade_arquivos}\n")
        arquivo.write(f"Tamanho total: {tamanho_total} bytes\n")
        arquivo.write(f"Maior arquivo: {maior_arquivo}\n")
        arquivo.write(f"Tamanho do maior arquivo: {maior_tamanho} bytes\n")
        arquivo.write("=" * 50 + "\n")

    logging.info("Relatório gerado.")


def executar_auditoria():
    """Coordena as etapas da auditoria."""
    try:
        preparar_ambiente()
        configurar_log()

        print("Analisando arquivos...")
        (
            quantidade_arquivos,
            tamanho_total,
            maior_arquivo,
            maior_tamanho,
        ) = analisar_diretorios()

        validar_resultados(quantidade_arquivos, tamanho_total)
        gerar_relatorio(
            quantidade_arquivos,
            tamanho_total,
            maior_arquivo,
            maior_tamanho,
        )

        print()
        print("Auditoria concluída.")
        print(f"Arquivos encontrados: {quantidade_arquivos}")
        print(f"Tamanho total: {tamanho_total} bytes")
        print(f"Maior arquivo: {maior_arquivo}")
        print(f"Tamanho: {maior_tamanho} bytes")
        logging.info("Programa finalizado com sucesso.")

    except Exception:
        print("Não foi possível concluir a auditoria.")
        logging.exception("Erro durante a execução.")