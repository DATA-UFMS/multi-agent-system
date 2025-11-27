import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError
from collections import defaultdict
import re
from urllib.parse import urljoin, urlparse


async def analisar_seo_on_page(url: str) -> dict:
    """
    Agente Arquiteto: Responsável por realizar uma análise de SEO do site fornecido.
    Ao executá-lo individualmente, recebe uma URL e retorna um JSON com os resultados da análise.
    """

    print("Agente Arquiteto - Iniciando execução")

    resultado = {
        "url": url,
        "status": "Erro",
        "titulo": "",
        "meta_description": "",
        "meta_keywords": "",
        "tags_cabecalho": {},
        "contagem_palavras": 0,
        "imagens_sem_alt": [],
        "links_internos": 0,
        "links_externos": 0,
        "links_quebrados": [],
        "tempo_carregamento": 0,
        "mobile_friendly": False,
        "structured_data": [],
        "canonical_url": "",
        "meta_robots": "",
        "open_graph": {},
        "twitter_cards": {},
        "performance_metrics": {}
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, # True permite que a execução ocorra em segundo plano
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            viewport={"width": 1920, "height": 1080}
        )

        page = await context.new_page()

        try:
            # Medir tempo de carregamento
            start_time = asyncio.get_event_loop().time()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            end_time = asyncio.get_event_loop().time()

            resultado["tempo_carregamento"] = round(end_time - start_time, 2)
            print(f"Página carregada em {resultado['tempo_carregamento']} segundos.")

            await page.wait_for_timeout(3000)

            # Título
            titulo_element = await page.query_selector("title")
            if titulo_element:
                resultado["titulo"] = await titulo_element.inner_text()

            # Meta description
            meta_desc = await page.query_selector("meta[name=\"description\"]")
            if meta_desc:
                resultado["meta_description"] = await meta_desc.get_attribute("content") or ""

            # Keywords
            meta_keywords = await page.query_selector("meta[name=\"keywords\"]")
            if meta_keywords:
                resultado["meta_keywords"] = await meta_keywords.get_attribute("content") or ""

            # Robots
            meta_robots = await page.query_selector("meta[name=\"robots\"]")
            if meta_robots:
                resultado["meta_robots"] = await meta_robots.get_attribute("content") or ""

            # Canonical
            canonical = await page.query_selector("link[rel=\"canonical\"]")
            if canonical:
                resultado["canonical_url"] = await canonical.get_attribute("href") or ""

            # Open Graph
            og_tags = {}
            og_elements = await page.query_selector_all("meta[property^=\"og:\"]")
            for og_element in og_elements:
                property_name = await og_element.get_attribute("property")
                content = await og_element.get_attribute("content")
                if property_name and content:
                    og_tags[property_name] = content
            resultado["open_graph"] = og_tags

            # Twitter Cards
            twitter_tags = {}
            twitter_elements = await page.query_selector_all("meta[name^=\"twitter:\"]")
            for twitter_element in twitter_elements:
                name = await twitter_element.get_attribute("name")
                content = await twitter_element.get_attribute("content")
                if name and content:
                    twitter_tags[name] = content
            resultado["twitter_cards"] = twitter_tags

            # Headers
            tags_cabecalho = defaultdict(list)
            for i in range(1, 7):
                tag_name = f"h{i}"
                headers = await page.query_selector_all(tag_name)
                for header in headers:
                    text = await header.inner_text()
                    if text.strip():
                        tags_cabecalho[tag_name].append(text.strip())
            resultado["tags_cabecalho"] = dict(tags_cabecalho)

            # Contagem de palavras
            body_text = await page.evaluate(
                """
                () => {
                    const body = document.body;
                    if (!body) return '';
                    const clone = body.cloneNode(true);
                    const remove = clone.querySelectorAll('script, style, noscript, nav, header, footer');
                    remove.forEach(el => el.remove());
                    return clone.innerText || clone.textContent || '';
                }
                """
            )

            if body_text:
                words = re.findall(r'\b\w+\b', body_text.lower())
                resultado["contagem_palavras"] = len(words)

            # Imagens sem ALT
            imagens_sem_alt = []
            images = await page.query_selector_all("img")
            for img in images:
                alt_text = await img.get_attribute("alt")
                src = await img.get_attribute("src")
                if not alt_text or not alt_text.strip():
                    imagens_sem_alt.append(src or "SRC não encontrado")
            resultado["imagens_sem_alt"] = imagens_sem_alt

            # Links internos e externos
            links_internos = 0
            links_externos = 0

            parsed_url = urlparse(url)

            links = await page.query_selector_all("a[href]")
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    absolute_url = urljoin(url, href)
                    parsed_link = urlparse(absolute_url)

                    if parsed_link.netloc == parsed_url.netloc:
                        links_internos += 1
                    elif parsed_link.netloc:
                        links_externos += 1

            resultado["links_internos"] = links_internos
            resultado["links_externos"] = links_externos

            # Mobile friendly
            viewport_meta = await page.query_selector("meta[name=\"viewport\"]")
            if viewport_meta:
                viewport_content = await viewport_meta.get_attribute("content")
                if viewport_content and "width=device-width" in viewport_content:
                    resultado["mobile_friendly"] = True

            # Structured Data
            structured_data = []
            json_ld_scripts = await page.query_selector_all("script[type=\"application/ld+json\"]")
            for script in json_ld_scripts:
                try:
                    content = await script.inner_text()
                    if content.strip():
                        data = json.loads(content)
                        structured_data.append(data)
                except json.JSONDecodeError:
                    continue
            resultado["structured_data"] = structured_data

            # Performance metrics
            try:
                performance_metrics = await page.evaluate(
                    """
                    () => {
                        const nav = performance.getEntriesByType('navigation')[0];
                        if (nav) {
                            return {
                                dom_content_loaded: Math.round(nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart),
                                load_complete: Math.round(nav.loadEventEnd - nav.loadEventStart),
                                first_paint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                                first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                            };
                        }
                        return {};
                    }
                    """
                )
                resultado["performance_metrics"] = performance_metrics
            except Exception as e:
                print(f"Erro ao realizar a coleta: {e}")
                resultado["performance_metrics"] = {}

            resultado["status"] = "Sucesso"
            print("Agente Arquiteto - Análise concluída.")

        except TimeoutError:
            resultado["status"] = "Timeout"
            print("Agente Arquiteto - Timeout")
        except Exception as e:
            resultado["status"] = f"Erro durante a análise: {str(e)}"
            print(f"Agente Arquiteto - Erro -> {e}")
        finally:
            await browser.close()

        return resultado


async def main():
    url_uso = input("Digite a URL para análise (ex: https://ufms.br): ")

    if not url_uso:
        print("URL vazia.")
        return

    if not url_uso.startswith(("http://", "https://")):
        url_uso = "https://" + url_uso

    resultados = await analisar_seo_on_page(url_uso)

    nome_arquivo = f"seo_analysis_{urlparse(url_uso).netloc.replace('.', '_')}.json"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)

    print(f"\nAnálise salva em: {nome_arquivo}")

    print("\nResumo da Análise")
    print(f"Status: {resultados['status']}")
    print(f"Título: {resultados['titulo']}")
    print(f"Contagem de palavras: {resultados['contagem_palavras']}")
    print(f"Imagens sem ALT: {len(resultados['imagens_sem_alt'])}")
    print(f"Links internos: {resultados['links_internos']}")
    print(f"Links externos: {resultados['links_externos']}")
    print(f"Mobile-friendly: {resultados['mobile_friendly']}")
    print(f"Tempo de carregamento: {resultados['tempo_carregamento']}s")


if __name__ == "__main__":
    asyncio.run(main())
