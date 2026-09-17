"""
Verificação pós-hoc de explicabilidade (fidelidade) dos relatórios.

O campo "Evidência" e o campo "Fontes" de cada recomendação são autodeclarações do LLM.
Este script verifica, sem alterar o sistema, se essas declarações são sustentadas pelos
dados estruturados da execução:

  1. evidencia_dados     - a Evidência menciona um número ou um fato presente nos dados coletados
                           ou no diagnóstico (mesma função para sistema e baseline);
  2. evidencia_contexto  - a Evidência menciona um elemento do contexto informado pelo gestor;
  3. fontes_verificaveis - fração das fontes citadas que constam entre os documentos de fato
                           recuperados na execução (o baseline B1 não tem recuperação registrada,
                           logo suas fontes são inverificáveis por construção);
  4. numeros_nao_rastreaveis - números no relatório que não aparecem nos dados, no diagnóstico,
                           nos limiares das regras nem no contexto (lista para revisão manual).

  python explicabilidade.py --resultados resultados --saida resultados/explicabilidade
  python explicabilidade.py --pasta resultados/teste_v3          # uma execução isolada
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import unicodedata
from urllib.parse import urlparse

LIMIARES_REGRAS = {"30", "60", "70", "160", "300", "25", "3", "1,8", "1.8", "1", "5"}
STOPWORDS = set("""a o as os de da do das dos e em um uma para com que se não mais por como ao aos na no nas
nos sua seu suas seus ser tem está são foi ou mas já muito também pela pelo entre sobre ate até
empresa clínica clinica gostariam possuem querem interesse maior necessidade plano ação acao prático
pratico aplicação aplicacao definir avaliar estratégias estrategias outras intuito atrair clientes
melhorar algo sejam seja embora fazem publicações publicacoes conteúdo conteudo localizada""".split())


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t.lower()).strip()


def numeros(t: str) -> set:
    """Números como aparecem no texto, normalizados (vírgula -> ponto, sem separador de milhar)."""
    out = set()
    for m in re.findall(r"\d[\d.,]*", t or ""):
        m = m.rstrip(".,")
        if not m:
            continue
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", m):        # 1.086 -> 1086
            m = m.replace(".", "")
        m = m.replace(",", ".")
        out.add(m)
        if "." in m:
            out.add(m.split(".")[0])
    return out


# ------------------------------------------------------------------ fatos
def fatos_da_execucao(exec_json: dict) -> dict:
    """Números e palavras-chave verificáveis, derivados dos dados coletados (iguais para as duas condições)."""
    seo = exec_json.get("dados_coletados", {}).get("seo", {}) or {}
    anuncios = exec_json.get("dados_coletados", {}).get("anuncios", []) or []
    nums, chaves = set(), set()

    def add_num(v):
        if isinstance(v, (int, float)) and v is not None:
            nums.update(numeros(str(v)))
            nums.update(numeros(str(round(v, 1))))
            nums.update(numeros(str(round(v, 2))))

    titulo = seo.get("titulo") or ""
    desc = seo.get("meta_description") or ""
    add_num(len(titulo)); add_num(len(desc)); add_num(seo.get("contagem_palavras"))
    add_num(seo.get("tempo_carregamento")); add_num(len(seo.get("imagens_sem_alt") or []))
    add_num(seo.get("links_internos")); add_num(seo.get("links_externos"))
    add_num(len(anuncios))
    for tag, lst in (seo.get("tags_cabecalho") or {}).items():
        add_num(len(lst)); chaves.add(tag.lower())
    perf = seo.get("performance_metrics") or {}
    fcp = perf.get("first_contentful_paint")
    if fcp:
        add_num(fcp); add_num(fcp / 1000)
    if seo.get("canonical_url"):
        chaves.add("canonic")
        host = urlparse(seo["canonical_url"]).netloc.replace("www.", "")
        if host:
            chaves.add(normalizar(host))
    if titulo: chaves.add("titulo")
    if desc: chaves.add("meta descri")
    if not seo.get("mobile_friendly"): chaves.add("viewport"); chaves.add("mobile")
    if seo.get("imagens_sem_alt"): chaves.add("alt")
    if not seo.get("open_graph"): chaves.add("open graph")
    if not seo.get("structured_data"): chaves.update({"json-ld", "dados estruturados"})
    chaves.update({"palavras", "carregamento", "anuncio", "anúncio"})
    tipos = {normalizar(a.get("tipo_criativo", "")) for a in anuncios}
    if "video" in tipos: chaves.add("video")
    if "imagem" in tipos: chaves.add("imagem")
    if any(a.get("cta") not in (None, "", "Não encontrado") for a in anuncios): chaves.add("cta")

    ig = (exec_json.get("dados_coletados", {}).get("perfil_instagram") or {}).get("perfil_social") or {}
    for k in ("seguidores", "publicacoes"):
        add_num(ig.get(k))
    if ig:
        chaves.update({"seguidores", "publicac", "instagram"})
    ps = exec_json.get("dados_coletados", {}).get("pagespeed", {}) or {}
    for v in (ps.get("categorias") or {}).values():
        add_num(v)
    for k, v in (ps.get("laboratorio") or {}).items():
        if isinstance(v, (int, float)):
            add_num(v); add_num(v / 1000)
    for k, v in (ps.get("campo") or {}).items():
        if isinstance(v, dict) and isinstance(v.get("p75"), (int, float)):
            add_num(v["p75"]); add_num(v["p75"] / 1000)
    if ps.get("status") == "Sucesso":
        chaves.update({"lighthouse", "pagespeed", "lcp", "cls", "inp", "desempenho"})

    # diagnóstico do sistema (se houver): números e regras acionadas
    analise = exec_json.get("analise_completa", {}) or {}
    for p in analise.get("problemas_identificados", []):
        nums.update(numeros(p.get("problema", "")))
        chaves.add(normalizar(p.get("categoria", "")))
    for o in analise.get("oportunidades_identificadas", []):
        nums.update(numeros(o.get("oportunidade", "")))
    pan = analise.get("panorama_anuncios", {}) or {}
    add_num(pan.get("total_coletado"))
    if pan.get("proporcao_video") is not None:
        add_num(pan["proporcao_video"]); add_num(round(pan["proporcao_video"] * 100))

    # contexto informado pelo gestor
    prompt = exec_json.get("metadados", {}).get("prompt_usuario", "")
    termo = exec_json.get("metadados", {}).get("termo_busca", "")
    palavras_ctx = {w for w in re.findall(r"[a-zA-ZÀ-ÿ]{4,}", prompt + " " + termo)}
    contexto = {normalizar(w) for w in palavras_ctx if normalizar(w) not in STOPWORDS}
    nums.update(numeros(prompt))

    fontes_recuperadas = set()
    for r in analise.get("recomendacoes_estrategicas", []):
        fontes_recuperadas.update(r.get("fontes", []))
    return {"numeros": nums, "chaves": chaves, "contexto": contexto, "fontes": fontes_recuperadas}


# -------------------------------------------------------------- relatório
CAMPOS = ["Ação", "Evidência", "Como executar", "Prioridade", "Esforço", "Fontes"]


def parse_recomendacoes(md: str) -> list:
    """Extrai as subseções '### 4.x' com os campos em negrito."""
    recs = []
    partes = re.split(r"\n###\s+", md)
    for parte in partes[1:]:
        titulo = parte.split("\n", 1)[0].strip()
        if not re.match(r"4\.\d", titulo):
            continue
        rec = {"titulo": titulo}
        for campo in CAMPOS:
            m = re.search(r"\*\*%s:?\*\*:?\s*(.+?)(?=\n\s*\*\*|\n###|\n##|\Z)" % re.escape(campo), parte, re.S)
            rec[campo] = m.group(1).strip() if m else ""
        recs.append(rec)
    return recs


def avaliar_relatorio(md: str, fatos: dict, condicao: str) -> list:
    linhas = []
    for rec in parse_recomendacoes(md):
        ev = rec["Evidência"]
        ev_n = normalizar(ev)
        nums_ev = numeros(ev)
        num_ok = bool(nums_ev & fatos["numeros"])
        chave_ok = any(c and c in ev_n for c in fatos["chaves"])
        ctx_ok = any(c in ev_n for c in fatos["contexto"])
        fontes_citadas = [f.strip() for f in re.split(r"[,;]", rec["Fontes"]) if f.strip()]
        fontes_citadas = [f for f in fontes_citadas if not re.search(r"nao (recuperadas|informadas)", normalizar(f))]
        if condicao == "sistema":
            ok = [f for f in fontes_citadas if any(f.lower() in fr.lower() or fr.lower() in f.lower() for fr in fatos["fontes"])]
            fontes_verif = round(len(ok) / len(fontes_citadas), 2) if fontes_citadas else None
        else:
            fontes_verif = 0.0 if fontes_citadas else None   # sem recuperação registrada: inverificáveis
        linhas.append({
            "condicao": condicao, "recomendacao": rec["titulo"],
            "evidencia_dados": int(num_ok or chave_ok), "evidencia_numero": int(num_ok),
            "evidencia_contexto": int(ctx_ok), "evidencia_vazia": int(not ev.strip()),
            "n_fontes_citadas": len(fontes_citadas), "fontes_verificaveis": fontes_verif,
            "prioridade": rec["Prioridade"][:10], "esforco": rec["Esforço"][:10],
            "evidencia": ev.replace("\n", " ")[:200],
        })
    return linhas


def numeros_nao_rastreaveis(md: str, fatos: dict) -> list:
    corpo = re.sub(r"^#{1,3}\s.*$", "", md, flags=re.M)          # remove títulos (numeração de seções)
    corpo = re.sub(r"\b4\.\d\b", "", corpo)
    conhecidos = fatos["numeros"] | LIMIARES_REGRAS | {"2026", "2025", "90", "100"}
    return sorted(n for n in numeros(corpo) if n not in conhecidos and not re.fullmatch(r"[1-5]", n))


# ------------------------------------------------------------------ main
def avaliar_pasta(pasta_exec: str, condicao: str, fatos: dict = None):
    with open(os.path.join(pasta_exec, "execucao.json"), encoding="utf-8") as f:
        ex = json.load(f)
    with open(os.path.join(pasta_exec, "relatorio.md"), encoding="utf-8") as f:
        md = f.read()
    fatos = fatos or fatos_da_execucao(ex)
    return avaliar_relatorio(md, fatos, condicao), numeros_nao_rastreaveis(md, fatos), fatos


def resumo(linhas):
    n = len(linhas) or 1
    fv = [l["fontes_verificaveis"] for l in linhas if l["fontes_verificaveis"] is not None]
    return {
        "n_recomendacoes": len(linhas),
        "evidencia_dados_%": round(100 * sum(l["evidencia_dados"] for l in linhas) / n),
        "evidencia_contexto_%": round(100 * sum(l["evidencia_contexto"] for l in linhas) / n),
        "evidencia_vazia_%": round(100 * sum(l["evidencia_vazia"] for l in linhas) / n),
        "fontes_verificaveis_%": round(100 * sum(fv) / len(fv)) if fv else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultados", default="resultados")
    ap.add_argument("--saida", default="resultados/explicabilidade")
    ap.add_argument("--pasta", help="avalia uma única execução do sistema (ex.: resultados/teste_v3)")
    args = ap.parse_args()

    todas, resumos = [], []
    if args.pasta:
        linhas, nao_rastr, _ = avaliar_pasta(args.pasta, "sistema")
        for l in linhas: l["empresa"] = os.path.basename(args.pasta)
        todas += linhas
        resumos.append({"empresa": os.path.basename(args.pasta), "condicao": "sistema", **resumo(linhas),
                        "numeros_nao_rastreaveis": " ".join(nao_rastr)})
    else:
        for emp in sorted(os.listdir(args.resultados)):
            p_sis = os.path.join(args.resultados, emp, "sistema", "rep1")
            p_b1 = os.path.join(args.resultados, emp, "b1")
            if not os.path.exists(os.path.join(p_sis, "execucao.json")):
                continue
            linhas, nao_rastr, fatos = avaliar_pasta(p_sis, "sistema")
            for l in linhas: l["empresa"] = emp
            todas += linhas
            resumos.append({"empresa": emp, "condicao": "sistema", **resumo(linhas), "numeros_nao_rastreaveis": " ".join(nao_rastr)})
            if os.path.exists(os.path.join(p_b1, "relatorio.md")):
                # B1 é avaliado contra os MESMOS fatos brutos (sem o diagnóstico do sistema)
                with open(os.path.join(p_b1, "execucao.json"), encoding="utf-8") as f:
                    ex_b1 = json.load(f)
                fatos_b1 = fatos_da_execucao({**ex_b1, "analise_completa": {}})
                with open(os.path.join(p_b1, "relatorio.md"), encoding="utf-8") as f:
                    md_b1 = f.read()
                l_b1 = avaliar_relatorio(md_b1, fatos_b1, "b1")
                for l in l_b1: l["empresa"] = emp
                todas += l_b1
                resumos.append({"empresa": emp, "condicao": "b1", **resumo(l_b1),
                                "numeros_nao_rastreaveis": " ".join(numeros_nao_rastreaveis(md_b1, fatos_b1))})

    os.makedirs(args.saida, exist_ok=True)
    if todas:
        with open(os.path.join(args.saida, "explicabilidade.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(todas[0].keys())); w.writeheader(); w.writerows(todas)
    with open(os.path.join(args.saida, "resumo.md"), "w", encoding="utf-8") as f:
        f.write("| Empresa | Condição | Rec. | Evidência c/ dados | Evidência c/ contexto | Evidência vazia | Fontes verificáveis | Números não rastreáveis |\n|---|---|---|---|---|---|---|---|\n")
        for r in resumos:
            f.write(f"| {r['empresa']} | {r['condicao']} | {r['n_recomendacoes']} | {r['evidencia_dados_%']}% | "
                    f"{r['evidencia_contexto_%']}% | {r['evidencia_vazia_%']}% | "
                    f"{r['fontes_verificaveis_%'] if r['fontes_verificaveis_%'] is not None else 'n/a'}"
                    f"{'%' if r['fontes_verificaveis_%'] is not None else ''} | {r['numeros_nao_rastreaveis'] or '—'} |\n")
    print(open(os.path.join(args.saida, "resumo.md"), encoding="utf-8").read())
    for l in todas:
        print(f"[{l['condicao']}] {l['recomendacao'][:45]:45s} dados={l['evidencia_dados']} ctx={l['evidencia_contexto']} "
              f"fontes={l['fontes_verificaveis']} | {l['evidencia'][:90]}")


if __name__ == "__main__":
    main()
