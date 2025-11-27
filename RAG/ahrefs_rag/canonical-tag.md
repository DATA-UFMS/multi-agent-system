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

[ Cached Page  ](//ahrefs.com/seo/glossary/cached-page)

#  Canonical Tag 

##  What is a Canonical Tag? 

A canonical tag or rel=“canonical” is a snippet of HTML code that declares the [ canonical URL ](https://ahrefs.com/seo/glossary/canonical-url) of the web page. In other words, it lets you define the main version for your duplicate, near-duplicate, and similar content under different URLs to instruct search engines on which version should be indexed. 

Canonicalization helps you control your duplicate content by explicitly specifying to Google which URL is canonical and should be indexed. 

Here’s what it looks like in the page code: 

` <link rel="canonical" href="https://ahrefs.com/blog/"> `

An alternative to canonical tags is implementing a rel=“canonical” HTTP header. 

##  Why are canonical tags important? 

Using the canonical tag is the primary way to solve duplicate content issues on a website. A canonical tag helps search engines find the most representative “canonical” version among the duplicate pages to indicate what needs to be indexed and re-crawled more frequently. 

The tag also helps consolidate link signals from a set of duplicate pages to the canonical version (or the one you want to be ranked), thereby improving its overall ranking. 

If you don’t use canonical tags on the duplicate pages of your site, Google will still attempt to identify the canonical page. However, there’s no guarantee that it will be the page version you want to be indexed. 

##  Best practices for canonical tags 

Here are a few things to keep in mind when using the canonical tags: 

###  1\. Always use the self-referential canonical tag 

A self-referencing canonical tag references the URL of the given page, even if the page has no alternative versions. In this case, whenever a page is accessed via a URL with URL parameters, it will automatically point to the canonical version. 

Although using self-referential canonical tags is not necessary, it is recommended. 

> “I recommend [using a] self-referential canonical because it really makes it clear to us which page you want to have indexed, or what the URL should be when it is indexed. 
> 
> Even if you have one page, sometimes there are different variations of the URL that can pull that page up. For example, with parameters in the end, perhaps with upper lower case or www and non-www. All of these things can be kind of cleaned up with a rel canonical tag” - [ John Mueller from Google ](https://www.youtube.com/watch?v=XOGOhWyNSf8&t=492s)

###  2\. Use absolute URLs 

Absolute URLs (that contain all the information necessary to locate a resource) in canonical tags can help you avoid unintentional mistakes or misinterpretations of canonical URLs by search engines. 

You can use relative URLs in canonical tags, but it’s recommended best SEO practice to use absolute URLs. 

###  3\. Don’t use the robots.txt file for canonicalization 

The robots.txt file tells search engine crawlers where they can and can’t go on your site. If the URLs are disallowed in robots.txt, Google won’t read their canonical tags. Besides, link signals from these pages will not be consolidated. 

###  4\. Audit your website regularly 

It’s important to monitor duplicate content issues on your website to ensure proper canonicalization of your pages. 

Ahrefs [ Site Audit ](https://ahrefs.com/site-audit) (or the free Ahrefs [ Webmaster Tools ](https://ahrefs.com/webmaster-tools) ) can help you with that. You’ll be able to find the “duplicates” report that will show the duplicate and near-duplicate pages of your website that aren’t properly canonicalized. 

![Duplicate content issues in ahrefs site audit report](https://ahrefs.com/blog/wp-content/uploads/2022/03/Duplicate-contnet-issues-in-ahrefs-site-audit-report.png)

##  FAQs 

###  Is the canonical tag always necessary? 

Although it is not necessary to use the canonical tag, we recommend using it. If there’s duplicate content without the canonical tag, Google may still try to find the canonical version. However, in the presence of a canonical tag, it would become clearer to the search engine. 

###  What is a canonical URL? 

A canonical URL is a URL of the preferred version of a page in a set of duplicate or near-duplicate pages. This URL is used in the canonical tag instructing the search engines about canonicalization. 

[ Canonical URL  ](//ahrefs.com/seo/glossary/canonical-url)

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

[ Cached Page  ](//ahrefs.com/seo/glossary/cached-page)

[ Canonical URL  ](//ahrefs.com/seo/glossary/canonical-url)

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

[ Contact us  ](/cdn-cgi/l/email-protection#671412171708151327060f150201144904080a)

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
