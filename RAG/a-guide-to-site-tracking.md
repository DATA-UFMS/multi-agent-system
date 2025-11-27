##  Introduction 

In our [ migration guide ](https://www.activecampaign.com/learn/guides/migration-guide-from-importing-contacts-to-transferring-workflows/) , we say that using our site tracking is imperative for success. If you don’t believe that now, we hope the following guide convinces you. 

##  What It Is 

[ Site tracking ](https://www.activecampaign.com/learn/video/site-tracking-intro/) records all essential actions that contacts take on **any** of your web assets and third-party tools. When we say “all essential actions,” we mean it. 

ActiveCampaign users can segment contacts according to 6 essential site actions: 

  * **Has visited:** targets contacts that have visited a certain URL or domain 
  * **Has not visited:** targets contacts that have not visited a certain URL or domain 
  * **Was referred from:** targets contacts who were referred from a certain URL 
  * **Visiting Device:** targets contacts based on whether they did or didn’t visit via desktop, laptop, or tablet 
  * **Total page visits:** targets contacts who have or don’t have a certain number of total page visits 
  * **Total site visits:** targets contacts who have or don’t have a certain number of total site visits 



The [ segment builder ](https://www.activecampaign.com/learn/guides/using-the-segment-builder-in-activecampaign) , which can be found throughout the platform and is shown here in an [ automation ](http://www.activecampaign.com/learn/guides/what-are-automations/) , allows you to further define the actions you wish to isolate. 

If you add the “Has visited” an exact URL condition to our automation, you will target contacts who have visited the URL “mydomain.com/aboutme” one time. 

You start with the action “Has visited” and can choose if you want to focus on visits to a certain URL or domain. You can specify if you want exact matches of the URL/domain or if URLs/domains that merely contain whatever you type in the empty field will suffice. 

In the empty field, you type in the URL or domain you wish to track visits to. Lastly, for the “Has visited” action, our segment builder empowers you to target contacts based on the **number** of visits they make to the URL or domain you choose to isolate. 

You can apply similar flexibility to each of the 6 site tracking actions, and we encourage you to do so. The ability to perform site tracking at such a granular level is unique to ActiveCampaign. For the remaining 5 actions, the segment builder has only 3 pieces of data to configure (it removes the frequency field). 

**Note:** If you set up site tracking, you do not have to create [ tags ](http://www.activecampaign.com/learn/guides/what-are-tags/) or use [ custom fields ](http://www.activecampaign.com/learn/guides/what-are-custom-fields/) to store data such as site visits. The platform automatically stores that activity for you, and you can easily use the segment builder to target contacts accordingly. 

You can also filter contacts according to site tracking data on the main “Contacts” page. Simply access the segment builder and select the relevant condition. 

Also, you can monitor individual contact activity in the “Recent Activities” stream on each contact record. 

![](https://active-campaign.transforms.svdcdn.com/production/general/Screenshot-2024-01-16-at-08.36.41-1024x544.png?w=1600&q=80&auto=format&fit=clip&dm=1747262553&s=286a9dfded6533e84f9e5a4ccc59bd32) ![](https://active-campaign.transforms.svdcdn.com/production/general/Screenshot-2024-01-16-at-08.36.41-1024x544.png?w=1600&q=80&auto=format&fit=clip&dm=1747262553&s=286a9dfded6533e84f9e5a4ccc59bd32)

##  Why It Matters 

Above all else, site tracking allows for advanced [ segmentation ](http://www.activecampaign.com/learn/guides/lets-get-personal-a-guide-to-automatic-contact-segmentation/) . By using the segment builder in automations, you can automate the grouping of contacts who perform actions on the sites or pages that you wish to isolate. As is the case with automations, you can also automate any messaging these contacts receive. 

So, at the end of the day, site tracking empowers you to practice **behavioral-based marketing** . It allows you to personalize at scale and engage with contacts based on the actions they’ve taken on your web assets and third-party tools. The more targeted your marketing is, the more likely you are to achieve your ultimate business goals. 

The potential worth of site tracking is immeasurable. Here are just five scenarios where site tracking data could prove valuable: 

  * **Helps support team diagnose issues:** When dealing with frustrated customers, support reps could view contacts’ site activities. Perhaps the data shows that a contact repeatedly visited the “forgot password” page. That could be the reason why the contact is upset–they couldn’t log in. 
  * **Measures the effectiveness of your websites:** Site tracking allows you to assess how your web assets and third-party tools perform. Are they generating traffic? What sites is traffic coming from? What pages lead to conversions? 
  * **Mobile, Tablet, or Desktop:** Site tracking monitors the devices contacts use to browse your web assets and third-party tools. Rather than simply following industry trends, you can use site tracking data to determine what devices _your_ hottest leads are using and adjust your strategy appropriately. 
  * **Helps sales team convert contacts:** Your sales team can identify contacts who repeatedly visit your product page(s) and can engage them accordingly. 
  * **Works to tell contacts’ stories:** Together with tags and custom fields, site tracking helps tell contacts’ stories. The data provides a detailed history of a contact’s unique journey with your company. 



##  How To Set It Up 

You’ve discovered what site tracking is. You’ve explored why it matters. Now, find out how to set it up. 

The good news is that setting up site tracking is easy. However, you need to understand what’s required for site tracking to work properly. If you don’t, you might think your site tracking is broken, when in reality it wasn’t configured correctly. 

In our [ migration guide ](http://www.activecampaign.com/learn/guides/migration-guide-from-importing-contacts-to-transferring-workflows/) , we suggest that site tracking setup should be one of the first tasks you complete. To do so, you need to carry out 3 steps. All of them take place under the “Tracking” section of your settings page. 

  1. Activate Site Tracking by clicking the “Enable” option and setting it to “ON” 
  2. In the “Add Website URL” field, type your website URL (excluding the “http://”) and click “Add” 
  3. Copy the Tracking Code and paste it into the footer of your website and third-party tools. 



Once you do that, ActiveCampaign tracks the contacts that visit your sites and their pages for as long as they exist in your database. 

**Note:** Site tracking works through cookies. In order to add a site tracking cookie to a browser, contacts must either submit information via an ActiveCampaign form (third-party forms not included), or click on a link in a campaign email sent through ActiveCampaign. For more information, please read this [ article ](https://help.activecampaign.com/hc/en-us/articles/221542267-An-overview-of-Site-Tracking#an-overview-of-site-tracking-0-0) . 

##  Using Site Tracking Data in an Automation 

It’s important to clarify the difference between the “Actions” category and the “Site & Event Data” category that appears in the segment builder. 

The “Actions” condition refers to actions contacts take on messages sent via ActiveCampaign, form submissions, list actions, and more. The “Site & Event Data” condition relates to site tracking and site visits. Use it to leverage actions that contacts take on your external web assets and third-party tools. 


© 2025 ActiveCampaign 
