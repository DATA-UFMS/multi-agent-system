"""
Agente Estrategista (RAG): consulta a base de conhecimento curada e devolve a resposta
acompanhada dos documentos recuperados (rastreabilidade das fontes).
"""
from __future__ import annotations

import os
import asyncio
from typing import Any, Dict

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.readers.file import PDFReader, EpubReader, DocxReader, MarkdownReader
from llama_index.embeddings.openai import OpenAIEmbedding

from config import (OPENROUTER_API_KEY, OPENROUTER_API_BASE, EMBED_MODEL, LLM_MODEL,
                    get_llm, com_tentativas)

BASE_CONHECIMENTO_DIR = os.getenv("RAG_DIR", "RAG")
DIRETORIO_PERSISTENCIA = os.getenv("RAG_STORAGE", "./storage")
TOP_K = int(os.getenv("RAG_TOP_K", "3"))

os.environ["OPENAI_ORG_ID"] = "openrouter"

embed_model = OpenAIEmbedding(
    model_name=EMBED_MODEL,
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)

_indice = None
_motor = None
_n_documentos = 0


def carregar_documentos(diretorio):
    documentos = []
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            caminho = os.path.join(raiz, arquivo)
            if arquivo.endswith(".pdf"):
                documentos.extend(PDFReader().load_data(file=caminho))
            elif arquivo.endswith(".epub"):
                documentos.extend(EpubReader().load_data(file=caminho))
            elif arquivo.endswith(".docx"):
                documentos.extend(DocxReader().load_data(file=caminho))
            elif arquivo.endswith(".md") or arquivo.endswith(".txt"):
                documentos.extend(MarkdownReader().load_data(file=caminho))
    return documentos


def construir_ou_recarregar_indice():
    global _n_documentos
    if os.path.exists(DIRETORIO_PERSISTENCIA):
        print("Agente Estrategista: recarregando índice salvo.")
        storage_context = StorageContext.from_defaults(persist_dir=DIRETORIO_PERSISTENCIA)
        indice = load_index_from_storage(storage_context, embed_model=embed_model)
        _n_documentos = len(indice.docstore.docs)
    else:
        print("Agente Estrategista: construindo índice pela primeira vez.")
        documentos = carregar_documentos(BASE_CONHECIMENTO_DIR)
        _n_documentos = len(documentos)
        print(f"Agente Estrategista: {_n_documentos} documentos carregados.")
        indice = VectorStoreIndex.from_documents(documentos, embed_model=embed_model)
        indice.storage_context.persist(persist_dir=DIRETORIO_PERSISTENCIA)
    return indice


def obter_motor():
    """Constrói o índice e o motor uma única vez por processo (antes era refeito a cada pergunta)."""
    global _indice, _motor
    if _motor is None:
        _indice = construir_ou_recarregar_indice()
        _motor = _indice.as_query_engine(llm=get_llm(), similarity_top_k=TOP_K)
        print(f"Agente Estrategista: motor de consulta pronto (modelo {LLM_MODEL}, top_k={TOP_K}).")
    return _motor


def _formatar_fontes(resposta) -> list:
    fontes = []
    for node in getattr(resposta, "source_nodes", []) or []:
        meta = node.node.metadata or {}
        fontes.append({
            "arquivo": meta.get("file_name") or meta.get("filename") or meta.get("file_path", "desconhecido"),
            "score": round(float(node.score), 4) if node.score is not None else None,
            "trecho": node.node.get_content()[:300].replace("\n", " "),
        })
    return fontes


async def configurar_rag_e_consultar(texto_consulta: str) -> Dict[str, Any]:
    """
    Consulta a base curada. Retorna:
      {"texto": resposta gerada, "fontes": [{"arquivo", "score", "trecho"}, ...]}
    """
    motor = obter_motor()
    print(f"Agente Estrategista: consultando '{texto_consulta[:90]}...'")
    resposta = com_tentativas(lambda: motor.query(texto_consulta), rotulo="Agente Estrategista")
    fontes = _formatar_fontes(resposta)
    print(f"Agente Estrategista: {len(fontes)} documento(s) recuperado(s): "
          f"{[f['arquivo'] for f in fontes]}")
    return {"texto": str(resposta), "fontes": fontes}


if __name__ == "__main__":
    async def main():
        r = await configurar_rag_e_consultar("Como estruturar conteúdo para SEO local de uma clínica?")
        print("\nResposta:\n", r["texto"])
        print("\nFontes:", [f["arquivo"] for f in r["fontes"]])

    asyncio.run(main())
