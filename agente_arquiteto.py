import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError
from collections import defaultdict
import re
from urllib.parse import urljoin, urlparse


REDES = {
    "instagram": ("instagram.com/",),
    "whatsapp": ("wa.me/", "api.whatsapp.com", "whatsapp.com/send", "web.whatsapp.com"),
    "facebook": ("facebook.com/", "fb.com/"),
    "youtube": ("youtube.com/", "youtu.be/"),
    "linkedin": ("linkedin.com/",),
    "tiktok": ("tiktok.com/",),
}


async def _existe(page, url_recurso: str) -> bool:
    """Verifica se um recurso responde 200 (robots.txt, sitemap.xml)."""
    try:
        resp = await page.request.get(url_recurso, timeout=10000)
        return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def _num_abreviado(texto: str):
    """'12,5 mil' / '12.5K' / '1,2M' / '980' -> int."""
    m = re.search(r"([\d.,]+)\s*(mil|k|m|mi)?", texto.lower())
    if not m:
        return None
    n = m.group(1).replace(".", "").replace(",", ".") if m.group(2) else m.group(1).replace(".", "").replace(",", "")
    try:
        v = float(n)
    except ValueError:
        return None
    suf = m.group(2) or ""
    return int(v * (1000 if suf in ("mil", "k") else 1_000_000 if suf in ("m", "mi") else 1))


async def analisar_perfil_instagram(url: str) -> dict:
    """
    Coleta mínima para empresas sem site: lê as meta tags públicas do perfil do Instagram
    (og:title, og:description com seguidores/publicações). Não exige login; pode ser bloqueada.
    """
    resultado = {
        "url": url, "status": "Erro", "tipo_presenca": "perfil_instagram",
        "titulo": "", "meta_description": "", "meta_keywords": "", "tags_cabecalho": {},
        "contagem_palavras": 0, "imagens_sem_alt": [], "links_internos": 0, "links_externos": 0,
        "links_quebrados": [], "tempo_carregamento": 0, "mobile_friendly": True,
        "structured_data": [], "canonical_url": "", "meta_robots": "", "open_graph": {},
        "twitter_cards": {}, "performance_metrics": {}, "https": True,
        "robots_txt": None, "sitemap_xml": None, "redes_sociais_no_site": {},
        "perfil_social": {"rede": "instagram", "usuario": urlparse(url).path.strip("/").split("/")[0]},
    }
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR")
        page = await context.new_page()
        try:
            start = asyncio.get_event_loop().time()
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            resultado["tempo_carregamento"] = round(asyncio.get_event_loop().time() - start, 2)
            await page.wait_for_timeout(2500)
            og = {}
            for el in await page.query_selector_all("meta[property^='og:']"):
                prop, cont = await el.get_attribute("property"), await el.get_attribute("content")
                if prop and cont:
                    og[prop] = cont
            desc_el = await page.query_selector("meta[name='description']")
            desc = (await desc_el.get_attribute("content")) if desc_el else ""
            resultado["open_graph"] = og
            resultado["titulo"] = og.get("og:title", "")
            resultado["meta_description"] = og.get("og:description", "") or desc or ""
            texto = resultado["meta_description"]
            perfil = resultado["perfil_social"]
            m_seg = re.search(r"([\d.,]+\s*(?:mil|k|m|mi)?)\s*(?:seguidores|followers)", texto, re.I)
            m_pub = re.search(r"([\d.,]+\s*(?:mil|k|m|mi)?)\s*(?:publica[çc][õo]es|posts)", texto, re.I)
            perfil["seguidores"] = _num_abreviado(m_seg.group(1)) if m_seg else None
            perfil["publicacoes"] = _num_abreviado(m_pub.group(1)) if m_pub else None
            # bio: trecho após o "@usuario:" ou após as contagens, quando presente
            m_bio = re.search(r"(?:@[\w.]+\s*(?:no Instagram)?:?\s*[\"“]?)(.+)$", texto)
            perfil["bio"] = (m_bio.group(1).strip(' "”') if m_bio else "")
            perfil["contagens_encontradas"] = bool(m_seg or m_pub)
            if og or desc:
                resultado["status"] = "Sucesso"
                print(f"Agente Arquiteto - Perfil Instagram lido: {perfil}")
            else:
                resultado["status"] = "Erro: página do perfil sem metadados públicos (login exigido ou bloqueio)"
                print("Agente Arquiteto - Perfil Instagram sem metadados públicos.")
        except TimeoutError:
            resultado["status"] = "Timeout"
            print("Agente Arquiteto - Timeout no perfil Instagram")
        except Exception as e:  # noqa: BLE001
            resultado["status"] = f"Erro durante a análise: {e}"
            print(f"Agente Arquiteto - Erro -> {e}")
        finally:
            await browser.close()
    return resultado


async def analisar_seo_on_page(url: str) -> dict:
    """
    Agente Arquiteto: Responsável por realizar uma análise de SEO do site fornecido.
    Ao executá-lo individualmente, recebe uma URL e retorna um JSON com os resultados da análise.
    """

    print("Agente Arquiteto - Iniciando execução")

    if "instagram.com" in urlparse(url).netloc.lower():
        return await analisar_perfil_instagram(url)

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
        "tipo_presenca": "site",          # "site" ou "perfil_instagram"
        "https": url.lower().startswith("https://"),
        "robots_txt": None,
        "sitemap_xml": None,
        "redes_sociais_no_site": {},
        "perfil_social": {},
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
            # Espera o evento "load" (até 45 s). Sites com chat/analytics nunca atingem
            # "networkidle", por isso ele é tentado depois, por no máximo 10 s, sem falhar.
            start_time = asyncio.get_event_loop().time()
            await page.goto(url, wait_until="load", timeout=45000)
            end_time = asyncio.get_event_loop().time()
            resultado["tempo_carregamento"] = round(end_time - start_time, 2)
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
                resultado["rede_ociosa"] = True
                # Métrica usada na prova de conceito original (tempo até a rede ficar ociosa).
                resultado["tempo_ate_rede_ociosa"] = round(asyncio.get_event_loop().time() - start_time, 2)
            except TimeoutError:
                resultado["rede_ociosa"] = False
                resultado["tempo_ate_rede_ociosa"] = None
            print(f"Página carregada (evento load) em {resultado['tempo_carregamento']} segundos; "
                  f"rede ociosa: {resultado['rede_ociosa']}.")

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

            # Redes sociais e canais de contato referenciados pelo site
            redes = {}
            for link in links:
                href = (await link.get_attribute("href")) or ""
                h = href.lower()
                for chave, padroes in REDES.items():
                    if chave not in redes and any(p in h for p in padroes):
                        redes[chave] = href
            resultado["redes_sociais_no_site"] = redes

            # robots.txt e sitemap.xml (requisições simples na mesma origem)
            origem = f"{parsed_url.scheme}://{parsed_url.netloc}"
            resultado["robots_txt"] = await _existe(page, origem + "/robots.txt")
            resultado["sitemap_xml"] = await _existe(page, origem + "/sitemap.xml")
            resultado["https"] = page.url.lower().startswith("https://")

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
