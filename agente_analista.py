"""
Agente Analista: diagnóstico por regras (verificáveis, com referência), panorama dos anúncios,
formulação de perguntas ao Estrategista (RAG) e redação do relatório.
"""
from __future__ import annotations

import asyncio
import json
import re
import textwrap
from collections import Counter
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from config import OPENROUTER_API_KEY, LLM_MODEL, get_llm, com_tentativas
from agente_estrategista import configurar_rag_e_consultar

N_PERGUNTAS = 5

# Referências dos limiares (citadas no artigo):
#  - Google Search Central, "Title links" e "Snippets" (tamanho de título/descrição; faixas usuais 30–60 e 70–160).
#  - Google, Core Web Vitals / Lighthouse: FCP "bom" <= 1,8 s; carregamento >3 s associado a abandono.
#  - WCAG 2.x, critério 1.1.1 (texto alternativo em imagens).
#  - Google Search Central, "Consolidate duplicate URLs" (rel=canonical).
#  - Schema.org / Google "Structured data" (rich results).
REF_GOOGLE_SNIPPETS = "Google Search Central: title links e snippets"
REF_CWV = "Google Core Web Vitals / Lighthouse"
REF_WCAG = "WCAG 2.x 1.1.1"
REF_CANONICAL = "Google Search Central: rel=canonical"
REF_SCHEMA = "Google Search Central: structured data"
REF_OG = "Open Graph Protocol / Meta Sharing Debugger"


class AgenteAnalista:
    def __init__(self, rag_query_func):
        self.problemas_identificados: List[Dict] = []
        self.oportunidades_identificadas: List[Dict] = []
        self.recomendacoes_estrategicas: List[Dict] = []
        self.panorama_anuncios: Dict[str, Any] = {}
        self.falhas: List[Dict] = []
        self.contexto: Dict[str, Any] = {}
        self.rag_query_func = rag_query_func
        self.llm = self._setup_llm()

    def _setup_llm(self):
        if not OPENROUTER_API_KEY:
            print("Agente Analista: ALERTA - OPENROUTER_API_KEY não configurada no .env.")
            return None
        try:
            llm = get_llm()
            print(f"Agente Analista: LLM pronto (modelo {LLM_MODEL}).")
            return llm
        except Exception as e:  # noqa: BLE001
            print(f"Agente Analista: ERRO - Falha ao conectar ao OpenRouter. Detalhe: {e}")
            return None

    # ------------------------------------------------------------------ fluxo
    async def analisar_dados_marketing(self, dados_seo: Dict, dados_anuncios: List[Dict],
                                       diretivas_usuario: Dict, prompt_original: str,
                                       termo_busca: str = "") -> Dict[str, Any]:
        print("\nAgente Analista")
        self.problemas_identificados, self.oportunidades_identificadas = [], []
        self.recomendacoes_estrategicas, self.falhas = [], []
        self.contexto = {
            "prompt_original": prompt_original,
            "termo_busca": termo_busca,
            "foco_analise": diretivas_usuario.get("foco_analise", []),
            "hipoteses_usuario": diretivas_usuario.get("hipoteses_usuario", []),
        }

        self._analise_primaria_seo(dados_seo)
        self._analise_primaria_anuncios(dados_anuncios)
        await self._raciocinar_e_consultar_estrategista(dados_seo, dados_anuncios, diretivas_usuario, prompt_original)

        print("Agente Analista: Análise concluída.")
        return self._gerar_relatorio_final()

    # ------------------------------------------------------------- diagnóstico
    def _problema(self, regra, categoria, problema, prioridade, referencia):
        self.problemas_identificados.append({
            "regra": regra, "categoria": categoria, "problema": problema,
            "prioridade": prioridade, "referencia": referencia,
        })

    def _analise_primaria_seo(self, dados_seo: Dict):
        if dados_seo.get("status") != "Sucesso":
            self._problema("coleta_seo", "SEO", f"Falha na coleta de dados SEO: {dados_seo.get('status')}",
                           "crítica", "-")
            return

        titulo = (dados_seo.get("titulo") or "").strip()
        if not titulo:
            self._problema("titulo_ausente", "SEO", "Título da página ausente.", "alta", REF_GOOGLE_SNIPPETS)
        elif not 30 <= len(titulo) <= 60:
            self._problema("titulo_tamanho", "SEO",
                           f"Título com {len(titulo)} caracteres (faixa recomendada: 30–60).", "média", REF_GOOGLE_SNIPPETS)

        desc = (dados_seo.get("meta_description") or "").strip()
        if not desc:
            self._problema("meta_description_ausente", "SEO", "Meta descrição ausente.", "alta", REF_GOOGLE_SNIPPETS)
        elif not 70 <= len(desc) <= 160:
            self._problema("meta_description_tamanho", "SEO",
                           f"Meta descrição com {len(desc)} caracteres (faixa recomendada: 70–160).", "média", REF_GOOGLE_SNIPPETS)

        h1 = dados_seo.get("tags_cabecalho", {}).get("h1") or []
        if not h1:
            self._problema("h1_ausente", "SEO", "Nenhuma tag H1 encontrada.", "alta", REF_GOOGLE_SNIPPETS)
        elif len(h1) > 1:
            self._problema("h1_multiplo", "SEO", f"{len(h1)} tags H1 na página (recomenda-se uma).", "baixa", REF_GOOGLE_SNIPPETS)

        palavras = dados_seo.get("contagem_palavras", 0)
        if palavras < 300:
            self._problema("conteudo_curto", "Conteúdo",
                           f"Conteúdo principal com apenas {palavras} palavras (< 300).", "média", "prática de SEO on-page")

        sem_alt = dados_seo.get("imagens_sem_alt") or []
        if sem_alt:
            self._problema("imagens_sem_alt", "Acessibilidade/SEO",
                           f"{len(sem_alt)} imagem(ns) sem atributo alt.", "média", REF_WCAG)

        canonical = (dados_seo.get("canonical_url") or "").strip()
        if not canonical:
            self._problema("canonical_ausente", "SEO", "URL canônica não declarada.", "baixa", REF_CANONICAL)
        else:
            host_pagina = urlparse(dados_seo.get("url", "")).netloc.replace("www.", "")
            host_canon = urlparse(canonical).netloc.replace("www.", "")
            if host_pagina and host_canon and host_pagina != host_canon:
                self._problema("canonical_outro_dominio", "SEO",
                               f"URL canônica aponta para outro domínio ({host_canon}); o site pode ceder a indexação a ele.",
                               "alta", REF_CANONICAL)

        if not dados_seo.get("open_graph"):
            self._problema("open_graph_ausente", "Redes sociais",
                           "Sem marcações Open Graph (prévia ao compartilhar links).", "baixa", REF_OG)

        if not dados_seo.get("structured_data"):
            self._problema("dados_estruturados_ausentes", "SEO",
                           "Sem dados estruturados (JSON-LD), o que limita rich results.", "baixa", REF_SCHEMA)

        perf = dados_seo.get("performance_metrics") or {}
        fcp_ms = perf.get("first_contentful_paint") or 0
        if fcp_ms > 1800:
            self._problema("fcp_lento", "Performance",
                           f"First Contentful Paint de {fcp_ms / 1000:.1f} s (limiar 'bom': 1,8 s).", "alta", REF_CWV)
        elif dados_seo.get("tempo_carregamento", 0) > 3:
            self._problema("carregamento_lento", "Performance",
                           f"Evento load em {dados_seo.get('tempo_carregamento')} s (> 3 s).", "alta", REF_CWV)

        if not dados_seo.get("mobile_friendly"):
            self._problema("sem_viewport_mobile", "Usabilidade",
                           "Sem meta viewport (indício de página não adaptada a dispositivos móveis).", "alta", REF_CWV)

    def _analise_primaria_anuncios(self, dados_anuncios: List[Dict]):
        anuncios = dados_anuncios if isinstance(dados_anuncios, list) else []
        n = len(anuncios)

        def validos(chave):
            return [a.get(chave) for a in anuncios if a.get(chave) not in (None, "", "Não encontrado", "Não especificado")]

        tipos = Counter(validos("tipo_criativo"))
        ctas = Counter(validos("cta"))
        self.panorama_anuncios = {
            "total_coletado": n,
            "criativos": dict(tipos),
            "proporcao_video": round(tipos.get("Vídeo", 0) / n, 2) if n else None,
            "ctas_mais_comuns": ctas.most_common(5),
            "anuncios_com_data_inicio": len(validos("data_inicio")),
            "amostra_textos": [(a.get("texto") or "")[:200].replace("\n", " ") for a in anuncios[:5]],
            "observacao": "Recorte da Biblioteca de Anúncios da Meta para o termo informado; não representa todo o setor.",
        }

        if n == 0:
            self.oportunidades_identificadas.append({
                "categoria": "Publicidade",
                "oportunidade": "Nenhum anúncio ativo encontrado para o termo; indício de baixa concorrência paga no recorte.",
                "potencial": "alto",
            })
        elif n < 25:
            self.oportunidades_identificadas.append({
                "categoria": "Publicidade",
                "oportunidade": f"Baixa concorrência no recorte ({n} anúncios ativos, limiar 25); espaço para se destacar.",
                "potencial": "alto",
            })
        if n and tipos and tipos.get("Vídeo", 0) / n >= 0.6:
            self.oportunidades_identificadas.append({
                "categoria": "Criativos",
                "oportunidade": f"{tipos.get('Vídeo', 0)} de {n} anúncios concorrentes usam vídeo; o formato é a norma no recorte.",
                "potencial": "médio",
            })

    # ---------------------------------------------------------- perguntas/RAG
    async def _raciocinar_e_consultar_estrategista(self, dados_seo, dados_anuncios, diretivas_usuario, prompt_original):
        if not self.llm:
            print("Agente Analista: LLM indisponível.")
            self.falhas.append({"etapa": "llm_indisponivel"})
            return

        hipoteses = diretivas_usuario.get("hipoteses_usuario") or []
        resumo_caso = textwrap.dedent(f"""
            Resumo do caso
            - URL analisada: {dados_seo.get('url')}
            - Contexto informado pelo gestor: "{prompt_original}"
            - Foco identificado pelo Intérprete: {diretivas_usuario.get('foco_analise', [])}
            - Hipóteses/dúvidas do gestor (extraídas pelo Intérprete): {hipoteses or 'nenhuma'}

            Diagnóstico por regras (características verificáveis da página):
        """)
        for p in self.problemas_identificados:
            resumo_caso += f"- [{p['prioridade']}] {p['categoria']}: {p['problema']}\n"
        if not self.problemas_identificados:
            resumo_caso += "- Nenhum problema apontado pelas regras.\n"
        resumo_caso += "\nOportunidades:\n" + "".join(
            f"- {o['categoria']}: {o['oportunidade']}\n" for o in self.oportunidades_identificadas)
        resumo_caso += "\nPanorama dos anúncios concorrentes coletados:\n" + json.dumps(
            self.panorama_anuncios, ensure_ascii=False, indent=2)

        prompt_template = textwrap.dedent(f"""
            Você é um Analista de Marketing Digital Sênior.
            Formule {N_PERGUNTAS} perguntas investigativas para um Agente Estrategista que consulta uma base
            de conhecimento de marketing digital (RAG). As respostas vão fundamentar o plano de ação da empresa.

            REGRAS:
            1. Perguntas específicas ao nicho, à localidade e ao contexto informado — nada genérico.
            2. Pelo menos duas perguntas devem responder diretamente às hipóteses/dúvidas do gestor, se houver.
            3. Pelo menos uma pergunta deve partir de um problema do diagnóstico ou do panorama dos anúncios.
            4. Busque ações práticas, viáveis para uma PME.
            5. Retorne APENAS uma lista JSON de {N_PERGUNTAS} strings.

            {resumo_caso}
        """)

        def gerar_perguntas():
            raw_text = str(self.llm.complete(prompt_template)).strip()
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            perguntas = json.loads(match.group(0) if match else raw_text)
            if not isinstance(perguntas, list) or not all(isinstance(p, str) for p in perguntas):
                raise ValueError("resposta não é uma lista JSON de strings")
            return perguntas[:N_PERGUNTAS]

        try:
            perguntas = com_tentativas(gerar_perguntas, rotulo="Agente Analista (perguntas)")
            print(f"Agente Analista - {len(perguntas)} perguntas geradas: {perguntas}")
        except Exception as e:  # noqa: BLE001
            print(f"Agente Analista - ERRO ao gerar perguntas após tentativas: {e}")
            self.falhas.append({"etapa": "geracao_perguntas", "erro": str(e)})
            return

        # Consultas ao Estrategista em paralelo (antes eram sequenciais).
        respostas = await asyncio.gather(*(self.rag_query_func(p) for p in perguntas), return_exceptions=True)
        for pergunta, resposta_rag in zip(perguntas, respostas):
            if isinstance(resposta_rag, Exception):
                print(f"Agente Analista - ERRO ao consultar RAG para '{pergunta[:60]}...': {resposta_rag}")
                self.falhas.append({"etapa": "consulta_rag", "pergunta": pergunta, "erro": str(resposta_rag)})
                continue
            if isinstance(resposta_rag, dict):
                texto, fontes = resposta_rag.get("texto", ""), resposta_rag.get("fontes", [])
            else:
                texto, fontes = str(resposta_rag), []
            self.recomendacoes_estrategicas.append({
                "pergunta": pergunta,
                "recomendacao": texto,
                "fontes": sorted({f["arquivo"] for f in fontes}),
                "fontes_detalhe": fontes,
            })

    # --------------------------------------------------------------- saídas
    def _gerar_relatorio_final(self) -> Dict[str, Any]:
        return {
            "resumo_executivo": (f"Análise concluída. {len(self.problemas_identificados)} problema(s), "
                                 f"{len(self.oportunidades_identificadas)} oportunidade(s) e "
                                 f"{len(self.recomendacoes_estrategicas)} recomendação(ões)."),
            "contexto": self.contexto,
            "problemas_identificados": self.problemas_identificados,
            "oportunidades_identificadas": self.oportunidades_identificadas,
            "panorama_anuncios": self.panorama_anuncios,
            "recomendacoes_estrategicas": self.recomendacoes_estrategicas,
            "falhas_tratadas": self.falhas,
        }

    async def gerar_relatorio_formatado_txt(self) -> str:
        print("\nAgente Analista - Gerando relatório formatado.")
        if not self.llm:
            return "ERRO: Cliente LLM indisponível."

        dados = self._gerar_relatorio_final()
        dados_prompt = {k: v for k, v in dados.items() if k not in ("falhas_tratadas", "resumo_executivo")}
        dados_prompt["recomendacoes_estrategicas"] = [
            {k: v for k, v in r.items() if k != "fontes_detalhe"} for r in dados["recomendacoes_estrategicas"]]

        prompt_relatorio = textwrap.dedent(f"""
            Você é um consultor que escreve relatórios de marketing digital para gestores de PMEs sem
            formação em marketing. Transforme o JSON abaixo em um relatório em Markdown, em português.

            Estrutura obrigatória (use exatamente estes títulos):
            ## 1. RESUMO EXECUTIVO
            ## 2. PROBLEMAS IDENTIFICADOS
            ## 3. OPORTUNIDADES (Volume de anúncios)
            ## 4. PLANO DE AÇÃO ESTRATÉGICO

            Regras:
            - Resumo executivo: 4–6 frases que respondam ao contexto informado pelo gestor, dizendo o que foi
              encontrado e quais são as três ações prioritárias. Não copie contagens mecânicas.
            - Problemas: um item por problema, com prioridade e referência do critério. Se não houver, diga
              o que está adequado.
            - Oportunidades: apresente também o panorama dos anúncios concorrentes (formatos, CTAs).
            - Plano de ação: uma subseção (### 4.x Título curto) por recomendação, com exatamente estes campos
              em negrito, cada um em 1–3 frases:
              **Ação:** o que fazer. **Evidência:** qual dado do diagnóstico, do panorama de anúncios ou do
              contexto motiva a ação. **Como executar:** passos concretos. **Prioridade:** alta/média/baixa.
              **Esforço:** baixo/médio/alto para uma equipe pequena. **Fontes:** os nomes de arquivo do campo
              "fontes" (ou "não recuperadas").
            - Use somente informações do JSON; não invente números nem dados.
            - Linguagem direta, sem jargão não explicado.

            Dados:
            {json.dumps(dados_prompt, indent=2, ensure_ascii=False)}
        """)
        try:
            resposta_llm = com_tentativas(lambda: self.llm.complete(prompt_relatorio),
                                          rotulo="Agente Analista (relatório)")
            print("Agente Analista - Relatório formatado gerado.")
            return str(resposta_llm).strip()
        except Exception as e:  # noqa: BLE001
            print(f"Agente Analista - ERRO ao gerar relatório: {e}")
            self.falhas.append({"etapa": "relatorio", "erro": str(e)})
            return f"ERRO ao gerar relatório: {e}"


async def analisar_marketing_digital(dados_seo: Dict, dados_anuncios: List[Dict],
                                     diretivas_usuario: Dict, prompt_original: str,
                                     termo_busca: str = "") -> Tuple[Dict[str, Any], "AgenteAnalista"]:
    analista = AgenteAnalista(rag_query_func=configurar_rag_e_consultar)
    resultado = await analista.analisar_dados_marketing(dados_seo, dados_anuncios, diretivas_usuario,
                                                        prompt_original, termo_busca)
    return resultado, analista
