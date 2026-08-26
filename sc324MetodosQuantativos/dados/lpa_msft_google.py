# -*- coding: utf-8 -*-
"""
EPS basico trimestral pelo EDGAR da SEC - Microsoft e Google/Alphabet
Fonte primaria e gratuita. De 2010 ate o periodo mais recente.

Ideia de aula
    O EPS que aparece no Refinitiv ou no Yahoo nasce dos formularios
    10-Q e 10-K entregues no EDGAR. Aqui vamos direto na fonte, pela API
    XBRL de dados da empresa (companyconcept), e comparamos com o Refinitiv.

Como funciona
    A SEC publica cada fato contabil marcado em XBRL. O EPS basico usa a
    etiqueta us-gaap:EarningsPerShareBasic, na unidade USD/shares. Cada
    registro tem inicio e fim de periodo. O trimestre isolado tem duracao
    perto de 90 dias. O acumulado de meio ano tem perto de 180. O ano
    inteiro tem perto de 365. Filtramos pela duracao para pegar o trimestre.

Regras de uso justo da SEC
    Toda requisicao precisa de um cabecalho User-Agent com nome e e-mail.
    O limite e de dez requisicoes por segundo. Baixe so o necessario.
    Referencia em https://www.sec.gov/about/developer-resources

Requisitos
    pip install requests pandas openpyxl
"""

import time
from datetime import date

import requests
import pandas as pd


# ----------------------------------------------------------------------
# 1) CONFIGURACAO - o aluno precisa preencher o contato
#    A SEC recusa (erro 403) requisicoes sem um contato valido.
# ----------------------------------------------------------------------
CONTATO = "Claudio Barros marceloedwards@ufpr.br"   # troque pelo seu nome e e-mail real

ANO_INICIAL = 2010

# Uma empresa pode ter mais de um CIK ao longo do tempo.
# O Google Inc (CIK 1288776) cobre ate 2015. A Alphabet (CIK 1652044)
# assume a partir da reorganizacao de 2015. Unimos os dois para chegar a 2010.
EMPRESAS = {
    "Microsoft": ["0000789019"],
    "Google/Alphabet": ["0001288776", "0001652044"],
}

# Etiquetas candidatas de EPS basico, em ordem de tentativa.
TAGS_EPS_BASICO = ["EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"]

PAUSA_SEGUNDOS = 0.5          # respeita o limite de dez por segundo com folga
ARQUIVO_SAIDA = "EPS_trimestral_EDGAR_MSFT_GOOGL.xlsx"

SESSAO = requests.Session()
SESSAO.headers.update({"User-Agent": CONTATO, "Accept-Encoding": "gzip, deflate"})


# ----------------------------------------------------------------------
# 2) Acesso a API com controle de ritmo e novas tentativas
# ----------------------------------------------------------------------
def baixar_conceito(cik, tag, tentativas=4):
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
    for tentativa in range(1, tentativas + 1):
        resposta = SESSAO.get(url, timeout=30)
        if resposta.status_code == 200:
            return resposta.json()
        if resposta.status_code == 404:
            return None   # a etiqueta nao existe para este CIK
        if resposta.status_code in (403, 429, 500, 503):
            espera = PAUSA_SEGUNDOS * (2 ** tentativa)
            print(f"  status {resposta.status_code} em {cik}/{tag}. "
                  f"Nova tentativa em {espera:.1f}s")
            time.sleep(espera)
            continue
        resposta.raise_for_status()
    return None


def registros_eps(cik):
    """Retorna a lista de fatos de EPS basico de um CIK, testando as etiquetas."""
    for tag in TAGS_EPS_BASICO:
        dado = baixar_conceito(cik, tag)
        time.sleep(PAUSA_SEGUNDOS)
        if not dado:
            continue
        unidades = dado.get("units", {})
        chave = "USD/shares" if "USD/shares" in unidades else next(iter(unidades), None)
        if not chave:
            continue
        linhas = []
        for item in unidades[chave]:
            if item.get("start") and item.get("end"):
                linhas.append({
                    "cik": cik, "tag": tag,
                    "inicio": item["start"], "fim": item["end"],
                    "valor": item.get("val"),
                    "fy": item.get("fy"), "fp": item.get("fp"),
                    "form": item.get("form"), "filed": item.get("filed"),
                    "frame": item.get("frame"),
                })
        if linhas:
            print(f"  CIK {cik}: {len(linhas)} registros na etiqueta {tag}")
            return linhas
    print(f"  CIK {cik}: nenhum registro de EPS basico encontrado")
    return []


# ----------------------------------------------------------------------
# 3) Tratamento - separa trimestre isolado e ano inteiro pela duracao
# ----------------------------------------------------------------------
def preparar(df):
    df = df.copy()
    df["inicio"] = pd.to_datetime(df["inicio"], errors="coerce")
    df["fim"] = pd.to_datetime(df["fim"], errors="coerce")
    df["filed"] = pd.to_datetime(df["filed"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["inicio", "fim", "valor"])
    df["dias"] = (df["fim"] - df["inicio"]).dt.days
    return df


def trimestres_isolados(df):
    """Periodos com duracao perto de 90 dias sao trimestres isolados."""
    tri = df[(df["dias"] >= 80) & (df["dias"] <= 100)].copy()
    # remove repeticoes do mesmo trimestre vindas de arquivos diferentes
    tri = tri.sort_values("filed").drop_duplicates(subset=["fim"], keep="first")
    return tri.sort_values("fim")


def anuais(df):
    """Periodos com duracao perto de 365 dias sao o ano fiscal."""
    ano = df[(df["dias"] >= 350) & (df["dias"] <= 380)].copy()
    ano = ano.sort_values("filed").drop_duplicates(subset=["fim"], keep="first")
    return ano.sort_values("fim")


def derivar_quarto_trimestre(tri, ano):
    """
    O EDGAR nao traz um Q4 isolado. As empresas reportam o ano inteiro no
    10-K. Aqui estimamos o Q4 como EPS anual menos a soma dos tres primeiros
    trimestres do mesmo ano fiscal. E uma aproximacao, porque o numero medio
    de acoes muda entre os periodos. O valor vem marcado como estimado.
    """
    if tri.empty or ano.empty:
        return pd.DataFrame(columns=tri.columns)
    soma_tres = tri.groupby("fy")["valor"].sum()
    linhas_q4 = []
    for _, linha in ano.iterrows():
        fy = linha["fy"]
        if fy in soma_tres.index:
            q4 = linha["valor"] - soma_tres.loc[fy]
            linhas_q4.append({
                "cik": linha["cik"], "tag": linha["tag"],
                "inicio": pd.NaT, "fim": linha["fim"], "valor": q4,
                "fy": fy, "fp": "Q4(estimado)", "form": linha["form"],
                "filed": linha["filed"], "frame": None, "dias": None,
            })
    return pd.DataFrame(linhas_q4)


# ----------------------------------------------------------------------
# 4) Coleta por empresa (une os CIKs) e monta a serie
# ----------------------------------------------------------------------
def coletar_empresa(nome, ciks):
    print(f"\nColetando {nome}")
    brutos = []
    for cik in ciks:
        brutos.extend(registros_eps(cik))
    if not brutos:
        return pd.DataFrame()

    df = preparar(pd.DataFrame(brutos))
    tri = trimestres_isolados(df)
    ano = anuais(df)
    q4 = derivar_quarto_trimestre(tri, ano)

    serie = pd.concat([tri, q4], ignore_index=True)
    serie = serie[serie["fim"].dt.year >= ANO_INICIAL].copy()
    serie["Empresa"] = nome
    serie["Ano"] = serie["fim"].dt.year
    serie["Trimestre_calendario"] = serie["fim"].dt.quarter
    return serie.sort_values("fim")


def main():
    if "nome@dominio.com" in CONTATO:
        raise SystemExit(
            "Preencha a variavel CONTATO com seu nome e e-mail reais. "
            "A SEC exige isso para liberar o acesso."
        )

    print(f"EDGAR companyconcept - EPS basico trimestral")
    print(f"Janela a partir de {ANO_INICIAL} ate {date.today().isoformat()}")

    partes = [coletar_empresa(nome, ciks) for nome, ciks in EMPRESAS.items()]
    dados = pd.concat([p for p in partes if not p.empty], ignore_index=True)
    if dados.empty:
        raise RuntimeError("Nenhum dado retornou. Confira o CONTATO e a conexao.")

    # Tabela larga - uma coluna por empresa, indexada pela data de fim de periodo
    serie = dados.pivot_table(
        index="fim", columns="Empresa", values="valor", aggfunc="last"
    ).sort_index()
    serie.index.name = "Data de fim de periodo"
    ordem = [n for n in EMPRESAS.keys() if n in serie.columns]
    serie = serie[ordem]

    print("\nPrevia dos ultimos 12 periodos")
    print(serie.tail(12))

    # Exportacao
    brutos_export = dados[[
        "Empresa", "cik", "fim", "Ano", "Trimestre_calendario",
        "fp", "form", "filed", "valor"
    ]].rename(columns={"fim": "Data de fim de periodo", "valor": "EPS basico"})

    try:
        with pd.ExcelWriter(ARQUIVO_SAIDA, engine="openpyxl") as escritor:
            serie.to_excel(escritor, sheet_name="EPS trimestral")
            brutos_export.to_excel(escritor, sheet_name="dados_brutos", index=False)
        print(f"\nArquivo salvo em {ARQUIVO_SAIDA}")
    except Exception as erro:
        alternativo = ARQUIVO_SAIDA.replace(".xlsx", ".csv")
        serie.to_csv(alternativo)
        print(f"\nExcel indisponivel ({erro}). Serie salva em {alternativo}")

    print(
        "\nAviso importante para a comparacao com o Refinitiv\n"
        "  O EDGAR traz o EPS como foi reportado na epoca, sem ajuste por\n"
        "  desdobramento de acoes. O Google desdobrou em 2014 e 2022, entao\n"
        "  os valores antigos aqui vem em base nao ajustada e ficarao maiores\n"
        "  que os do Refinitiv, que costuma vir ajustado. O Q4 vem estimado\n"
        "  pela diferenca entre o ano e os tres primeiros trimestres."
    )
    return serie


if __name__ == "__main__":
    serie_eps = main()