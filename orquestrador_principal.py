from __future__ import annotations
import argparse
import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any

from config import OPENROUTER_API_KEY, LLM_MODEL, EMBED_MODEL, uso_da_chave_usd
from agente_interprete import interpretar_prompt_usuario
from agente_analista import analisar_marketing_digital, AgenteAnalista
from agente_coletor_meta import coletar_anuncios_meta
from agente_arquiteto import analisar_seo_on_page
from agente_pagespeed import coletar_pagespeed

VERSAO_ORQUESTRADOR = "3.3"

if not OPENROUTER_API_KEY:
    raise EnvironmentError(
        "ERRO: Variável OPENROUTER_API_KEY não encontrada no .env. "
        "Crie um arquivo .env na raiz com:\n"
        "OPENROUTER_API_KEY=sua_chave_aqui\n"
        "OPENROUTER_API_BASE=https://openrouter.ai/api/v1"
    )

class OrquestradorPrincipal:
    """
    Coordena o fluxo completo de análise:
    1. Interpretação do prompt do usuário (Agente Intérprete)
    2. Coleta de dados SEO e anúncios (Agentes Coletor e Arquiteto)
    3. Análise inteligente via LLM (Agente Analista)
    """

    def __init__(self):
        self.dados_coletados: Dict[str, Any] = {}
        self.resultados_analise: Dict[str, Any] = {}
        self.relatorio_final: Dict[str, Any] = {}
        self.diretivas_usuario: Dict[str, Any] = {}
        self.agente_analista_instance: AgenteAnalista | None = None
        self.tempos: Dict[str, float] = {}   # duração (s) de cada etapa

    def __interpretacao(self, prompt_usuario: str) -> Dict[str, Any]:
        """Interpreta o prompt do usuário com o Agente Intérprete."""
        print("\nINTERPRETAÇÃO DA INTENÇÃO DO USUÁRIO")

        diretivas = interpretar_prompt_usuario(prompt_usuario)
        print(f"Diretivas geradas: {diretivas}")
        return diretivas

    async def __coleta_dados(self, url: str, termo_busca: str):
        """Coordena a coleta de dados pelos agentes especializados."""
        print("\nCOLETA DE DADOS")

        eh_perfil_social = "instagram.com" in url.lower()
        resultados = await asyncio.gather(
            analisar_seo_on_page(url),
            coletar_anuncios_meta(termo_busca),
            coletar_pagespeed(url) if not eh_perfil_social else asyncio.sleep(0, result={"status": "nao_aplicavel"}),
            return_exceptions=True
        )

        dados_seo, dados_anuncios, dados_pagespeed = resultados
        if isinstance(dados_pagespeed, Exception):
            print(f"Erro na coleta PageSpeed: {dados_pagespeed}")
            dados_pagespeed = {"status": f"Erro: {dados_pagespeed}"}

        if isinstance(dados_seo, Exception):
            print(f"Erro na coleta SEO: {dados_seo}")
            dados_seo = {"status": f"Erro: {dados_seo}", "url": url}

        if isinstance(dados_anuncios, Exception):
            print(f"Erro na coleta de anúncios: {dados_anuncios}")
            dados_anuncios = []

        self.dados_coletados = {
            "seo": dados_seo,
            "anuncios": dados_anuncios,
            "pagespeed": dados_pagespeed,
        }

        print(f"Coleta concluída: SEO ({dados_seo.get('status', 'OK')}), "
              f"Anúncios ({len(dados_anuncios) if isinstance(dados_anuncios, list) else 0})")

    async def __analise_(self, termo_busca: str, prompt_usuario: str):
        """Realiza a análise com o Agente Analista."""
        print("\nANÁLISE")

        try:
            self.resultados_analise, self.agente_analista_instance = await analisar_marketing_digital(
                dados_seo=self.dados_coletados.get("seo", {}),
                dados_anuncios=self.dados_coletados.get("anuncios", []),
                diretivas_usuario=self.diretivas_usuario,
                prompt_original=prompt_usuario,
                termo_busca=termo_busca,
                dados_pagespeed=self.dados_coletados.get("pagespeed", {})
            )
            print("Análise concluída com sucesso.")
        except Exception as e:
            print(f"Erro no Agente Analista: {e}")
            self.resultados_analise = {"status": "erro", "erro": str(e)}
            self.agente_analista_instance = None

    async def __relatorio_final(self, url: str, termo_busca: str, prompt_usuario: str):
        """Gera o relatório final."""
        print("\nRELATÓRIO")

        relatorio_formatado = "Geração de relatório falhou devido a erro anterior."

        if self.agente_analista_instance:
            relatorio_formatado = await self.agente_analista_instance.gerar_relatorio_formatado_txt()

        self.relatorio_final = {
            "metadados": {
                "url_analisada": url,
                "termo_busca": termo_busca,
                "prompt_usuario": prompt_usuario,
                "diretivas_interpretadas": self.diretivas_usuario,
                "timestamp_analise": datetime.now().isoformat(),
                "versao_orquestrador": VERSAO_ORQUESTRADOR,
                "modelo_llm": LLM_MODEL,
                "modelo_embeddings": EMBED_MODEL,
                "agentes_utilizados": [
                    "Agente Intérprete",
                    "Agente Coletor Meta",
                    "Agente Arquiteto",
                    "Agente PageSpeed",
                    "Agente Analista",
                    "Agente Estrategista"
                ]
            },
            "analise_completa": self.resultados_analise,
            "dados_coletados": self.dados_coletados,
            "relatorio_formatado": relatorio_formatado,
            "execucao": self._resumo_execucao(),
        }

        print("Relatório final consolidado com sucesso!")

    def _resumo_execucao(self) -> Dict[str, Any]:
        """Indicadores da execução usados na avaliação (Seção 5 do artigo)."""
        seo = self.dados_coletados.get("seo", {}) or {}
        anuncios = self.dados_coletados.get("anuncios", []) or []
        analise = self.resultados_analise or {}
        return {
            "tempos_s": {k: round(v, 2) for k, v in self.tempos.items()},
            "interprete_status": self.diretivas_usuario.get("status"),
            "seo_status": seo.get("status"),
            "pagespeed_status": (self.dados_coletados.get("pagespeed") or {}).get("status"),
            "pagespeed_campo": bool((self.dados_coletados.get("pagespeed") or {}).get("campo")),
            "n_anuncios_coletados": len(anuncios) if isinstance(anuncios, list) else 0,
            "n_problemas": len(analise.get("problemas_identificados", [])),
            "n_oportunidades": len(analise.get("oportunidades_identificadas", [])),
            "n_recomendacoes": len(analise.get("recomendacoes_estrategicas", [])),
            "n_recomendacoes_com_fontes": sum(
                1 for r in analise.get("recomendacoes_estrategicas", []) if r.get("fontes")),
            "falhas_tratadas": analise.get("falhas_tratadas", []),
        }

    async def _cronometrar(self, nome: str, coro):
        inicio = time.perf_counter()
        try:
            return await coro
        finally:
            self.tempos[nome] = time.perf_counter() - inicio

    async def executar_analise_completa(
        self,
        url: str,
        termo_busca: str,
        prompt_usuario: str = "",
        salvar_arquivos: bool = True
    ) -> Dict[str, Any]:
        """Executa o fluxo completo de análise."""
        print(f"ANÁLISE DE MARKETING DIGITAL INICIADA")
        print(f"URL: {url}")
        print(f"TERMO: {termo_busca}")
        print(f"PROMPT: {prompt_usuario or 'Nenhum'}")
        print(f"INÍCIO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        custo_inicial = uso_da_chave_usd()
        inicio_total = time.perf_counter()
        try:
            t0 = time.perf_counter()
            self.diretivas_usuario = self.__interpretacao(prompt_usuario)
            self.tempos["interpretacao"] = time.perf_counter() - t0

            await self._cronometrar("coleta", self.__coleta_dados(url, termo_busca))
            await self._cronometrar("analise", self.__analise_(termo_busca, prompt_usuario))
            await self._cronometrar("relatorio", self.__relatorio_final(url, termo_busca, prompt_usuario))
            self.tempos["total"] = time.perf_counter() - inicio_total

            custo_final = uso_da_chave_usd()
            custo = (round(custo_final - custo_inicial, 4)
                     if custo_inicial is not None and custo_final is not None else None)
            self.relatorio_final["execucao"] = self._resumo_execucao()
            self.relatorio_final["execucao"]["custo_usd"] = custo

            print(f"\nANÁLISE CONCLUÍDA. Tempo total: {self.tempos['total']:.1f}s; "
                  f"custo: {custo if custo is not None else 'n/d'} USD")
            return self.relatorio_final

        except Exception as e:
            print(f"\nERRO GERAL NO ORQUESTRADOR: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }

async def main():
    parser = argparse.ArgumentParser(description="Orquestrador Principal")
    parser.add_argument("--url", type=str, required=True, help="URL do site a ser analisado")
    parser.add_argument("--termo", type=str, required=True, help="Termo para busca de anúncios")
    parser.add_argument("--prompt", type=str, default="", help="Prompt opcional com observações do usuário")
    parser.add_argument("--salvar", action="store_true", help="Salvar arquivos intermediários")
    parser.add_argument("--saida", type=str, default="",
                        help="Pasta onde salvar execucao.json e relatorio.md (UTF-8)")
    args = parser.parse_args()

    orquestrador = OrquestradorPrincipal()
    resultado_final = await orquestrador.executar_analise_completa(
        url=args.url,
        termo_busca=args.termo,
        prompt_usuario=args.prompt,
        salvar_arquivos=args.salvar
    )

    if args.saida:
        salvar_resultado(resultado_final, args.saida)
    else:
        print(json.dumps(resultado_final, indent=2, ensure_ascii=False))


def salvar_resultado(resultado: Dict[str, Any], pasta: str):
    """Grava execucao.json e relatorio.md em UTF-8 (dispensa a etapa de correção de codificação)."""
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "execucao.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    with open(os.path.join(pasta, "relatorio.md"), "w", encoding="utf-8") as f:
        f.write(resultado.get("relatorio_formatado", ""))
    print(f"Arquivos salvos em {pasta}/ (execucao.json, relatorio.md)")


if __name__ == "__main__":
    asyncio.run(main())