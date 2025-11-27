[ Ahrefs  ](/)

Product 

[ Search marketing ](/search-marketing)

[ Site Explorer  Study your competitors' websites.  ](/site-explorer) [ Keywords Explorer  Learn what your customers are searching for.  ](/keywords-explorer) [ Rank Tracker  Monitor your rankings in search engines.  ](/rank-tracker) [ Brand Radar  Track your brand's visibility in LLMs.  ](/brand-radar)

[ Website performance ](/website-performance)

[ Site Audit  Audit & optimize your website.  ](/site-audit) [ Web Analytics  Get insights about your website's traffic.  ](/web-analytics)

[ Content marketing ](/content-marketing)

[ Content Explorer  Track your web mentions & find link prospects.  ](/content-explorer) [ AI Content Helper  Improve your content with AI.  ](/ai-content-helper) [ Social Media Manager  Schedule, edit, and manage social media from one place.  ](/social-media-manager)

[ Reporting ](/reporting)

[ Dashboard  Track performance and progress across projects.  ](/dashboard) [ Portfolios  Monitor the performance of multiple URLs.  ](/portfolios) [ Report Builder  Measure your work’s impact, and showcase its value.  ](/report-builder)

[ Local SEO ](/local-seo)

[ GBP Monitor  New  Manage Google Business Profiles at scale.  ](/gbp-monitor)

What's new 

[ Ahrefs Certification: What To Expect and How It Works ↗ ](https://ahrefs.com/blog/ahrefs-certification/)

March 2025 

[ Use Cases ](/use-cases)

[ Competitive Intelligence  ](/use-cases/competitive-intelligence) [ PPC  ](/use-cases/ppc) [ SEO  ](/use-cases/seo) [ Content Marketing  ](/use-cases/content-marketing) [ Brand Marketing  ](/use-cases/brand-marketing)

[ Discover all tools → ](/all)

[ Our data ](/big-data)

Resources 

Learn Ahrefs 

[ Help Center  Browse bite-sized tutorials, FAQs, and best practices.  ](https://help.ahrefs.com) [ How to use Ahrefs  Learn practical ways to use Ahrefs’ tools and reports.  ](/academy/how-to-use-ahrefs) [ Ahrefs Certification  Turn your Ahrefs knowledge into a tangible credential.  ](/certification) [ What’s new?  See all the latest product features and improvements.  ](https://ahrefs.com/blog/category/product-blog/)

Learn marketing 

[ Blog  Expand your marketing knowledge.  ](https://ahrefs.com/blog/) [ Academy  Get better at digital marketing with our free video courses.  ](/academy) [ Podcast  Get first-hand insights from the world of digital marketing.  ](/podcast) [ Ahrefs on YouTube  Watch actionable digital marketing tutorials.  ](https://www.youtube.com/c/AhrefsCom)

Misc 

[ Agency Directory  Find a perfect match for your project.  ](/agencies) [ Top Websites  See top ranking websites by Ahrefs traffic estimates.  ](/websites) [ Events  Explore Ahrefs events happening near you.  ](/events) [ Testimonials  Read what users love most about our tools.  ](/reviews)

Free tools 

[ SEO Tools  ](/free-seo-tools) [ AI Writing Tools  ](/writing-tools) [ SEO Browser Extension  ](/seo-toolbar)

[ Word Count ↗ ](https://wordcount.com)

[ Pricing ](/pricing)

[ Enterprise ](/enterprise)

[ Evolve  ](https://ahrefsevolve.com?utm_source=ahrefs_website&utm_medium=menu)

[ Sign in ](//app.ahrefs.com/user/login)

Ahrefs 

[ SEO Glossary  /  ](//ahrefs.com/seo/glossary)

[ Holistic SEO  ](//ahrefs.com/seo/glossary/holistic-seo)

#  Hreflang 

##  What is Hreflang? 

Hreflang is an HTML attribute that informs search engines about the multiple versions of a page for different languages or regions. 

It helps Google to serve the correct localized version to the searchers. 

There are three ways to apply the hreflang attribute: 

  * HTML tags 
  * HTTP headers 
  * Sitemaps 



Here’s how hreflang is implemented in the HTML code of our blog homepage: 

` <link rel="alternate" href="https://ahrefs.com/blog/" hreflang="x-default">   
<link rel="alternate" href="https://ahrefs.com/blog/" hreflang="en">   
<link rel="alternate" href="https://ahrefs.com/blog/zh/" hreflang="zh-Hans">   
<link rel="alternate" href="https://ahrefs.com/blog/ru/" hreflang="ru">   
<link rel="alternate" href="https://ahrefs.com/blog/de/" hreflang="de">   
<link rel="alternate" href="https://ahrefs.com/blog/es/" hreflang="es">   
<link rel="alternate" href="https://ahrefs.com/blog/it/" hreflang="it"> `

##  Why is hreflang important for SEO? 

Hreflang is important for SEO because it helps search engines discover and serve the relevant localized version of your pages based on the user’s language and/or region. 

It’s one of the crucial components of international SEO while expanding your online presence in multiple countries. 

Moreover, the group of hreflang pages shares each other’s ranking signals. 

According to the explanation from Google’s Gary Illyes, the page that is the best match will determine the ranking position, but the most relevant page for a user will be shown in the SERPs. 

Thus, hreflang tags can impact your rankings directly. 

Besides, hreflang is also one of the effective ways to resolve [ duplicate content ](https://ahrefs.com/blog/duplicate-content/) issues on your site. Let’s say you’re targeting the audience in the US and UK with two different versions of the same page. 

Apart from minor differences like some spellings, currencies, etc., the rest of the content on both pages will be identical. So you need to signal Google about two different versions with hreflang.   
![minor differences between US and GB pages](https://ahrefs.com/blog/wp-content/uploads/2019/12/hreflang-image.png)

Without the hreflang attribute, Google may see these pages as duplicates and index only one of them. As a result, the other page wouldn’t get visibility and traffic. 

##  Hreflang best practices 

Now, let’s understand some best practices to implement hreflang tags correctly. 

###  1\. Always use self-referencing hreflang tag 

Whenever you apply hreflang tags on a page, ensure that you’ve added a self-referencing hreflang link to that page.   
For example, your site has the following English and Italian versions of a page: 

https://example.com/hello and https://example.com/ciao 

In addition to   
` <link rel="alternate" hreflang="it" href="https://example.com/ciao" /> `   
the English version must also refencence itself   
` <link rel="alternate" hreflang="en" href="https://example.com/hello" /> `

![image explaining how self-referencing hreflang links work](https://ahrefs.com/blog/wp-content/uploads/2020/03/how-self-referential-hreflangs-work.png)

Although some SEOs argue that it’s an optional practice, [ Google’s guidelines ](https://developers.google.com/search/docs/advanced/crawling/localized-versions) say it’s a must. 

###  2\. Make sure the language and region codes are valid 

[ Googlebot ](https://ahrefs.com/seo/glossary/googlebot) identifies the value of the hreflang attribute with the help of language and region codes. Google-approved format for language code is [ ISO 639-1 ](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) and [ ISO 3166-1 Alpha 2 ](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for region code. 

While the language code is mandatory, the region code is optional in the hreflang attribute. So, if you’ve specified only one code, Google considers it language code by default. Hence, you must use the correct format for codes. 

For example, if you’re targeting the UK, the language-location code must be **en-gb** , not **en-uk** . 

###  3\. Add “x-default” tag for unmatched languages 

The hreflang **x-default** tag tells Google that the page is for every other language that is not specified in the hreflang section. 

Simply put, it acts as a fallback page to be shown to users that don’t match the specified language codes. It’s not a mandatory practice, but Google recommends it. 

It looks like this:   
` <link rel="alternate" hreflang="x-default" href="https://example.com/" /> `

###  4\. The set of hreflang tags must be identical on all page versions 

The easiest way to ensure the accuracy of hreflang tags is to check whether tags are identical across all page versions. 

In other words, every page in the group must have the exact same set of hreflang links. 

Getting back to our blog homepage example, it has six language versions, and each localized version has the **exact same** set of 7 hreflang links (6 languages + x-default). 

##  FAQs 

###  How to generate hreflang tags? 

Although everyone can write the hreflang tag manually, there are tools like [ Hreflang Tags Generator ](https://www.aleydasolis.com/english/international-seo-tools/hreflang-tags-generator/) that help you generate it automatically. You can just fill in the details, and it’ll provide you with the correct hreflang tags for your pages. 

###  How to find hreflang issues? 

If you want to find the hreflang issues for individual pages, you can use the [ Hreflang Tags Testing Tool ](https://technicalseo.com/tools/hreflang/) . But if you want to check the hreflang issues for your entire site, it’s better to use Ahrefs [ Site Audit ](https://ahrefs.com/site-audit) . It’ll crawl all the pages on your site, highlight all the issues (including hreflang issues), and provide detailed reports. 

[ HTTP 200 Response Code  ](//ahrefs.com/seo/glossary/http-200)

Starter 

See what people search and spy on competitors. 

![](/assets/esbuild/sparkles-YB3DPL4I.svg)

$ 

29 

/  mo 

[ Get started  ](/signup?interval=monthly&plan=trial&utm_source=glossary)

Webmaster Tools 

Get Ahrefs data on your site and fix what matters. 

![](/assets/esbuild/rocket-empty-ZUC5GJET.svg)

Free  [ Get started  ](/signup?utm_source=glossary&plan=awt)

[ Holistic SEO  ](//ahrefs.com/seo/glossary/holistic-seo)

[ HTTP 200 Response Code  ](//ahrefs.com/seo/glossary/http-200)

Language 

English 

Core tools 

[ Brand Radar  ](/brand-radar)

[ Dashboard  ](/dashboard)

[ Site Explorer  ](/site-explorer)

[ Keywords Explorer  ](/keywords-explorer)

[ Site Audit  ](/site-audit)

[ Rank Tracker  ](/rank-tracker)

[ Content Explorer  ](/content-explorer)

[ Web Analytics  ](/web-analytics)

[ GBP Monitor  ](/gbp-monitor)

[ Use cases →  ](/use-cases)

[ Competitive Intelligence  ](/use-cases/competitive-intelligence)

[ SEO  ](/use-cases/seo)

[ PPC  ](/use-cases/ppc)

[ Content Marketing  ](/use-cases/content-marketing)

[ Brand Marketing  ](/use-cases/brand-marketing)

[ Alternatives →  ](/vs)

[ Ahrefs vs Semrush  ](/vs/semrush)

[ Free SEO tools →  ](/free-seo-tools)

[ Webmaster Tools  ](/webmaster-tools)

[ Backlink Checker  ](/backlink-checker)

[ Broken Link Checker  ](/broken-link-checker)

[ Website Authority Checker  ](/website-authority-checker)

[ Keyword Generator  ](/keyword-generator)

[ YouTube Keyword Tool  ](/youtube-keyword-tool)

[ Amazon Keyword Tool  ](/amazon-keyword-tool)

[ Bing Keyword Tool  ](/bing-keyword-tool)

[ SERP Checker  ](/serp-checker)

[ SEO Toolbar  ](/seo-toolbar)

[ WordPress Plugin  ](/wordpress-seo-plugin)

[ Keyword Rank Checker  ](/keyword-rank-checker)

[ Keyword Difficulty Checker  ](/keyword-difficulty)

[ Website Checker  ](/website-checker)

[ AI Writing tools  ](/writing-tools)

[ SEO Audit Tool  ](/seo-audit-tool)

Extra tools & features 

[ Domain Comparison  ](/domain-comparison)

[ Batch Analysis  ](/batch-analysis)

[ Link Intersect  ](/link-intersect)

[ Content Gap  ](/content-gap)

[ Email Alerts  ](/alerts)

[ SEO Checker  ](/seo-checker)

[ Word Count  ](https://wordcount.com)

[ Grammar Checker  ](https://wordcount.com/grammar-checker)

[ Traffic Checker  ](/traffic-checker)

[ Looker Studio Connectors  ](/google-data-studio-connectors)

[ Top Websites  ](/websites)

[ SEO Reporting  ](/seo-reporting)

[ AI Content Helper  ](/ai-content-helper)

[ Patches  ](/patches)

[ Portfolios  ](/portfolios)

[ IndexNow  ](/index-now)

Product 

[ Pricing  ](/pricing)

[ Our data  ](/big-data)

[ AhrefsBot  ](/robot)

[ API  ](https://docs.ahrefs.com/docs/api/reference/introduction)

[ Enterprise  ](/enterprise)

[ What’s new?  ](https://ahrefs.com/blog/category/product-blog/)

Company 

[ About  ](/about)

[ Team  ](/team)

[ Jobs  ](/jobs)

[ Media kit  ](/media-kit)

[ Contact us  ](/cdn-cgi/l/email-protection#1d6e686d6d726f695d7c756f787b6e337e7270)

[ Legal info  ](/legal)

[ Privacy Policy  ](/legal/privacy-policy)

[ Events  ](/events)

[ Testimonials  ](/reviews)

Resources 

[ Blog  ](https://ahrefs.com/blog/)

[ Tech blog  ](https://tech.ahrefs.com)

[ Podcast  ](/podcast)

[ SEO Guide  ](/seo)

[ Help center  ](https://help.ahrefs.com/)

[ Academy  ](/academy)

[ Marketing Agencies  ](/agencies)

[ Digest  ](/newsletter)

Social 

[ Twitter  ](https://x.com/ahrefs)

[ Youtube  ](https://www.youtube.com/c/AhrefsCom)

[ Instagram  ](https://www.instagram.com/ahrefs)

[ Facebook  ](https://www.facebook.com/Ahrefs)

[ Linkedin  ](https://www.linkedin.com/company/ahrefs/)

© 2025 Ahrefs Pte. Ltd. (201227417H) 16 Raffles Quay, #33-03 Hong Leong Building, Singapore 048581 

[ ](https://help.ahrefs.com/?mtm_campaign=floating-help-btn)
