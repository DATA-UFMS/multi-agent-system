import os
import json
import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI as OpenAIClient
from dotenv import load_dotenv

load_dotenv()

openrouter_key = os.getenv("OPENROUTER_API_KEY")

if openrouter_key:
    os.environ["OPENAI_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

DIRETIVAS_PADRAO = {
    "foco_analise": ["seo_geral", "anuncios_geral"],
    "hipoteses_usuario": [],
    "status": "sucesso_padrao"
}

AREAS_DE_FOCO = [
    "performance", "conteudo", "seo_tecnico", "design_responsivo",
    "analise_cta", "analise_criativos", "seo_geral", "anuncios_geral"
]

class DiretivasUsuario(BaseModel):
    foco_analise: List[str] = Field(
        description=f"Lista de áreas de foco da análise. Deve ser um subconjunto de: {AREAS_DE_FOCO}."
    )
    hipoteses_usuario: List[str] = Field(
        description="Lista de afirmações ou dúvidas diretas do usuário extraídas do prompt."
    )

def get_llm_client():
    try:
        client = OpenAIClient(
            base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENAI_API_KEY"), 
        )
        print("Agente Intérprete: Conexão com o LLM OpenRouter estabelecida.")
        return client
    except Exception as e:
        print(f"Agente Intérprete: {e}")
        return None

llm_client = get_llm_client()

def interpretar_prompt_usuario(prompt_usuario: str) -> Dict[str, Any]:
    print(f"\nAgente Intérprete: Iniciando interpretação do prompt")

    if not llm_client or not prompt_usuario.strip():
        print("Agente Intérprete: Cliente LLM não inicializado ou prompt vazio. Usando diretivas padrão.")
        return DIRETIVAS_PADRAO

    prompt_sistema = f"""
    Você é um especialista em Marketing Digital e SEO. Sua tarefa é analisar o pedido de um usuário e traduzi-lo em um objeto JSON. Tente adaptar suas respostas para atender as necessidades específicas do usuário e encaixar com seu conhecimento.

    As áreas de foco possíveis são: {', '.join(AREAS_DE_FOCO)}.
    As hipóteses são as afirmações ou dúvidas diretas do usuário.

    Analise o seguinte prompt do usuário:
    "{prompt_usuario}"

    Retorne APENAS um JSON contendo os valores preenchidos.
    Não retorne explicações.
    Não retorne comentários.
    NÃO retorne o schema.

    O JSON deve seguir exatamente o seguinte schema (não devolva o schema, use-o somente como referência):
    {DiretivasUsuario.model_json_schema()}

    """

    try:
        response = llm_client.chat.completions.create(
            model="openai/gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Prompt do Usuário: {prompt_usuario}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            timeout=120.0
        )

        resposta_texto = response.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", resposta_texto, re.DOTALL)
        json_string = match.group(0) if match else resposta_texto

        diretivas_dict = json.loads(json_string)
        diretivas_pydantic = DiretivasUsuario.model_validate(diretivas_dict)
        diretivas = diretivas_pydantic.model_dump()
        diretivas["status"] = "sucesso_llm"

        print(f"Agente Intérprete: Interpretação com LLM concluída. Diretivas: {diretivas}")
        return diretivas

    except ValidationError as e:
        print(f"Agente Intérprete: ERRO - Falha de validação Pydantic: {e}")
        return DIRETIVAS_PADRAO
    except json.JSONDecodeError as e:
        print(f"Agente Intérprete: ERRO - Falha ao decodificar JSON: {e}")
        return DIRETIVAS_PADRAO
    except Exception as e:
        print(f"Agente Intérprete: ERRO - Falha geral: {e}")
        return DIRETIVAS_PADRAO

def main():
    # Validação se o prompt está sendo interpretado corretamente   
    prompt_1 = "Analise meu site. Acho que ele está lento no celular e meus concorrentes usam mais vídeos nos anúncios. Também não sei se meu título está bom."
    print(f"Prompt: {prompt_1}")
    diretivas1 = interpretar_prompt_usuario(prompt_1)
    print(f"\nResultado Final 1:\n{json.dumps(diretivas1, indent=2, ensure_ascii=False)}")

    prompt_2 = "Quero saber se meu conteúdo está otimizado para SEO e se meus CTAs nos anúncios estão claros."
    print(f"Prompt: {prompt_2}")
    diretivas2 = interpretar_prompt_usuario(prompt_2)
    print(f"\n{json.dumps(diretivas2, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()
