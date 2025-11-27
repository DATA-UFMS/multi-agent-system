import os
import json
from typing import Dict, List, Any, Tuple
from llama_index.llms.openai import OpenAI
import re
import textwrap
import asyncio
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

from agente_estrategista import configurar_rag_e_consultar

class AgenteAnalista:
    def __init__(self, rag_query_func):
        self.problemas_identificados = []
        self.oportunidades_identificadas = []
        self.recomendacoes_estrategicas = []
        self.rag_query_func = rag_query_func
        self.llm = self._setup_llm()

    def _setup_llm(self):
        if not OPENROUTER_API_KEY:
            print("Agente Analista: ALERTA - OPENROUTER_API_KEY não configurada no .env.")
            return None

        try:
            llm = OpenAI(
                model="gpt-4-turbo-preview",
                api_base=OPENROUTER_API_BASE,
                api_key=OPENROUTER_API_KEY,
                request_timeout=180.0  # Configurado como 180 segundos
            )
            print("Agente Analista: Conexão LLM OpenRouter estabelecida.")
            return llm
        except Exception as e:
            print(f"Agente Analista: ERRO - Falha ao conectar ao OpenRouter. Detalhe: {e}")
            return None

    async def analisar_dados_marketing(self, dados_seo: Dict, dados_anuncios: List[Dict],
                                       diretivas_usuario: Dict, prompt_original: str,
                                       termo_busca: str = "") -> Dict[str, Any]:
        print("\nAgente Analista")
        self.problemas_identificados = []
        self.oportunidades_identificadas = []
        self.recomendacoes_estrategicas = []

        self._analise_primaria_seo(dados_seo)
        self._analise_primaria_anuncios(dados_anuncios)
        await self._raciocinar_e_consultar_estrategista(dados_seo, dados_anuncios, diretivas_usuario, prompt_original)
        relatorio_final = self._gerar_relatorio_final()

        print("Agente Analista: Análise concluída.")
        return relatorio_final

    def _analise_primaria_seo(self, dados_seo: Dict):
        if dados_seo.get("status") != "Sucesso":
            self.problemas_identificados.append({
                "categoria": "SEO",
                "problema": f"Falha na coleta de dados SEO: {dados_seo.get('status')}",
                "prioridade": "crítica"
            })
            return

        if not dados_seo.get("titulo"):
            self.problemas_identificados.append({
                "categoria": "SEO",
                "problema": "Título da página ausente.",
                "prioridade": "alta"
            })

        if not dados_seo.get("meta_description"):
            self.problemas_identificados.append({
                "categoria": "SEO",
                "problema": "Meta descrição ausente.",
                "prioridade": "alta"
            })

        if not dados_seo.get("tags_cabecalho", {}).get("h1"):
            self.problemas_identificados.append({
                "categoria": "SEO",
                "problema": "Nenhuma tag H1 encontrada.",
                "prioridade": "alta"
            })

        if dados_seo.get("contagem_palavras", 0) < 300:
            self.problemas_identificados.append({
                "categoria": "Conteúdo",
                "problema": f"Conteúdo superficial com apenas {dados_seo.get('contagem_palavras', 0)} palavras.",
                "prioridade": "média"
            })

        if dados_seo.get("tempo_carregamento", 0) > 3:
            self.problemas_identificados.append({
                "categoria": "Performance",
                "problema": f"Tempo de carregamento lento: {dados_seo.get('tempo_carregamento', 0)}s.",
                "prioridade": "alta"
            })

        if not dados_seo.get("mobile_friendly"):
            self.problemas_identificados.append({
                "categoria": "Usabilidade",
                "problema": "Página não otimizada para dispositivos móveis.",
                "prioridade": "alta"
            })

    def _analise_primaria_anuncios(self, dados_anuncios: List[Dict]):

        if not dados_anuncios:
            self.oportunidades_identificadas.append({
                "categoria": "Publicidade",
                "oportunidade": "Nenhum anúncio encontrado para o termo, indicando baixa concorrência paga.",
                "potencial": "alto"
            })
            return

        if len(dados_anuncios) < 25:
            self.oportunidades_identificadas.append({
                "categoria": "Publicidade",
                "oportunidade": f"Baixa concorrência ({len(dados_anuncios)} anúncios encontrados), oportunidade de se destacar.",
                "potencial": "alto"
            })

    async def _raciocinar_e_consultar_estrategista(self, dados_seo: Dict, dados_anuncios: List[Dict],
                                                   diretivas_usuario: Dict, prompt_original: str):
        if not self.llm:
            print("Agente Analista: LLM indisponível.")
            return

        resumo_caso = (
            f"Resumo da Análise de Marketing:\n"
            f"- URL Analisada: {dados_seo.get('url')}\n"
            f"- Contexto Original do Usuário: '{prompt_original}'\n"
            f"- Foco Identificado pelo Intérprete: {diretivas_usuario.get('foco_analise', 'Nenhum')}\n\n"
            "Principais Achados:\n"
        )

        for item in self.problemas_identificados + self.oportunidades_identificadas:
            resumo_caso += f"- {item.get('categoria', '')}: {item.get('problema') or item.get('oportunidade')}\n"

        prompt_template = textwrap.dedent(f"""
            Você é um Analista de Marketing Digital Sênior e um Estrategista de Conteúdo.
            Sua tarefa é analisar o caso abaixo e formular 5 perguntas investigativas e profundas
            para um Agente Estrategista (com acesso a uma base RAG).

            REGRAS:
            1. Perguntas específicas e contextuais.
            2. Conecte diferentes áreas do marketing.
            3. Busque insights e ações práticas.
            4. Retorne APENAS uma lista JSON de strings.
            5. As perguntas devem ser, de preferência, abordadas em relação ao nicho do usuário.

            {resumo_caso}

        """)

        try:
            resposta_llm = self.llm.complete(prompt_template)
            raw_text = str(resposta_llm).strip()
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            json_string = match.group(0) if match else raw_text
            perguntas_dinamicas = json.loads(json_string)
            print(f"Agente Analista - Perguntas geradas: {perguntas_dinamicas}")
        except json.JSONDecodeError as e:
            print(f"Agente Analista - ERRO ao decodificar JSON: {e}")
            perguntas_dinamicas = []
        except Exception as e:
            print(f"Agente Analista - ERRO inesperado ao gerar perguntas: {e}")
            perguntas_dinamicas = []

        if perguntas_dinamicas:
            for pergunta in perguntas_dinamicas:
                try:
                    resposta_rag = await self.rag_query_func(pergunta)
                    self.recomendacoes_estrategicas.append({
                        "pergunta": pergunta,
                        "recomendacao": str(resposta_rag),
                        "fonte": "RAG (pergunta dinâmica)"
                    })
                except Exception as e:
                    print(f"Agente Analista - ERRO ao consultar RAG para '{pergunta}': {e}")

    def _gerar_relatorio_final(self) -> Dict[str, Any]:
        return {
            "resumo_executivo": f"Análise concluída. Foram identificados {len(self.problemas_identificados)} problemas e {len(self.oportunidades_identificadas)} oportunidades. Foram geradas {len(self.recomendacoes_estrategicas)} recomendações estratégicas.",
            "problemas_identificados": self.problemas_identificados,
            "oportunidades_identificadas": self.oportunidades_identificadas,
            "recomendacoes_estrategicas": self.recomendacoes_estrategicas,
        }

    async def gerar_relatorio_formatado_txt(self) -> str:
        print("\nAgente Analista - Gerando relatório formatado.")

        if not self.llm:
            return "ERRO: Cliente LLM indisponível."

        prompt_relatorio = textwrap.dedent(f"""
            Você é um redator de relatórios de marketing digital.
            Transforme o JSON abaixo em um relatório legível e profissional (TXT).

            Estrutura:
            1. RESUMO EXECUTIVO
            2. PROBLEMAS IDENTIFICADOS
            3. OPORTUNIDADES (Volume de anúncios)
            4. PLANO DE AÇÃO ESTRATÉGICO

            Dados:
            {json.dumps(self._gerar_relatorio_final(), indent=2, ensure_ascii=False)}
        """)

        try:
            resposta_llm = self.llm.complete(prompt_relatorio)
            texto_relatorio = str(resposta_llm).strip()
            print("Agente Analista - Relatório formatado gerado.")
            return texto_relatorio
        except Exception as e:
            print(f"Agente Analista - ERRO ao gerar relatório: {e}")
            return f"ERRO ao gerar relatório: {e}"


async def analisar_marketing_digital(dados_seo: Dict, dados_anuncios: List[Dict],
                                           diretivas_usuario: Dict, prompt_original: str,
                                           termo_busca: str = "") -> Tuple[Dict[str, Any], 'AgenteAnalista']:
    analista = AgenteAnalista(rag_query_func=configurar_rag_e_consultar)
    analise_resultado = await analista.analisar_dados_marketing(
        dados_seo, dados_anuncios, diretivas_usuario, prompt_original, termo_busca
    )
    return analise_resultado, analista


async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())
