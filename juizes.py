"""
LLM-as-judge: comparação pareada cega entre o relatório do sistema e o do baseline B1.

Para cada empresa, cada juíza recebe os dois relatórios em ORDEM ALEATÓRIA e, em seguida, na
ordem INVERTIDA (controle de viés de posição). A rubrica é fixa (avaliacao/rubrica.md).
A juíza devolve, por dimensão, o vencedor (A/B/empate) e notas 1–5 para cada relatório.

  python juizes.py --resultados resultados --saida resultados/juizes [--modelos m1,m2,m3]
  python juizes.py --so-analise --saida resultados/juizes [--humanos avaliacao/respostas_harmonie.csv]

Saídas: julgamentos.csv (bruto), resumo.md (taxas de vitória, consistência de posição,
alpha de Krippendorff entre juízas e, se houver, concordância juízas × humanos).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import textwrap
from collections import Counter, defaultdict
from itertools import combinations

from config import LLM_TIMEOUT, get_openai_client, com_tentativas

DIMENSOES = {
    "contexto": "Aderência ao contexto: o relatório considera a necessidade, o setor e a localidade informados pela empresa, em vez de conselhos genéricos.",
    "acionabilidade": "Especificidade e acionabilidade: recomendações concretas, priorizadas e executáveis por uma PME, não frases vagas.",
    "fundamentacao": "Fundamentação: as recomendações se apoiam nos dados coletados (SEO, anúncios) e/ou em fontes identificáveis; problemas apontados correspondem aos dados.",
    "correcao": "Correção técnica: afirmações sobre SEO, anúncios e desempenho corretas; ausência de dados inventados ou incoerentes com os coletados.",
    "adequacao_pme": "Adequação a PME: viável com recursos limitados e escrito em linguagem compreensível para um gestor sem formação em marketing.",
}
PADRAO_JUIZAS = os.getenv("JUDGE_MODELS",
                         "anthropic/claude-sonnet-4.5,google/gemini-2.5-pro,mistralai/mistral-large")


def montar_prompt(contexto, dados_resumo, rel_a, rel_b):
    dims = "\n".join(f"- **{k}** — {v}" for k, v in DIMENSOES.items())
    return textwrap.dedent(f"""
        Você é um avaliador independente de relatórios de consultoria em marketing digital para PMEs.
        Dois relatórios (A e B) foram produzidos para a mesma empresa a partir dos MESMOS dados.
        Avalie-os com rigor e sem preferência por tamanho ou estilo.

        CONTEXTO INFORMADO PELA EMPRESA:
        {contexto}

        DADOS COLETADOS (resumo, para checar fundamentação e correção):
        {dados_resumo}

        DIMENSÕES:
        {dims}

        ===== RELATÓRIO A =====
        {rel_a}

        ===== RELATÓRIO B =====
        {rel_b}

        Responda APENAS com um JSON neste formato:
        {{
          "dimensoes": {{
            "contexto": {{"vencedor": "A|B|empate", "nota_A": 1-5, "nota_B": 1-5, "justificativa": "..."}},
            "acionabilidade": {{...}}, "fundamentacao": {{...}}, "correcao": {{...}}, "adequacao_pme": {{...}}
          }},
          "geral": {{"vencedor": "A|B|empate", "justificativa": "..."}}
        }}
    """).strip()


def resumo_dados(exec_json):
    d = exec_json.get("dados_coletados", {})
    seo = d.get("seo", {}) or {}
    chaves = ("url", "status", "titulo", "meta_description", "tags_cabecalho", "contagem_palavras",
              "tempo_carregamento", "mobile_friendly")
    resumo = {k: seo.get(k) for k in chaves if k in seo}
    resumo["n_anuncios_ativos_coletados"] = len(d.get("anuncios", []) or [])
    return json.dumps(resumo, ensure_ascii=False, indent=2)


def julgar(client, modelo, prompt):
    r = com_tentativas(lambda: client.chat.completions.create(
        model=modelo, messages=[{"role": "user", "content": prompt}],
        temperature=0.0, timeout=LLM_TIMEOUT), rotulo=f"Juíza {modelo}")
    txt = r.choices[0].message.content
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    return json.loads(m.group(0) if m else txt)


def carregar_par(pasta_resultados, emp_id):
    base = os.path.join(pasta_resultados, emp_id)
    p_sis = os.path.join(base, "sistema", "rep1")
    p_b1 = os.path.join(base, "b1")
    if not (os.path.exists(p_sis) and os.path.exists(p_b1)):
        return None
    with open(os.path.join(p_sis, "execucao.json"), encoding="utf-8") as f:
        exec_sis = json.load(f)
    with open(os.path.join(p_sis, "relatorio.md"), encoding="utf-8") as f:
        rel_sis = f.read()
    with open(os.path.join(p_b1, "relatorio.md"), encoding="utf-8") as f:
        rel_b1 = f.read()
    return exec_sis, rel_sis, rel_b1


def executar_julgamentos(pasta_resultados, modelos, saida, seed=42):
    random.seed(seed)
    client = get_openai_client()
    os.makedirs(saida, exist_ok=True)
    linhas = []
    empresas = sorted(d for d in os.listdir(pasta_resultados)
                      if os.path.isdir(os.path.join(pasta_resultados, d)) and d != "juizes")
    for emp_id in empresas:
        par = carregar_par(pasta_resultados, emp_id)
        if not par:
            print(f"{emp_id}: par incompleto, pulando.")
            continue
        exec_sis, rel_sis, rel_b1 = par
        contexto = exec_sis["metadados"]["prompt_usuario"]
        dados = resumo_dados(exec_sis)
        primeira_ordem = random.choice(["sistema_A", "b1_A"])
        for modelo in modelos:
            for ordem in (primeira_ordem, "b1_A" if primeira_ordem == "sistema_A" else "sistema_A"):
                rel_a, rel_b = (rel_sis, rel_b1) if ordem == "sistema_A" else (rel_b1, rel_sis)
                mapa = {"A": "sistema", "B": "b1"} if ordem == "sistema_A" else {"A": "b1", "B": "sistema"}
                print(f"{emp_id} | {modelo} | ordem {ordem}")
                try:
                    j = julgar(client, modelo, montar_prompt(contexto, dados, rel_a, rel_b))
                except Exception as e:  # noqa: BLE001
                    print(f"  falha: {e}")
                    linhas.append({"empresa": emp_id, "juiza": modelo, "ordem": ordem, "erro": str(e)})
                    continue
                for dim in list(DIMENSOES) + ["geral"]:
                    item = j.get("dimensoes", {}).get(dim) if dim != "geral" else j.get("geral", {})
                    if not item:
                        continue
                    venc = str(item.get("vencedor", "")).strip().upper()
                    venc_cond = mapa.get(venc, "empate" if "EMP" in venc else "invalido")
                    linhas.append({
                        "empresa": emp_id, "juiza": modelo, "ordem": ordem, "dimensao": dim,
                        "vencedor": venc_cond,
                        "nota_sistema": item.get("nota_A" if mapa["A"] == "sistema" else "nota_B"),
                        "nota_b1": item.get("nota_A" if mapa["A"] == "b1" else "nota_B"),
                        "justificativa": (item.get("justificativa") or "").replace("\n", " "),
                    })
                with open(os.path.join(saida, f"bruto_{emp_id}_{modelo.replace('/', '_')}_{ordem}.json"),
                          "w", encoding="utf-8") as f:
                    json.dump(j, f, ensure_ascii=False, indent=2)
    campos = ["empresa", "juiza", "ordem", "dimensao", "vencedor", "nota_sistema", "nota_b1", "justificativa", "erro"]
    with open(os.path.join(saida, "julgamentos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    return linhas


# ----------------------------- análise -----------------------------

def krippendorff_alpha_nominal(unidades):
    """
    alpha de Krippendorff (nominal). `unidades` = lista de listas de rótulos (um por avaliador),
    uma lista por unidade avaliada; unidades com <2 rótulos são ignoradas.
    """
    unidades = [[v for v in u if v is not None] for u in unidades]
    unidades = [u for u in unidades if len(u) >= 2]
    if not unidades:
        return None
    n = sum(len(u) for u in unidades)
    total = Counter(v for u in unidades for v in u)
    Do = 0.0
    for u in unidades:
        m = len(u)
        c = Counter(u)
        desac = sum(c[a] * c[b] for a, b in combinations(c, 2)) * 2
        Do += desac / (m - 1)
    Do /= n
    De = sum(total[a] * total[b] for a, b in combinations(total, 2)) * 2 / (n * (n - 1)) if n > 1 else 0
    return None if De == 0 else round(1 - Do / De, 3)


def analisar(saida, humanos_csv=None):
    with open(os.path.join(saida, "julgamentos.csv"), encoding="utf-8") as f:
        linhas = [l for l in csv.DictReader(f) if l.get("dimensao")]
    juizas = sorted({l["juiza"] for l in linhas})
    dims = list(DIMENSOES) + ["geral"]
    out = ["# Resultado das juízas LLM\n", f"Juízas: {', '.join(juizas)}\n"]

    # 1) taxas de vitória por dimensão (todas as juízas e ordens)
    out.append("\n## Taxa de vitória por dimensão (sistema vs. B1)\n")
    out.append("| Dimensão | Sistema | B1 | Empate | n | Nota média sistema | Nota média B1 |\n|---|---|---|---|---|---|---|")
    for dim in dims:
        ls = [l for l in linhas if l["dimensao"] == dim]
        c = Counter(l["vencedor"] for l in ls)
        n = len(ls) or 1
        def media(ch):
            vals = [float(l[ch]) for l in ls if l.get(ch) not in (None, "", "None")]
            return f"{sum(vals) / len(vals):.2f}" if vals else "-"
        out.append(f"| {dim} | {c['sistema'] / n:.0%} | {c['b1'] / n:.0%} | {c['empate'] / n:.0%} | {len(ls)} | {media('nota_sistema')} | {media('nota_b1')} |")

    # 2) consistência de posição: mesma juíza, mesma empresa, ordens invertidas
    out.append("\n## Consistência de posição (mesmo veredito nas duas ordens)\n")
    out.append("| Juíza | Consistência (geral) | Consistência (todas as dimensões) |\n|---|---|---|")
    for j in juizas:
        por_chave = defaultdict(dict)
        for l in linhas:
            if l["juiza"] == j:
                por_chave[(l["empresa"], l["dimensao"])][l["ordem"]] = l["vencedor"]
        pares = [v for v in por_chave.values() if len(v) == 2]
        geral = [v for (e, d), v in por_chave.items() if d == "geral" and len(v) == 2]
        cons = lambda ps: (f"{sum(1 for p in ps if len(set(p.values())) == 1) / len(ps):.0%}" if ps else "-")
        out.append(f"| {j} | {cons(geral)} | {cons(pares)} |")

    # 3) concordância entre juízas (voto majoritário por juíza/empresa/dimensão sobre as 2 ordens)
    def voto(j, emp, dim):
        vs = [l["vencedor"] for l in linhas if l["juiza"] == j and l["empresa"] == emp and l["dimensao"] == dim]
        if not vs:
            return None
        c = Counter(vs).most_common()
        return c[0][0] if len(c) == 1 or c[0][1] > c[1][1] else "empate"
    empresas = sorted({l["empresa"] for l in linhas})
    out.append("\n## Concordância entre juízas (alpha de Krippendorff, nominal)\n")
    out.append("| Dimensão | alpha |\n|---|---|")
    votos = {}
    for dim in dims:
        unidades = []
        for emp in empresas:
            u = [voto(j, emp, dim) for j in juizas]
            votos[(emp, dim)] = u
            unidades.append(u)
        out.append(f"| {dim} | {krippendorff_alpha_nominal(unidades)} |")

    # 4) humanos (opcional): CSV com colunas empresa,avaliador,dimensao,vencedor(sistema|b1|empate)
    if humanos_csv and os.path.exists(humanos_csv):
        with open(humanos_csv, encoding="utf-8") as f:
            hum = list(csv.DictReader(f))
        out.append("\n## Concordância juízas × humanos\n")
        out.append("| Dimensão | Empresas com humanos | Concordância maioria juízas × maioria humanos | alpha (juízas + humanos) |\n|---|---|---|---|")
        for dim in dims:
            acertos, total, unidades = 0, 0, []
            for emp in sorted({h["empresa"] for h in hum}):
                hv = [h["vencedor"] for h in hum if h["empresa"] == emp and h["dimensao"] == dim]
                jv = [v for v in votos.get((emp, dim), []) if v]
                if not hv or not jv:
                    continue
                maj = lambda vs: Counter(vs).most_common(1)[0][0]
                acertos += maj(hv) == maj(jv)
                total += 1
                unidades.append(jv + hv)
            out.append(f"| {dim} | {total} | {(acertos / total if total else 0):.0%} | {krippendorff_alpha_nominal(unidades)} |")

    texto = "\n".join(out) + "\n"
    with open(os.path.join(saida, "resumo.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resultados", default="resultados")
    parser.add_argument("--saida", default="resultados/juizes")
    parser.add_argument("--modelos", default=PADRAO_JUIZAS)
    parser.add_argument("--humanos", default="avaliacao/respostas_harmonie.csv")
    parser.add_argument("--so-analise", action="store_true")
    args = parser.parse_args()
    if not args.so_analise:
        executar_julgamentos(args.resultados, [m.strip() for m in args.modelos.split(",")], args.saida)
    analisar(args.saida, args.humanos)


if __name__ == "__main__":
    main()
