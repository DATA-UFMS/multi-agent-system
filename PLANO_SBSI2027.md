# Plano de trabalho — Agents-Mkt para o SBSI 2027

**Prazo:** janela de submissão 21–28/09/2026 (confirmar se o PDF completo tem data separada).
**Quem faz o quê:** Vanessa executa e revisa; Claude escreve código, harness de avaliação e texto.
**Objetivo:** transformar a prova de conceito (n=2, avaliada pelos autores) em uma avaliação
comparativa defensável na trilha de pesquisa.

## Diagnóstico honesto do artigo atual

- Contribuição percebida pelo revisor: engenharia; evidência: anedótica (2 execuções).
- Diagnóstico é baseado em regras triviais (H1, <300 palavras, >3 s, <25 anúncios); o LLM só
  formula perguntas e redige. Sem baseline, não há como mostrar o que a arquitetura acrescenta.
- RQ atual não é testável. Método ("pesquisa aplicada exploratória") frágil → reenquadrar como
  Design Science Research (DSR).
- Trabalhos relacionados fracos (TCCs, McKinsey). Faltam multiagentes com LLM, LLM-as-judge, DSR.
- Modelo obsoleto (gpt-4-turbo-preview), falha do Intérprete em 1 de 2 execuções, sem
  rastreabilidade das fontes do RAG, tempo/custo sem repetição.

## Desenho da avaliação (versão que cabe em 12 dias)

| Elemento | Decisão |
|---|---|
| Empresas | 6 PMEs com site público (Harmonie + Prolaje + 4 novas, setores distintos), anonimizadas |
| Condições | **Sistema** (multiagente + regras + RAG) vs. **B1** (um único LLM, mesmo modelo, mesmos dados coletados, mesma estrutura de relatório) |
| Repetições | 1 por condição; +1 repetição do sistema para variância de tempo/custo |
| Juízas LLM | 3 modelos de famílias diferentes do gerador; comparação pareada cega, ordem A/B invertida; rubrica fixa de 5 dimensões |
| Humanos | 3 pessoas da Harmonie avaliam os 2 relatórios da própria clínica (cegos), mesma rubrica + 4 itens de utilidade percebida (TTF). Serve para calibrar as juízas |
| Métricas | taxa de vitória por dimensão, consistência de posição, concordância entre juízas (alpha de Krippendorff), concordância juízas × humanos |
| Custo estimado | < US$ 15 no total |

**RQ nova (testável):** o diagnóstico dirigido por regras com consulta a base curada (RAG) produz
recomendações mais aderentes ao contexto, mais específicas e mais fundamentadas do que um único
LLM com os mesmos dados?

## Cronograma

| Data | Etapa | Responsável |
|---|---|---|
| 16/09 (qua) | Plano; correções no código (rastreabilidade RAG, retry, modelo configurável, tempo/custo); baseline B1; runner em lote; harness das juízas; rubrica e formulário | Claude |
| 17/09 (qui) | Criar `.env` com `OPENROUTER_API_KEY`; instalar ambiente; rodar teste com a Harmonie; escolher 4 PMEs novas e preencher `avaliacao/empresas.json`; enviar formulário à Harmonie (retorno até 24/09) | Vanessa |
| 18–19/09 | `python run_lote.py` (sistema + B1, 6 empresas); `python juizes.py` | Vanessa roda; Claude confere saídas |
| 20–22/09 | Tabelas e figura de resultados; reescrita: Seção 3 (DSR), RQ, trabalhos relacionados, Seção 5 nova, 5.4 enxuta | Claude escreve; Vanessa revisa |
| 23–25/09 | Incorporar respostas da Harmonie; ajustes; abstract e conclusões | ambos |
| 26–27/09 | Revisão simulada como avaliador da trilha; correções finais | Claude → Vanessa |
| 28/09 | Submissão | Vanessa |

**Corte de segurança:** se a Harmonie não responder até 24/09, o artigo segue sem calibração
humana e a limitação é declarada em 5.4.

## Comandos (rodar no Terminal do Mac, dentro da pasta do repositório)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp ENV_EXEMPLO.txt .env
# depois editar .env e colocar a chave em OPENROUTER_API_KEY

# teste único (Harmonie)
python orquestrador_principal.py --url "<URL>" --termo "clinica dermatologica <cidade>" \
  --prompt "<texto>" --saida resultados/teste

# lote completo (sistema + baseline) e depois juízas
python run_lote.py --empresas avaliacao/empresas.json --saida resultados
python juizes.py --resultados resultados --saida resultados/juizes
```

## Riscos

1. **Scraper da Biblioteca de Anúncios da Meta** (seletor de classes ofuscadas): pode ter quebrado.
   Se falhar, o Analista continua com lista vazia; corrigimos o seletor ou declaramos a limitação.
2. **Identificadores de modelo na OpenRouter** mudam; conferir em https://openrouter.ai/models antes de rodar.
3. **Avaliação humana sem CEP**: avaliação de artefato por usuários-alvo, com consentimento e
   anonimização; registrar isso explicitamente no texto.
4. **Rede**: as execuções só funcionam no Terminal do Mac (o ambiente do Claude não alcança
   OpenRouter nem facebook.com).

## Entregáveis na pasta

- `config.py`, agentes ajustados, `orquestrador_principal.py` com `--saida` (JSON UTF-8 + Markdown, tempo por etapa, custo)
- `baseline_b1.py`, `run_lote.py`, `juizes.py`
- `avaliacao/rubrica.md`, `avaliacao/formulario_harmonie.md`, `avaliacao/empresas.json`
- `resultados/` (gerado nas execuções)
- `Artigo/` (novas seções, conforme avançarmos)
