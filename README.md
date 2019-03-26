*******************************************************************

* Title:  nordvpn-spider
* Author: [Matthew Boyette](mailto:Dyndrilliac@gmail.com)
* Date:   3/17/2019

*******************************************************************

A simple single-purpose spider written in Python to crawl [NordVPN's website](https://nordvpn.com/servers/tools/) and extract the optimal VPN server. Created using [Scrapy](https://scrapy.org/).

This project is intended for use with [NordVPN's CLI Linux client](https://support.nordvpn.com/Connectivity/Linux/1182453582/Installing-and-using-NordVPN-on-Linux.htm), although it could also be used in conjunction with [OpenVPN](https://nordvpn.com/tutorials/linux/openvpn/) as well.

# CLI Usage

When executed from a command-line interface, the spider will provide the optimal server's hostname to the user via standard output.

* From repository root directory:
    * ``scrapy crawl --nolog nordvpn_spider``
* From arbitrary directory outside repository:
    * ``scrapy runspider --nolog $GITHUB/nordvpn-spider/nordvpn_spider/spiders/nordvpn_spider.py``

On my machine, I have the ``$GITHUB`` environment variable defined as:
```shell
export GITHUB="$HOME/Documents/Git/GitHub"
```

For maximum effect, I recommend the following additions to `~/.bashrc` or `~/.bash_profile` as appropriate:
```shell
# Define the $GITHUB environment variable.
export GITHUB="$HOME/Documents/Git/GitHub"

# Create a shortcut called 'nordvpn_scraper' for running the spider's python script using scrapy.
alias nordvpn_scraper="scrapy runspider --nolog $GITHUB/nordvpn-spider/nordvpn_spider/spiders/nordvpn_spider.py"

# Define a function to automatically connect to the optimal NordVPN server.
nordvpn_optimize () {
	# This script will print intermediate output by default for debugging purposes.
	# To make it quiet, pass the -silent (or -s) argument.
	isSilent=0
	# Handle function arguments appropriately.
	if [[ $# -gt 0 ]] ; then
		for arg in $@
		do
			case "$arg" in
				-silent|-s)
					isSilent=1
					;;
				*)
					echo "Unknown Argument: $arg"
			esac
		done
	fi
	# Get the server hostname using nordvpn_scraper.
	result=$(eval "nordvpn_scraper")
	if [[ $isSilent != 1 ]] ; then
		# Print the server to standard output.
		# The spider would ordinarily do this by default, but we are capturing the spider's natural output for use in this script.
		echo $result
	fi
	# Note that the syntax for connecting via NordVPN's CLI Linux client is:
	# 	nordvpn c <country_code server_number>
	# Example:
	# 	nordvpn c us2227
	# This means that we have to split off the information we need from the hostname provided by the spider.
	server=$(echo "$result" | cut -d "." -f 1)
	if [[ $isSilent != 1 ]] ; then
		# Print the piece of the hostname we want to standard output.
		echo "$server"
	fi
	# Finally, we can now connect to the desired NordVPN server.
	nordvpn c $server
}
```

With this function, you can automatically connect to the optimal NordVPN server using the simple ``nordvpn_optimize -s`` command. This process can also be automated to occur at login. While the NordVPN Linux client does have an autoconnect feature, it does not appear to choose the optimal server. It seems to choose one at random, which I personally found to be unacceptable - and is ultimately what prompted the creation of this project.

# Python Usage



# Design & Implementation Considerations

