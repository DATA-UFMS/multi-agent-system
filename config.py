"""
Configuração central do Agents-Mkt (modelos, API e utilitários compartilhados).

Tudo pode ser sobrescrito por variáveis de ambiente (arquivo .env):
  OPENROUTER_API_KEY   chave da OpenRouter (obrigatória)
  OPENROUTER_API_BASE  padrão: https://openrouter.ai/api/v1
  LLM_MODEL            modelo usado pelos agentes (padrão: openai/gpt-4.1)
  EMBED_MODEL          modelo de embeddings (precisa ser o mesmo do índice em ./storage)
  HEADLESS             "1" (padrão) roda os navegadores sem janela; "0" abre a janela
  LLM_MAX_TENTATIVAS   tentativas por chamada ao LLM (padrão: 3)
"""
from __future__ import annotations

import os
import time
from typing import Callable, TypeVar

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4.1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "mistralai/mistral-embed-2312")
HEADLESS = os.getenv("HEADLESS", "1") != "0"
LLM_MAX_TENTATIVAS = int(os.getenv("LLM_MAX_TENTATIVAS", "3"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "180"))

# Compatibilidade com bibliotecas que leem as variáveis da OpenAI diretamente.
if OPENROUTER_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", OPENROUTER_API_KEY)
    os.environ.setdefault("OPENAI_API_BASE", OPENROUTER_API_BASE)

T = TypeVar("T")


def com_tentativas(func: Callable[[], T], tentativas: int = None, rotulo: str = "LLM") -> T:
    """Executa `func` até `tentativas` vezes com espera exponencial. Relança a última exceção."""
    tentativas = tentativas or LLM_MAX_TENTATIVAS
    ultima = None
    for i in range(1, tentativas + 1):
        try:
            return func()
        except Exception as e:  # noqa: BLE001 - queremos capturar qualquer falha de rede/API
            ultima = e
            if i < tentativas:
                espera = 2 ** i
                print(f"{rotulo}: tentativa {i}/{tentativas} falhou ({type(e).__name__}: {e}). "
                      f"Nova tentativa em {espera}s.")
                time.sleep(espera)
    raise ultima


def get_llm(model: str = None, temperature: float = 0.0):
    """LLM para o LlamaIndex aceitando qualquer identificador de modelo da OpenRouter."""
    from llama_index.llms.openai_like import OpenAILike

    return OpenAILike(
        model=model or LLM_MODEL,
        api_base=OPENROUTER_API_BASE,
        api_key=OPENROUTER_API_KEY,
        is_chat_model=True,
        is_function_calling_model=False,
        context_window=128000,
        temperature=temperature,
        timeout=LLM_TIMEOUT,
        max_retries=0,  # as tentativas são controladas por com_tentativas()
    )


def get_openai_client():
    """Cliente OpenAI puro (usado pelo Intérprete, pelo baseline e pelas juízas)."""
    from openai import OpenAI

    return OpenAI(base_url=OPENROUTER_API_BASE, api_key=OPENROUTER_API_KEY,
                  timeout=LLM_TIMEOUT, max_retries=0)


def uso_da_chave_usd() -> float | None:
    """Total gasto (USD) pela chave até agora, segundo a OpenRouter. Usado para medir custo por execução."""
    try:
        import httpx

        r = httpx.get(f"{OPENROUTER_API_BASE}/auth/key",
                      headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}, timeout=20)
        r.raise_for_status()
        return float(r.json()["data"]["usage"])
    except Exception as e:  # noqa: BLE001
        print(f"config: não foi possível consultar o uso da chave ({e}).")
        return None
