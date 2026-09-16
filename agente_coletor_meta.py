
import asyncio
import json
import re
from playwright.async_api import async_playwright, TimeoutError

from config import HEADLESS

def anonimizar(texto: str) -> str:
    """Remove identificadores pessoais diretos dos textos de anúncios antes de armazená-los (LGPD)."""
    texto = re.sub(r'@[\w.]+', '@[perfil]', texto)
    texto = re.sub(r'\(?\b\d{2}\)?\s?\d{4,5}-?\d{4}\b', '[telefone]', texto)
    texto = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '[email]', texto)
    return texto


async def coletar_anuncios_meta(termo_busca: str):
    """
    Coleta dados de anúncios ativos para um termo de busca na Biblioteca de Anúncios da Meta (Facebook e Instagram).

    Caso chamado individualmente, solicita o termo de busca e entrega os dados em um arquivo JSON.
    """
    print(f"Iniciando coleta. Termo de busca: '{termo_busca}'")
    dados_anuncios = []

    async with async_playwright() as p:
        # HEADLESS=0 no .env abre a janela do navegador para depurar o seletor.
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = await context.new_page()

        url_busca = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BR&q={termo_busca.replace(' ', '%20' )}&search_type=keyword_unordered&media_type=all"

        try:
            await page.goto(url_busca, wait_until="networkidle", timeout=60000)
            print("Página carregada.")

            # Tenta fechar o pop-up de cookies
            try:
                # Seletor para o botão de aceitar cookies
                cookie_button_selector = "div[aria-label='Permitir todos os cookies']"
                print("Procurando por pop-up")
                await page.click(cookie_button_selector, timeout=5000)
                print("Pop-up de cookies fechado.")
            except TimeoutError:
                print("Nenhum pop-up de cookies encontrado.")

            print("Rolando a página para carregar mais anúncios.")
            for i in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print(f"Rolagem {i+1}/5")
                await page.wait_for_timeout(2000)
            seletor_card_anuncio = "div.x1plvlek.xryxfnj.x1gzqxud.x178xt8z"
            
            cards_anuncios = await page.query_selector_all(seletor_card_anuncio)
            print(f"Encontrados {len(cards_anuncios)} cards de anúncios.")

            if not cards_anuncios:
                print("Nenhum anúncio encontrado.")
                await browser.close()
                return []

            for card in cards_anuncios:
                anuncio = {}
                try:
                    # ID do Anúncio
                    id_element = (await card.query_selector("span:has-text('Library ID:')")
                                  or await card.query_selector("span:has-text('Identificação da biblioteca:')"))
                    anuncio['id'] = ((await id_element.inner_text()).split(':', 1)[-1].strip()
                                     if id_element else "Não encontrado")

                    # Texto do Anúncio (Copy)
                    copy_element = await card.query_selector("div._7jyr._a25-")
                    anuncio['texto'] = anonimizar(await copy_element.inner_text()) if copy_element else "Não encontrado"

                    # Criativo
                    img_element = await card.query_selector("img.x15mokao")
                    video_element = await card.query_selector("video")
                    if img_element:
                        anuncio['criativo_url'] = await img_element.get_attribute('src')
                        anuncio['tipo_criativo'] = 'Imagem'
                    elif video_element:
                        anuncio['criativo_url'] = await video_element.get_attribute('src')
                        anuncio['tipo_criativo'] = 'Vídeo'
                    else:
                        anuncio['criativo_url'] = "Não encontrado"
                        anuncio['tipo_criativo'] = "Não encontrado"

                    # Plataformas
                    platform_container = (await card.query_selector("div.x3nfvp2.x1e56ztr:has(span:text-is('Platforms'))")
                                          or await card.query_selector("div.x3nfvp2.x1e56ztr:has(span:text-is('Plataformas'))"))
                    if platform_container:
                         # Busca todas as imagens de ícones dentro do container de plataformas
                        platform_elements = await platform_container.query_selector_all("div.xtwfq29")
                        anuncio['plataformas'] = len(platform_elements)
                    else:
                        anuncio['plataformas'] = "Não especificado"


                    # Data de Início
                    date_element = (await card.query_selector("span:has-text('Started running on')")
                                    or await card.query_selector("span:has-text('Veiculação iniciada em')"))
                    if date_element:
                        txt = await date_element.inner_text()
                        anuncio['data_inicio'] = re.sub(r'^(Started running on|Veiculação iniciada em)\s*', '', txt).strip()
                    else:
                        anuncio['data_inicio'] = "Não encontrado"

                    # Call-to-Action (CTA)
                    cta_element = await card.query_selector("div[role='button'] div[dir='auto']")
                    anuncio['cta'] = await cta_element.inner_text() if cta_element else "Não encontrado"
                    
                    # Link de Destino
                    link_element = await card.query_selector("a[rel*='noopener']")
                    anuncio['link_destino'] = await link_element.get_attribute('href') if link_element else "Não encontrado"

                    dados_anuncios.append(anuncio)
                except Exception as e:
                    print(f"Erro ao processar um card, pulando. Detalhe: {e}")

        except Exception as e:
            print(f"Ocorreu um erro geral durante o scraping: {e}")
        finally:
            await browser.close()

    print(f"Coleta finalizada. Total de {len(dados_anuncios)} anúncios processados.")
    return dados_anuncios

async def main():
    termo_busca = input("Digite o termo de busca ou nome do anunciante (ex: Nike, Consultorio Odontologico): ")
    
    if not termo_busca:
        print("Termo de busca não pode ser vazio.")
        return

    resultados = await coletar_anuncios_meta(termo_busca)

    if resultados:
        nome_arquivo = f"anuncios_{termo_busca.replace(' ', '_').lower()}.json"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        print(f"\nDados salvos no arquivo: {nome_arquivo}")
        
        print("\nExemplo de anúncio coletado")
        print(json.dumps(resultados[0], indent=2, ensure_ascii=False))
    else:
        print("\nNenhum dado foi coletado.")

if __name__ == "__main__":
    asyncio.run(main())
