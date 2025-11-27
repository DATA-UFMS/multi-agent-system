import argparse
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

import os
from dotenv import load_dotenv

from agente_interprete import interpretar_prompt_usuario
from agente_analista import analisar_marketing_digital, AgenteAnalista
from agente_coletor_meta import coletar_anuncios_meta
from agente_arquiteto import analisar_seo_on_page

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

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

    def __interpretacao(self, prompt_usuario: str) -> Dict[str, Any]:
        """Interpreta o prompt do usuário com o Agente Intérprete."""
        print("\nINTERPRETAÇÃO DA INTENÇÃO DO USUÁRIO")

        diretivas = interpretar_prompt_usuario(prompt_usuario)
        print(f"Diretivas geradas: {diretivas}")
        return diretivas

    async def __coleta_dados(self, url: str, termo_busca: str):
        """Coordena a coleta de dados pelos agentes especializados."""
        print("\nCOLETA DE DADOS")

        resultados = await asyncio.gather(
            analisar_seo_on_page(url),
            coletar_anuncios_meta(termo_busca),
            return_exceptions=True
        )

        dados_seo, dados_anuncios = resultados

        if isinstance(dados_seo, Exception):
            print(f"Erro na coleta SEO: {dados_seo}")
            dados_seo = {"status": f"Erro: {dados_seo}", "url": url}

        if isinstance(dados_anuncios, Exception):
            print(f"Erro na coleta de anúncios: {dados_anuncios}")
            dados_anuncios = []

        self.dados_coletados = {
            "seo": dados_seo,
            "anuncios": dados_anuncios
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
                termo_busca=termo_busca
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
                "versao_orquestrador": "3.1",
                "agentes_utilizados": [
                    "Agente Intérprete",
                    "Agente Coletor Meta",
                    "Agente Arquiteto Senior",
                    "Agente Analista",
                    "Agente Estrategista"
                ]
            },
            "analise_completa": self.resultados_analise,
            "dados_coletados": self.dados_coletados,
            "relatorio_formatado": relatorio_formatado
        }

        print("Relatório final consolidado com sucesso!")

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

        try:
            self.diretivas_usuario = self.__interpretacao(prompt_usuario)
            await self.__coleta_dados(url, termo_busca)
            await self.__analise_(termo_busca, prompt_usuario)
            await self.__relatorio_final(url, termo_busca, prompt_usuario)

            print("\nANÁLISE CONCLUÍDA COM SUCESSO!")
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
    args = parser.parse_args()

    orquestrador = OrquestradorPrincipal()
    resultado_final = await orquestrador.executar_analise_completa(
        url=args.url,
        termo_busca=args.termo,
        prompt_usuario=args.prompt,
        salvar_arquivos=args.salvar
    )

    print(json.dumps(resultado_final, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())