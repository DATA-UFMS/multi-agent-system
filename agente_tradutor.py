import sys
import os
import re
import json
import argparse
from openai import OpenAI, AuthenticationError
from fpdf import FPDF
from dotenv import load_dotenv

client = None


def corrigir_codificacao(texto_para_corrigir):
    """
    Faz algumas substituições de forma hard-coded para corrigir erros de codificação.
    """
    substituicoes = {
        "recomenda├º├Áes": "recomendações", "amplifica├º├úo": "amplificação",
        "otimiza├º├úo": "otimização", "posi├º├úo": "posição", "convers├úo": "conversão",
        "impress├Áes": "impressões", "a├º├úo": "ação", "inten├º├Áes": "intenções",
        "informa├º├Áes": "informações", "solu├º├úo": "solução", "manuten├º├úo": "manutenção",
        "aten├º├úo": "atenção", "institui├º├úo": "instituição", "gera├º├úo": "geração",
        "visualiza├º├úo": "visualização", "navega├º├úo": "navegação", "produ├º├úo": "produção",
        "exporta├º├úo": "exportação", "configura├º├úo": "configuração", "autentica├º├úo": "autenticação",
        "avalia├º├úo": "avaliação", "segmenta├º├úo": "segmentação", "colabora├º├úo": "colaboração",
        "personaliza├º├úo": "personalização", "integra├º├úo": "integração", "documenta├º├úo": "documentação",
        "comunica├º├úo": "comunicação", "implementa├º├úo": "implementação", "investiga├º├úo": "investigação",
        "obriga├º├úo": "obrigação", "preocupa├º├úo": "preocupação", "prote├º├úo": "proteção",
        "satisfa├º├úo": "satisfação", "utiliza├º├úo": "utilização", "verifica├º├úo": "verificação",

        "├í": "á", "├®": "é", "├¡": "í", "├│": "ó", "├ú": "ã", "├¬": "ê",
        "├ô": "Ó", "├û": "û", "├î": "î", "├ô": "ô", "├û": "û", "├│rio": "ório",
        "├âO": "ÃO", "├Áes": "ões", "├ã": "ã", "├õ": "õ", "├║": "ú", "├ë": "É",
        "├ï": "Í", "├ö": "Ó", "├£": "Ú", "├Ç": "Ç", "├ç": "ç", "├à": "à",
        "├è": "è", "├ì": "ì", "├ò": "ò", "├ù": "ù", "├ñ": "ñ", "├Ñ": "Ñ",

        "ag├¬ncia": "agência", "r├ípidas": "rápidas", "seguran├ºa": "segurança",
        "RELATôRIO": "RELATÓRIO", "esforºos": "esforços", "aquisiºão": "aquisição",
        "experi├¬ncia": "experiência", "rastre├ível": "rastreável", "impec├ível": "impecável",
        "m├│veis": "móveis", "acess├¡vel": "acessível", "estrat├®gicas": "estratégicas",
        "m├®tricas": "métricas", "conte├║do": "conteúdo", "an├ílise": "análise",
        "cr├¡tico": "crítico", "pr├íticas": "práticas", "avan├ºadas": "avançadas",
        "an├║ncios": "anúncios", "neg├│cio": "negócio", "efic├ícia": "eficácia",
        "tr├ífego": "tráfego", "per├¡odos": "períodos",

        "├º": "ç", "├ª": "Ç",
    }

    for errado, certo in substituicoes.items():
        texto_para_corrigir = texto_para_corrigir.replace(errado, certo)

    return texto_para_corrigir


def primeira_correcao(caminho_entrada):
    """
    Lê o arquivo, extrai o bloco 'relatorio_formatado' e aplica a correção hard-coded.
    Retorna o texto do relatório pré-corrigido e o conteúdo bruto do arquivo.
    """
    try:
        with open(caminho_entrada, 'r', encoding='latin-1') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {caminho_entrada}")
        return None, None

    conteudo = conteudo.replace('\x00', '').lstrip('\ufeff')

    token = 'relatorio_formatado": "'

    if token in conteudo:
        pre_relatorio, pos_relatorio = conteudo.split(token, 1)
        ultima_aspa = pos_relatorio.rfind('"')

        if ultima_aspa != -1:
            relatorio_bruto = pos_relatorio[:ultima_aspa]
        else:
            relatorio_bruto = pos_relatorio

        try:
            desescapado = json.loads(f'"{relatorio_bruto}"')
        except Exception:
            desescapado = relatorio_bruto.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')

        corr_pre = corrigir_codificacao(desescapado)

        return corr_pre, conteudo

    else:
        print("Erro: Token 'relatorio_formatado' não encontrado.")
        return corrigir_codificacao(conteudo), conteudo


def corrigir_com_gpt4(texto):
    global client

    if client is None:
        print("Erro: Cliente OpenAI não inicializado.")
        return None

    print("Chamando GPT-4 para correção.")

    modelo = "openai/gpt-4-turbo-preview"

    prompt_sistema = (
        "Você é um agente de correção de texto especializado em português brasileiro. "
        "Corrija acentuação e erros de codificação preservando o formato."
    )

    try:
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto}
            ],
            temperature=0.1,
        )
        return resposta.choices[0].message.content

    except AuthenticationError:
        print("Erro de autenticação.")
        return None
    except Exception as e:
        print(f"Erro ao chamar a API do GPT-4: {e}")
        return None


def extrair_conteudo_anexo(conteudo_bruto):
    anexos = []
    padrao = re.compile(r'"pergunta"\s*:\s*"(.*?)",\s*"recomendacao"\s*:\s*"(.*?)"', re.DOTALL)
    ocorrencias = padrao.finditer(conteudo_bruto)

    contador = 0
    for m in ocorrencias:
        contador += 1
        perg_raw = m.group(1)
        rec_raw = m.group(2)

        try:
            perg = json.loads(f'"{perg_raw}"')
        except json.JSONDecodeError:
            perg = perg_raw.replace('\\n', '\n')

        try:
            rec = json.loads(f'"{rec_raw}"')
        except json.JSONDecodeError:
            rec = rec_raw.replace('\\n', '\n')

        perg_corr = corrigir_codificacao(perg)
        rec_corr = corrigir_codificacao(rec)

        anexos.append(f"### PERGUNTA {contador}")
        anexos.append(perg_corr)
        anexos.append(f"\n### RECOMENDAÇÃO {contador}")
        anexos.append(rec_corr)
        anexos.append("\n---\n")

    if contador == 0:
        anexos.append("Nenhuma pergunta ou recomendação encontrada.")

    texto_anexo = "\n".join(anexos)

    with open("anexo_conteudo.txt", "w", encoding="utf-8") as f:
        f.write(texto_anexo)

    return texto_anexo


def gerar_pdf(texto_principal, texto_anexo, caminho_saida):
    print(f"Gerando PDF em {caminho_saida}.")

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            if self.page_no() == 1:
                self.cell(0, 10, 'Relatório de Diagnóstico', 0, 1, 'C')
            elif self.is_annex_page:
                self.cell(0, 10, 'Anexo: Detalhamento de Perguntas e Recomendações', 0, 1, 'C')

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        def corpo_capitulo(self, texto):
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 5, texto.encode('latin-1', 'replace').decode('latin-1'))
            self.ln()

        is_annex_page = False

    pdf = PDF()

    pdf.add_page()
    pdf.is_annex_page = False
    pdf.corpo_capitulo(texto_principal)

    pdf.add_page()
    pdf.is_annex_page = True
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Anexo', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    pdf.corpo_capitulo(texto_anexo)

    pdf.output(caminho_saida)
    print("PDF gerado com sucesso.")


def main():
    global client

    load_dotenv()

    chave = os.environ.get("OPENROUTER_API_KEY")
    base = "https://openrouter.ai/api/v1"

    if not chave:
        print("ERRO: Chave de API não encontrada.")
        sys.exit(1)

    client = OpenAI(api_key=chave, base_url=base)

    parser = argparse.ArgumentParser(description="Agente Tradutor")
    parser.add_argument("input_file", type=str)
    parser.add_argument("--md", action="store_true")
    args = parser.parse_args()

    arquivo_entrada = args.input_file
    salvar_md = args.md

    extensao = ".md" if salvar_md else ".pdf"
    caminho_saida = f"relatorio_final{extensao}"

    precorrigido, bruto = primeira_correcao(arquivo_entrada)
    if precorrigido is None:
        sys.exit(1)

    with open("saida_pre_corrigida.txt", "w", encoding="utf-8") as f:
        f.write(precorrigido)

    final_corrigido = corrigir_com_gpt4(precorrigido)
    if final_corrigido is None:
        sys.exit(1)

    with open("saida_corrigida.txt", "w", encoding="utf-8") as f:
        f.write(final_corrigido)

    anexo_precorrigido = extrair_conteudo_anexo(bruto)

    print("Chamando GPT-4 para refinar anexo.")
    anexo_final = corrigir_com_gpt4(anexo_precorrigido)
    if anexo_final is None:
        anexo_final = anexo_precorrigido

    with open("anexo_saida.txt", "w", encoding="utf-8") as f:
        f.write(anexo_final)

    if salvar_md:
        conteudo_md = (
            f"{final_corrigido}\n\n---\n\n## Anexo \n\n{anexo_final}"
        )
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(conteudo_md)
        print(f"Relatório salvo como Markdown: {caminho_saida}")
    else:
        gerar_pdf(final_corrigido, anexo_final, caminho_saida)

    os.remove("saida_pre_corrigida.txt")
    os.remove("saida_corrigida.txt")
    os.remove("anexo_conteudo.txt")
    os.remove("anexo_saida.txt")


if __name__ == "__main__":
    main()
