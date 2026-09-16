# Rubrica de avaliação dos relatórios

Usada igualmente pelas juízas LLM (`juizes.py`) e pelos avaliadores humanos, para permitir o
cálculo de concordância. Cada dimensão recebe uma nota de 1 a 5 por relatório e um veredito
comparativo (A, B ou empate).

| Dimensão | O que observar | 1 (fraco) | 5 (forte) |
|---|---|---|---|
| **Aderência ao contexto** | O relatório leva em conta a necessidade, o setor e a localidade que a empresa informou? | Conselhos genéricos que serviriam para qualquer negócio | Recomendações claramente ligadas ao pedido, ao setor e à cidade informados |
| **Especificidade e acionabilidade** | Dá para saber o que fazer na segunda-feira? | Frases vagas ("melhore o SEO", "invista em conteúdo") | Ações concretas, priorizadas, com o que/como/por quê |
| **Fundamentação** | As recomendações se apoiam nos dados coletados do site e dos anúncios e/ou em fontes identificáveis? | Afirmações sem relação com os dados apresentados | Cada recomendação se conecta a um dado observado ou a uma fonte nomeada |
| **Correção técnica** | O que é dito sobre SEO, anúncios e desempenho está correto e coerente com os dados? | Erros técnicos ou números inventados | Sem erros; números batem com os dados coletados |
| **Adequação a PME** | É viável com recursos limitados e compreensível para quem não é de marketing? | Exige agência, orçamento alto ou jargão técnico | Viável com equipe pequena; linguagem clara para o gestor |

**Veredito geral:** qual relatório você escolheria para orientar as decisões da empresa nos
próximos 3 meses? (A, B ou empate)

## Instruções para os avaliadores humanos

- Os relatórios são identificados apenas como A e B; a ordem foi sorteada.
- Não há resposta certa: registre sua percepção como gestor(a) da empresa.
- Não considere tamanho ou formatação como critério em si.
- Tempo estimado: 15–20 minutos.
