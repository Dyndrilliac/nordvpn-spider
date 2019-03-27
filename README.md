*******************************************************************

* Title:  nordvpn-spider
* Author: [Matthew Boyette](mailto:Dyndrilliac@gmail.com)
* Date:   3/17/2019

*******************************************************************

A simple single-purpose spider written in Python to crawl [NordVPN's website](https://nordvpn.com/servers/tools/) and extract the optimal VPN server. Created using [Scrapy](https://scrapy.org/).

This project is intended for use with [NordVPN's CLI Linux client](https://support.nordvpn.com/Connectivity/Linux/1182453582/Installing-and-using-NordVPN-on-Linux.htm), although it could also be used in conjunction with [OpenVPN](https://nordvpn.com/tutorials/linux/openvpn/) as well.

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

For maximum effect, I have also included in this repository a simple shell script to invoke [NordVPN's CLI Linux client](https://support.nordvpn.com/Connectivity/Linux/1182453582/Installing-and-using-NordVPN-on-Linux.htm) and pass along the optimal server.

I recommend making the following additions to ``~/.bash_aliases`` or ``~/.bashrc`` as appropriate:
```shell
# Enable quick access to my custom python script for grabbing the optimal NordVPN server.
alias nordvpn_scraper="scrapy runspider --nolog $GITHUB/nordvpn-spider/nordvpn_spider/spiders/nordvpn_spider.py"
# Enable quick access to my custom shell script for invoking the NordVPN CLI Linux client.
alias nordvpn_optimizer="$GITHUB/nordvpn-spider/nordvpn_optimizer.sh"
```

With these modifications, you can automatically connect to the optimal NordVPN server using the simple ``nordvpn_optimizer -s`` command. This process can also be automated to occur at login. While the NordVPN Linux client does have an autoconnect feature, it does not appear to choose the optimal server. Instead, it seems to choose one at random. I personally found this behavior to be unacceptable, and is ultimately what prompted the creation of this project. To automatically connect to the optimal NordVPN server during login, simply add the following to the bottom of your ``~/.profile`` or ``~/.bash_profile`` as appropriate:
```shell
# Automatically connect to the optimal NordVPN server during login.
if [ -f "$GITHUB/nordvpn-spider/nordvpn_optimizer.sh" ] ; then
	$GITHUB/nordvpn-spider/nordvpn_optimizer.sh -s
fi
```

# Python Usage



# Design & Implementation Considerations

