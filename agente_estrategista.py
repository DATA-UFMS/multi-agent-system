import os
import asyncio
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.readers.file import PDFReader, EpubReader, DocxReader, MarkdownReader
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

BASE_CONHECIMENTO_DIR = "RAG"
DIRETORIO_PERSISTENCIA = "./storage"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
os.environ["OPENAI_API_BASE"] = OPENROUTER_API_BASE
os.environ["OPENAI_ORG_ID"] = "openrouter"

print("API Key carregada:", "SIM" if OPENROUTER_API_KEY else "NÃO")
print("Base da API:", OPENROUTER_API_BASE)

# Modelo LLM
llm = OpenAI(
    model="gpt-4-turbo-preview",
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
    request_timeout=180.0
)

# Modelo de embeddings
embed_model = OpenAIEmbedding(
    model_name="mistralai/mistral-embed-2312",
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY
)

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

def construir_ou_recarregar_indice(documentos):
    if os.path.exists(DIRETORIO_PERSISTENCIA):
        print("Recarregando índice salvo.")
        storage_context = StorageContext.from_defaults(persist_dir=DIRETORIO_PERSISTENCIA)
        indice = load_index_from_storage(storage_context, embed_model=embed_model)
    else:
        print("Construindo índice pela primeira vez.")
        indice = VectorStoreIndex.from_documents(documentos, embed_model=embed_model)
        indice.storage_context.persist(persist_dir=DIRETORIO_PERSISTENCIA)

    return indice

def criar_motor_de_consulta(indice):
    return indice.as_query_engine(llm=llm)

async def configurar_rag_e_consultar(texto_consulta):
    print("Carregando documentos.")
    documentos = carregar_documentos(BASE_CONHECIMENTO_DIR)
    print(f"Documentos carregados: {len(documentos)}")

    print("Construindo ou recarregando o índice vetorial.")
    indice = construir_ou_recarregar_indice(documentos)
    print("Índice vetorial pronto.")

    print("Criando motor de consulta.")
    motor = criar_motor_de_consulta(indice)
    print("Motor de consulta criado.")

    print(f"Realizando consulta: '{texto_consulta}'")
    resposta = motor.query(texto_consulta)

    return resposta

if __name__ == "__main__":
    async def main():
        resposta = await configurar_rag_e_consultar("Me dê uma lista de citações sobre SEO")
        print("\nResposta do RAG:")
        print(resposta)

    asyncio.run(main())
