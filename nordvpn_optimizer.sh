#!/bin/bash
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
# Get the server hostname using nordvpn_spider.
result=$(eval "scrapy runspider --nolog $GITHUB/nordvpn-spider/nordvpn_spider/spiders/nordvpn_spider.py")
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
# Initialize NordVPN connectivity status variable for the first execution of the loop.
status=$(eval "nordvpn status")
while [[ $status = *Disconnected* ]]
do
	if [[ $isSilent != 1 ]] ; then
		# Print the status of our connectivity to NordVPN via standard output.
		echo $status
	fi
	# Finally, we can now connect to the desired NordVPN server.
	nordvpn c $server
	# Check for connectivity; if not connected, try again until a connection is established.
	status=$(eval "nordvpn status")
done