"""
Executa o sistema (multiagente) e o baseline B1 para uma lista de empresas.

  python run_lote.py --empresas avaliacao/empresas.json --saida resultados [--repeticoes 2] [--so-b1]

Estrutura de saída:
  resultados/<id>/sistema/rep1/{execucao.json, relatorio.md}
  resultados/<id>/b1/{execucao.json, relatorio.md}
  resultados/resumo.csv
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import traceback

from orquestrador_principal import OrquestradorPrincipal, salvar_resultado
from baseline_b1 import executar_baseline
from config import uso_da_chave_usd


def _linha_resumo(emp_id, condicao, rep, execucao, caminho):
    e = execucao or {}
    t = e.get("tempos_s", {})
    return {
        "empresa": emp_id, "condicao": condicao, "repeticao": rep,
        "tempo_total_s": t.get("total"), "tempo_interpretacao_s": t.get("interpretacao"),
        "tempo_coleta_s": t.get("coleta"), "tempo_analise_s": t.get("analise"),
        "tempo_relatorio_s": t.get("relatorio"), "custo_usd": e.get("custo_usd"),
        "interprete_status": e.get("interprete_status"), "seo_status": e.get("seo_status"),
        "pagespeed_status": e.get("pagespeed_status"), "pagespeed_campo": e.get("pagespeed_campo"),
        "n_anuncios": e.get("n_anuncios_coletados"), "n_problemas": e.get("n_problemas"),
        "n_oportunidades": e.get("n_oportunidades"), "n_recomendacoes": e.get("n_recomendacoes"),
        "n_recomendacoes_com_fontes": e.get("n_recomendacoes_com_fontes"),
        "n_falhas_tratadas": len(e.get("falhas_tratadas", []) or []),
        "caminho": caminho,
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--empresas", default="avaliacao/empresas.json")
    parser.add_argument("--saida", default="resultados")
    parser.add_argument("--repeticoes", type=int, default=1, help="repetições do sistema por empresa")
    parser.add_argument("--so-b1", action="store_true", help="só roda o baseline a partir de execuções salvas")
    args = parser.parse_args()

    with open(args.empresas, encoding="utf-8") as f:
        empresas = json.load(f)
    pendentes = [e["id"] for e in empresas if "PREENCHER" in json.dumps(e)]
    if pendentes:
        raise SystemExit(f"empresas.json ainda tem campos PREENCHER nas empresas {pendentes}; preencha antes de rodar.")

    custo_inicial = uso_da_chave_usd()
    linhas = []
    for emp in empresas:
        emp_id = emp["id"]
        print(f"\n{'=' * 70}\nEMPRESA {emp_id} ({emp.get('setor', '')})\n{'=' * 70}")

        if not args.so_b1:
            for rep in range(1, args.repeticoes + 1):
                pasta = os.path.join(args.saida, emp_id, "sistema", f"rep{rep}")
                try:
                    orq = OrquestradorPrincipal()
                    resultado = await orq.executar_analise_completa(emp["url"], emp["termo"], emp["prompt"])
                    salvar_resultado(resultado, pasta)
                    linhas.append(_linha_resumo(emp_id, "sistema", rep, resultado.get("execucao"), pasta))
                except Exception as e:  # noqa: BLE001
                    traceback.print_exc()
                    linhas.append({**_linha_resumo(emp_id, "sistema", rep, None, pasta), "erro": str(e)})

        # B1 usa os dados coletados na primeira repetição do sistema (mesma entrada).
        caminho_dados = os.path.join(args.saida, emp_id, "sistema", "rep1", "execucao.json")
        if os.path.exists(caminho_dados):
            pasta_b1 = os.path.join(args.saida, emp_id, "b1")
            try:
                with open(caminho_dados, encoding="utf-8") as f:
                    exec_sistema = json.load(f)
                res_b1 = executar_baseline(emp["url"], emp["termo"], emp["prompt"], exec_sistema["dados_coletados"])
                os.makedirs(pasta_b1, exist_ok=True)
                with open(os.path.join(pasta_b1, "execucao.json"), "w", encoding="utf-8") as f:
                    json.dump(res_b1, f, indent=2, ensure_ascii=False)
                with open(os.path.join(pasta_b1, "relatorio.md"), "w", encoding="utf-8") as f:
                    f.write(res_b1["relatorio_formatado"])
                linhas.append(_linha_resumo(emp_id, "b1", 1, res_b1.get("execucao"), pasta_b1))
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                linhas.append({**_linha_resumo(emp_id, "b1", 1, None, pasta_b1), "erro": str(e)})
        else:
            print(f"Sem execução do sistema para {emp_id}; B1 não executado.")

    custo_final = uso_da_chave_usd()
    if custo_inicial is not None and custo_final is not None:
        total = round(custo_final - custo_inicial, 4)
        n = len(linhas) or 1
        print(f"\nCusto total do lote (contador da chave): US$ {total} em {n} execuções "
              f"(média US$ {total / n:.4f}). O custo por execução no CSV é aproximado: o contador da plataforma "
              f"atualiza com atraso; use o total do lote no artigo.")
        with open(os.path.join(args.saida, "custo_lote.json"), "w", encoding="utf-8") as f:
            json.dump({"custo_total_usd": total, "n_execucoes": n, "custo_medio_usd": round(total / n, 4)}, f, indent=2)

    os.makedirs(args.saida, exist_ok=True)
    caminho_csv = os.path.join(args.saida, "resumo.csv")
    campos = sorted({k for l in linhas for k in l})
    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f"\nResumo salvo em {caminho_csv}")


if __name__ == "__main__":
    asyncio.run(main())
