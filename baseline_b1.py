"""
Baseline B1: um único LLM, sem agentes, sem regras e sem RAG.

Recebe EXATAMENTE os mesmos dados coletados (SEO on-page e anúncios) e o mesmo prompt do
usuário de uma execução do sistema, e produz um relatório com a mesma estrutura de seções.
Serve para responder à pergunta: o que a arquitetura multiagente + RAG acrescenta?

Uso:
  python baseline_b1.py --dados resultados/A/sistema/execucao.json --saida resultados/A/b1
"""
from __future__ import annotations

import argparse
import json
import os
import textwrap
import time
from datetime import datetime
from typing import Any, Dict

from config import LLM_MODEL, LLM_TIMEOUT, get_openai_client, com_tentativas, uso_da_chave_usd

ESTRUTURA = """## 1. RESUMO EXECUTIVO
## 2. PROBLEMAS IDENTIFICADOS
## 3. OPORTUNIDADES (Volume de anúncios)
## 4. PLANO DE AÇÃO ESTRATÉGICO"""


def _resumir_anuncios(anuncios, limite=40):
    """Mantém o volume de tokens sob controle sem esconder informação relevante."""
    if not isinstance(anuncios, list):
        return {"total": 0, "amostra": []}
    campos = ("texto", "tipo_criativo", "plataformas", "data_inicio", "cta")
    amostra = [{k: a.get(k) for k in campos if k in a} for a in anuncios[:limite]]
    return {"total": len(anuncios), "amostra": amostra}


def montar_prompt(url: str, termo: str, prompt_usuario: str, dados: Dict[str, Any]) -> str:
    seo = dados.get("seo", {})
    anuncios = _resumir_anuncios(dados.get("anuncios", []))
    return textwrap.dedent(f"""
        Você é um consultor de marketing digital para pequenas e médias empresas.

        Uma PME pediu uma análise. Contexto informado pela empresa:
        "{prompt_usuario}"

        Site analisado: {url}
        Termo usado para consultar anúncios ativos na Biblioteca de Anúncios da Meta (Brasil): "{termo}"

        DADOS COLETADOS DO SITE (SEO on-page e desempenho, medidos automaticamente):
        {json.dumps(seo, indent=2, ensure_ascii=False)}

        ANÚNCIOS ATIVOS ENCONTRADOS PARA O TERMO:
        {json.dumps(anuncios, indent=2, ensure_ascii=False)}

        PAGESPEED INSIGHTS / LIGHTHOUSE (notas 0-100 e Core Web Vitals; "campo" = usuários reais):
        {json.dumps({k: (dados.get("pagespeed") or {}).get(k) for k in ("status", "estrategia", "categorias", "laboratorio", "campo")}, indent=2, ensure_ascii=False)}

        Escreva um relatório em Markdown, em português, para um gestor sem formação em marketing,
        com exatamente estas seções:
        {ESTRUTURA}

        Regras:
        - Resumo executivo: 4–6 frases que respondam ao contexto informado, dizendo o que foi encontrado
          e quais são as três ações prioritárias.
        - Problemas: um item por problema que você identificar nos dados, com prioridade. Se não houver,
          diga o que está adequado.
        - Oportunidades: considere o volume e o perfil dos anúncios concorrentes.
        - Plano de ação: cinco recomendações, uma subseção (### 4.x Título curto) cada, com exatamente
          estes campos em negrito, cada um em 1–3 frases: **Ação:** **Evidência:** (qual dado ou parte do
          contexto motiva a ação) **Como executar:** **Prioridade:** alta/média/baixa **Esforço:**
          baixo/médio/alto **Fontes:** (referências em que se apoia, ou "não informadas").
        - Baseie-se nos dados acima e no contexto da empresa; não invente números.
        - Linguagem direta, sem jargão não explicado.
    """).strip()


def executar_baseline(url: str, termo: str, prompt_usuario: str, dados_coletados: Dict[str, Any],
                      modelo: str = None) -> Dict[str, Any]:
    modelo = modelo or LLM_MODEL
    client = get_openai_client()
    prompt = montar_prompt(url, termo, prompt_usuario, dados_coletados)

    custo_inicial = uso_da_chave_usd()
    inicio = time.perf_counter()
    resposta = com_tentativas(lambda: client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        timeout=LLM_TIMEOUT,
    ), rotulo="Baseline B1")
    duracao = time.perf_counter() - inicio
    custo_final = uso_da_chave_usd()

    texto = resposta.choices[0].message.content.strip()
    uso = getattr(resposta, "usage", None)
    return {
        "metadados": {
            "condicao": "B1_llm_unico",
            "url_analisada": url,
            "termo_busca": termo,
            "prompt_usuario": prompt_usuario,
            "modelo_llm": modelo,
            "timestamp_analise": datetime.now().isoformat(),
        },
        "dados_coletados": dados_coletados,
        "relatorio_formatado": texto,
        "execucao": {
            "tempos_s": {"total": round(duracao, 2)},
            "tokens_prompt": getattr(uso, "prompt_tokens", None),
            "tokens_resposta": getattr(uso, "completion_tokens", None),
            "custo_usd": (round(custo_final - custo_inicial, 4)
                          if custo_inicial is not None and custo_final is not None else None),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Baseline B1 (LLM único)")
    parser.add_argument("--dados", required=True, help="execucao.json de uma execução do sistema")
    parser.add_argument("--saida", required=True, help="pasta de saída")
    parser.add_argument("--modelo", default=None, help="sobrescreve LLM_MODEL")
    args = parser.parse_args()

    with open(args.dados, encoding="utf-8") as f:
        exec_sistema = json.load(f)
    meta = exec_sistema["metadados"]
    resultado = executar_baseline(meta["url_analisada"], meta["termo_busca"], meta["prompt_usuario"],
                                  exec_sistema["dados_coletados"], args.modelo)

    os.makedirs(args.saida, exist_ok=True)
    with open(os.path.join(args.saida, "execucao.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    with open(os.path.join(args.saida, "relatorio.md"), "w", encoding="utf-8") as f:
        f.write(resultado["relatorio_formatado"])
    print(f"B1 concluído em {resultado['execucao']['tempos_s']['total']}s; salvo em {args.saida}/")


if __name__ == "__main__":
    main()
