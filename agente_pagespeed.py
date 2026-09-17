"""
Agente PageSpeed: coleta métricas de desempenho e notas do Lighthouse pela PageSpeed Insights API
(Google). Fonte de dados adicional, incorporada sem alteração dos demais coletores (objetivo O1).

Devolve dados de LABORATÓRIO (Lighthouse, ambiente controlado) e, quando o sítio tem tráfego
suficiente no Chrome UX Report, dados de CAMPO (usuários reais, 28 dias): LCP, INP e CLS.

Configuração no .env:  PAGESPEED_API_KEY=...   (opcional: PAGESPEED_ESTRATEGIA=mobile|desktop)
"""
from __future__ import annotations

import os
from typing import Any, Dict

import httpx

from config import com_tentativas_async

PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")
ESTRATEGIA = os.getenv("PAGESPEED_ESTRATEGIA", "mobile")
ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Limiares oficiais (Core Web Vitals / Lighthouse): (bom, ruim)
LIMIARES = {
    "lcp_ms": (2500, 4000), "inp_ms": (200, 500), "cls": (0.10, 0.25),
    "fcp_ms": (1800, 3000), "tbt_ms": (200, 600),
}


def classificar(metrica: str, valor):
    if valor is None or metrica not in LIMIARES:
        return None
    bom, ruim = LIMIARES[metrica]
    return "bom" if valor <= bom else "ruim" if valor > ruim else "precisa_melhorar"


async def coletar_pagespeed(url: str, estrategia: str = None) -> Dict[str, Any]:
    estrategia = estrategia or ESTRATEGIA
    resultado: Dict[str, Any] = {"status": "nao_configurado", "estrategia": estrategia,
                                 "categorias": {}, "laboratorio": {}, "campo": None}
    if not PAGESPEED_API_KEY:
        print("Agente PageSpeed: PAGESPEED_API_KEY ausente; coleta ignorada.")
        return resultado

    params = [("url", url), ("key", PAGESPEED_API_KEY), ("strategy", estrategia), ("locale", "pt_BR")]
    params += [("category", c) for c in ("performance", "seo", "accessibility", "best-practices")]

    async def chamar():
        async with httpx.AsyncClient(timeout=90) as cli:
            r = await cli.get(ENDPOINT, params=params)
            r.raise_for_status()
            return r.json()

    try:
        print(f"Agente PageSpeed: consultando ({estrategia})...")
        dados = await com_tentativas_async(chamar, tentativas=2, rotulo="Agente PageSpeed")
    except Exception as e:  # noqa: BLE001
        resultado["status"] = f"Erro: {e}"
        print(f"Agente PageSpeed: falha -> {e}")
        return resultado

    lh = dados.get("lighthouseResult", {}) or {}
    cats = lh.get("categories", {}) or {}
    resultado["categorias"] = {
        nome: round((cats.get(chave, {}).get("score") or 0) * 100)
        for nome, chave in (("desempenho", "performance"), ("seo", "seo"),
                            ("acessibilidade", "accessibility"), ("boas_praticas", "best-practices"))
        if chave in cats
    }
    audits = lh.get("audits", {}) or {}

    def num(chave):
        v = (audits.get(chave) or {}).get("numericValue")
        return round(v, 3) if isinstance(v, (int, float)) else None

    lab = {
        "fcp_ms": num("first-contentful-paint"), "lcp_ms": num("largest-contentful-paint"),
        "cls": num("cumulative-layout-shift"), "tbt_ms": num("total-blocking-time"),
        "speed_index_ms": num("speed-index"),
    }
    lab["classificacao"] = {k: classificar(k, v) for k, v in lab.items() if k in LIMIARES}
    resultado["laboratorio"] = lab

    le = dados.get("loadingExperience", {}) or {}
    metricas = le.get("metrics") or {}
    if metricas:
        mapa = {"LARGEST_CONTENTFUL_PAINT_MS": "lcp_ms", "INTERACTION_TO_NEXT_PAINT": "inp_ms",
                "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls", "FIRST_CONTENTFUL_PAINT_MS": "fcp_ms"}
        campo = {}
        for chave_api, nome in mapa.items():
            m = metricas.get(chave_api)
            if m:
                valor = m.get("percentile")
                if nome == "cls" and valor is not None:
                    valor = valor / 100  # a API devolve CLS x100
                campo[nome] = {"p75": valor, "categoria": (m.get("category") or "").lower()}
        campo["geral"] = (le.get("overall_category") or "").lower()
        campo["origem_agregada"] = bool(le.get("origin_fallback"))
        resultado["campo"] = campo
    else:
        resultado["campo"] = None  # tráfego insuficiente no CrUX (comum em PMEs)

    resultado["status"] = "Sucesso"
    print(f"Agente PageSpeed: notas {resultado['categorias']}; campo: "
          f"{'sim' if resultado['campo'] else 'sem dados (tráfego insuficiente)'}")
    return resultado


if __name__ == "__main__":
    import asyncio, json, sys
    print(json.dumps(asyncio.run(coletar_pagespeed(sys.argv[1])), indent=2, ensure_ascii=False))
