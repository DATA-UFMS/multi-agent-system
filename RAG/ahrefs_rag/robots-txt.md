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

[ Rich Snippet  ](//ahrefs.com/seo/glossary/rich-snippet)

#  Robots.txt 

##  What is Robots.txt? 

A robots.txt file restricts [ web crawlers ](https://ahrefs.com/seo/glossary/crawler) , such as search engine bots, from accessing specific URLs on a website. Also, it can be used to adjust the crawling speed for some web crawlers. 

All “good” web crawlers adhere to the rules specified in the robots.txt file. However, there are “bad” unregistered crawlers, often utilized for scraping purposes, that completely disregard the robots.txt file. 

The robots.txt file must be used to reduce/optimize crawler traffic to a website and it should not be used to control [ indexing ](https://ahrefs.com/seo/glossary/indexability) of web pages. Even if a URL is disallowed in robots.txt, it can still be indexed by Google if it’s discovered via an external link. 

The syntax of the robots.txt file contains the following fields: 

  * user-agent: the crawler the rules apply to 
  * disallow: a path that must not be crawled 
  * allow: a path that can be crawled (optional) 
  * sitemap: location of the sitemap file (optional) 
  * crawl-delay: controls the crawling speed (optional and not supported by [ GoogleBot ](https://ahrefs.com/seo/glossary/googlebot) ) 



Here’s an example: 

` User-agent: AhrefsSiteAudit   
Disallow: /resources/   
Allow: /resources/images/   
Crawl-delay: 2 `

Sitemap: https://ahrefs.com/academy/sitemap.xml 

This robots.txt file instructs AhrefsSiteAudit crawler not to crawl URLs in the “/resources/” directory except for those in “/resources/images/” and sets the delay between the requests to 2 seconds. 

##  Why is the robots.txt file important? 

The robots.txt file is important because it enables webmasters to control the behavior of crawlers on their websites, optimizing the [ crawl budget ](https://ahrefs.com/seo/glossary/crawl-budget) and restricting the crawling of website sections that are not intended for public access. 

Many website owners choose to noindex certain pages such as author pages, login pages, or pages within a membership site. They may also block the crawling and indexing of gated resources like PDFs or videos that require an email opt-in to access. 

It’s worth noting that if you use a CMS like WordPress, the /wp-admin/ login page is automatically blocked from being indexed by crawlers. 

However, it’s important to note that Google does not recommend relying solely on the robots.txt file to control the indexing of pages. And if you’re making changes to a page, such as adding a “noindex” tag, make sure the page is not disallowed in the robots.txt. Otherwise, Googlebot won’t be able to read it and update its index in a timely manner. 

##  FAQs 

###  What happens if I don’t have a robots.txt file? 

Most sites don’t absolutely require a robots.txt file. The purpose of a robots.txt file is to communicate specific instructions to search bots, but this may not be necessary if you have a smaller website or one without a lot of pages that you need to block from the search crawlers. 

With that said, there’s also no downside to creating a robots.txt file and having it live on your website. This will make it easy to add directives if you need to do so in the future. 

###  Can I hide a page from search engines using robots.txt? 

Yes. Hiding pages from search engines is one of the primary functions of a robots.txt file. You can do this with the disallow parameter and the URL you want to block. 

However, it’s important to note that simply hiding a URL from Googlebot using the robots.txt file does not guarantee that it won’t be indexed. In some cases, a URL may still be indexed based on factors such as the text of the URL itself, the [ anchor text ](https://ahrefs.com/seo/glossary/anchor-text) used in external links, and the context of the external page where the URL was discovered. 

###  How to test my robots.txt file? 

You can validate your robots.txt file and test how the instructions work on specific URLs using [ robots.txt tester ](https://www.google.com/webmasters/tools/robots-testing-tool) in Google Search Console or using external validators, like [ the one from Merkle ](https://technicalseo.com/tools/robots-txt/) . 

[ Schema Markup  ](//ahrefs.com/seo/glossary/schema-markup)

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

[ Rich Snippet  ](//ahrefs.com/seo/glossary/rich-snippet)

[ Schema Markup  ](//ahrefs.com/seo/glossary/schema-markup)

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

[ Contact us  ](/cdn-cgi/l/email-protection#e0939590908f9294a0818892858693ce838f8d)

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
