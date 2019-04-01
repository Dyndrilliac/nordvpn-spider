*******************************************************************

* Title:  nordvpn-spider
* Author: [Matthew Boyette](mailto:Dyndrilliac@gmail.com)
* Date:   3/17/2019

*******************************************************************

A simple single-purpose spider written in Python to crawl [NordVPN's website](https://nordvpn.com/servers/tools/) and extract the optimal VPN server. Created using [Scrapy](https://scrapy.org/).

This project is intended for use with [NordVPN's CLI Linux client](https://support.nordvpn.com/Connectivity/Linux/1182453582/Installing-and-using-NordVPN-on-Linux.htm), although it could also be used in conjunction with [OpenVPN](https://nordvpn.com/tutorials/linux/openvpn/) as well. Currently the spider supports the following four configuration options:
* Standard VPN: OpenVPN UDP.
* Standard VPN: OpenVPN TCP.
* Obfuscated VPN: Obfuscated UDP.
    * **NOTE**: Obfuscated UDP is the default option!
* Obfuscated VPN: Obfuscated TCP.

Currently you must hardcode your configuration choices into the spider. To choose between them, you should modify [line 71](https://github.com/Dyndrilliac/nordvpn-spider/blob/master/nordvpn_spider/spiders/nordvpn_spider.py#L71) of ``nordvpn_spider.py``:
```python
    def __init__(self, isSilent = False, obfuscated = True, udp = True):
```

# CLI Usage

When executed from a command-line interface, the spider will provide the optimal server's hostname to the user via standard output.

* From the repository's root directory:
    * ``scrapy crawl --nolog nordvpn_spider``
* From an arbitrary directory outside the repository:
    * ``scrapy runspider --nolog $GITHUB/nordvpn-spider/nordvpn_spider/spiders/nordvpn_spider.py``

On my machine, I have the ``$GITHUB`` environment variable defined as:
```shell
export GITHUB="$HOME/Documents/Git/GitHub"
```

For maximum effect, I have also included in this repository a [simple shell script](https://github.com/Dyndrilliac/nordvpn-spider/blob/master/nordvpn_optimizer.sh) called ``nordvpn_optimizer.sh`` to invoke [NordVPN's CLI Linux client](https://support.nordvpn.com/Connectivity/Linux/1182453582/Installing-and-using-NordVPN-on-Linux.htm) and pass along the optimal server.

I recommend making the following additions to ``~/.bash_aliases`` or ``~/.bashrc`` as appropriate:
```shell
# Enable quick access to my custom python script for grabbing the optimal NordVPN server.
alias nordvpn_spider="scrapy runspider --nolog $GITHUB/nordvpn-spider/nordvpn_spider/spiders/nordvpn_spider.py"
# Enable quick access to my custom shell script for invoking the NordVPN CLI Linux client.
alias nordvpn_optimizer="$GITHUB/nordvpn-spider/nordvpn_optimizer.sh"
```

With these modifications, you can automatically connect to the optimal NordVPN server within a terminal window using the simple ``nordvpn_optimizer -s`` command. This process can also be automated to occur at login. While the NordVPN Linux client does have an autoconnect feature, it does not appear to choose the optimal server. Instead, it seems to choose one at random. I personally found this behavior to be unacceptable, and it is ultimately what prompted the creation of this project. To automatically connect to the optimal NordVPN server during login, simply add the following to the bottom of your ``~/.profile`` or ``~/.bash_profile`` as appropriate:
```shell
# Automatically connect to the optimal NordVPN server during login.
if [ -f "$GITHUB/nordvpn-spider/nordvpn_optimizer.sh" ] ; then
	$GITHUB/nordvpn-spider/nordvpn_optimizer.sh -s
fi
```

# Python Usage



# Design & Implementation Considerations

This section details the various decisions that were made while developing this project. It's part tutorial, part changelog, and part documentation.

**Note**: I'm using Google Chrome, but virtually every modern browser has web debugging tools. Refer to the documentation for your browser's developer tools as you follow along!

If you examine [the page on NordVPN's website](https://nordvpn.com/servers/tools/) which executes the script that will show the optimal VPN server for you, you will find that the server's hostname gets printed inside an ``h5`` element on the page. You can see this most easily by right-clicking on the server's hostname and clicking the ``Inspect`` option. On the right-hand side of the screen, you should see the page's HTML code focused on the line:
```html
<h5 class="Title mb-3">us2826.nordvpn.com</h5>
```

Note that your optimal server hostname may not be the same as mine. Anyway, before we do anything we want to see if we can simply pull the information we want (the server's hostname) out of the page's HTML output. So right-click on the element's HTML code and copy the CSS selector and the XPath.

* Selector: ``#recommended > div > div > div:nth-child(2) > div.col-xs-12.col-sm-8.col-sm-offset-2.col-md-offset-0.col-md-6.mt-sm-7 > div > div > div.Card__body > div.py-10.px-6.text-center > div.js-RecommendedServerSection__card > h5``
* XPath: ``//*[@id="recommended"]/div/div/div[2]/div[1]/div/div/div[2]/div[1]/div[2]/h5``

In a terminal window, run Scrapy's shell interpreter on the URL where the [the page on NordVPN's website](https://nordvpn.com/servers/tools/) is located:
```shell
scrapy shell https://nordvpn.com/servers/tools/
```

Now, if you try to grab the content we want from the page you will find that it doesn't exist (yet):
```
>>> response.css('#recommended > div > div > div:nth-child(2) > div.col-xs-12.col-sm-8.col-sm-offset-2.col-md-offset-0.col-md-6.mt-sm-7 > div > div > div.Card__body > div.py-10.px-6.text-center > div.js-RecommendedServerSection__card > h5').getall()
[]
>>> response.xpath('//*[@id="recommended"]/div/div/div[2]/div[1]/div/div/div[2]/div[1]/div[2]/h5').getall()
[]
```

What gives? The elements we want are created and populated dynamically by AJAX scripts running on the page behind the scenes. If you switch your browser's development tools to the ``Network`` tab and reload the page, you will see that the page relies on a pretty ridiculously long list of remote resources that need to be loaded at runtime. According to my browser, the page we're interested in makes a total of 108 requests which take a total of 12.25 seconds to finish loading and rendering! Fortunately, we only need to crawl a small subset of these resources. Since we know the data is populated using AJAX, we can eliminate a lot of items from consideration. While still in the ``Network`` tab of your browser's development tools, click on the filter labelled ``XHR``. XHR stands for ``XMLHttpRequest`` and is the core API behind AJAX. If you filter out all but the XHR requests, then that should cut our list down to ten different items. Better still, later on we will find that we really only need three of them. Here is the list of resources we will actually crawl and use:
```
https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data
https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_countries
https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&filters={%22country_id%22:228,%22servers_groups%22:[11]}
```

We can further reduce this list by replacing the second resource (the ``servers_countries`` JSON response) with a local data store, as seen below (and on [line 8 of nordvpn_spider.py](https://github.com/Dyndrilliac/nordvpn-spider/blob/master/nordvpn_spider/spiders/nordvpn_spider.py#L8)):
```python
    country_ids = {
            "Albania":2,
            "Argentina":10,
            "Australia":13,
            "Austria":14,
            "Belgium":21,
            "Bosnia and Herzegovina":27,
            "Brazil":30,
            "Bulgaria":33,
            "Canada":38,
            "Chile":43,
            "Costa Rica":52,
            "Croatia":54,
            "Cyprus":56,
            "Czech Republic":57,
            "Denmark":58,
            "Egypt":64,
            "Estonia":68,
            "Finland":73,
            "France":74,
            "Georgia":80,
            "Germany":81,
            "Greece":84,
            "Hong Kong":97,
            "Hungary":98,
            "Iceland":99,
            "India":100,
            "Indonesia":101,
            "Ireland":104,
            "Israel":105,
            "Italy":106,
            "Japan":108,
            "Latvia":119,
            "Luxembourg":126,
            "Malaysia":131,
            "Mexico":140,
            "Moldova":142,
            "Netherlands":153,
            "New Zealand":156,
            "North Macedonia":128,
            "Norway":163,
            "Poland":174,
            "Portugal":175,
            "Romania":179,
            "Serbia":192,
            "Singapore":195,
            "Slovakia":196,
            "Slovenia":197,
            "South Africa":200,
            "South Korea":114,
            "Spain":202,
            "Sweden":208,
            "Switzerland":209,
            "Taiwan":211,
            "Thailand":214,
            "Turkey":220,
            "Ukraine":225,
            "United Arab Emirates":226,
            "United Kingdom":227,
            "United States":228,
            "Vietnam":234,
        }
```

This client-side dictionary will take a ``country`` and resolve a ``country_id`` much faster than querying the server script, downloading the result, parsing it with JSON, and searching it for a match to a given country string. Since we intend to undergo this process every time we log into our machine, we need to shave as much time off our clock as possible. I literally copy and pasted from the server's ``servers_countries`` response to construct this dictionary. All the data came from the server originally, we're just caching it for faster lookup times.