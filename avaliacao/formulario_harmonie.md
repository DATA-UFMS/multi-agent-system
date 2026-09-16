# Avaliação de relatórios de marketing digital — Clínica Harmonie

*(Texto pronto para colar em um Google Forms. Anexar os dois PDFs `Relatorio_A.pdf` e
`Relatorio_B.pdf`, gerados a partir de `resultados/A/sistema/rep1/relatorio.md` e
`resultados/A/b1/relatorio.md`, em ordem sorteada — registrar qual é qual em
`avaliacao/mapa_cego_harmonie.txt`, que fica só com a pesquisadora.)*

---

## Apresentação e consentimento

Você está sendo convidado(a) a avaliar dois relatórios de marketing digital produzidos
automaticamente para a Clínica Harmonie a partir de dados públicos do site e de anúncios.
A avaliação faz parte de uma pesquisa acadêmica da UFMS sobre sistemas de apoio à decisão para
pequenas e médias empresas. Leva de 15 a 20 minutos.

Suas respostas serão usadas de forma agregada e anônima; nenhum nome de pessoa será divulgado.
Você pode interromper a qualquer momento. Dúvidas: vanessa.a.borges@ufms.br.

- [ ] Li as informações acima e concordo em participar.

## Sobre você

1. Qual é a sua função na clínica? (resposta curta)
2. Você tem formação ou experiência profissional em marketing? ( ) Não ( ) Alguma ( ) Sim, formal
3. Com que frequência você participa de decisões sobre a divulgação da clínica?
   ( ) Nunca ( ) Às vezes ( ) Frequentemente ( ) Sou o(a) responsável

## Leia os dois relatórios (A e B) e avalie cada um

Para cada afirmação, dê uma nota de 1 (discordo totalmente) a 5 (concordo totalmente), para o
Relatório A e para o Relatório B.

| # | Afirmação | Relatório A (1–5) | Relatório B (1–5) |
|---|---|---|---|
| 4 | O relatório leva em conta a realidade da clínica (nosso pedido, o setor de dermatologia e a cidade). | | |
| 5 | As recomendações são concretas: dá para saber o que fazer primeiro e como. | | |
| 6 | As recomendações se apoiam nos dados apresentados sobre o site e os anúncios, e é possível ver de onde vieram. | | |
| 7 | O que o relatório afirma sobre o site e sobre os anúncios parece correto e coerente. | | |
| 8 | As ações são viáveis para a nossa equipe e o nosso orçamento, e o texto é fácil de entender. | | |

## Utilidade percebida (adaptado de Task–Technology Fit)

| # | Afirmação | Relatório A (1–5) | Relatório B (1–5) |
|---|---|---|---|
| 9 | Este relatório me ajudaria a decidir o que fazer no marketing digital da clínica. | | |
| 10 | As informações estão no nível de detalhe adequado para a decisão. | | |
| 11 | Eu confiaria nas recomendações para agir. | | |
| 12 | Eu usaria um relatório como este periodicamente (por exemplo, a cada trimestre). | | |

## Comparação direta

13. Em cada aspecto, qual relatório é melhor? (A / B / Empate)

| Aspecto | A | B | Empate |
|---|---|---|---|
| Considera a realidade da clínica | | | |
| Recomendações concretas e acionáveis | | | |
| Apoiado nos dados e nas fontes | | | |
| Correção do que afirma | | | |
| Viável para uma clínica pequena e fácil de entender | | | |
| **No geral, qual você escolheria para orientar os próximos 3 meses?** | | | |

## Abertas

14. O que faltou nos relatórios que você esperava ver? (opcional)
15. Alguma recomendação pareceu errada, inviável ou fora da realidade da clínica? Qual? (opcional)

---

### Como transcrever as respostas para `avaliacao/respostas_harmonie.csv`

Colunas: `empresa,avaliador,dimensao,vencedor`. Uma linha por avaliador e por aspecto da
questão 13, com `empresa=A`, `avaliador=h1|h2|h3`, `dimensao` em
`contexto|acionabilidade|fundamentacao|correcao|adequacao_pme|geral` e `vencedor` em
`sistema|b1|empate` (converter A/B usando o `mapa_cego_harmonie.txt`). As notas 1–5 (questões
4–12) vão para `avaliacao/notas_harmonie.csv` com colunas `avaliador,item,relatorio,nota`.
