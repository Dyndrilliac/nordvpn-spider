import scrapy
import json
import sys

class NordVPNSpider(scrapy.Spider):
    name = "nordvpn_spider"
    urls = [
            "https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data",
            "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_countries",
        ]
    special_country_ids = {
            "UK":227,
            "USA":228,
        }

    def __init__(self, isSilent = False, obfuscated = True, udp = True):
        # Initialize the spider's custom settings.
        self.isSilent = isSilent
        self.obfuscated = obfuscated
        self.udp = udp
        # Call the super-class constructor.
        super(NordVPNSpider, self).__init__()

    def start_requests(self):
        # For each URL in the list of URLs to crawl...
        for url in self.urls:
            # Crawl the URL and parse the results.
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.url == self.urls[0]:
            try:
                # Construct the get_user_info_data JSON object.
                self.get_user_info_data = json.loads(response.text)
            except:
                # Print error to standard output.
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            finally:
                # Done parsing the first request.
                return
        elif response.url == self.urls[1]:
            try:
                # Construct the servers_countries JSON object.
                self.servers_countries = json.loads(response.text)
            except:
                # Print error to standard output.
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            finally:
                # Crawl the generated data URL using the responses to our previous queries and parse the results.
                yield scrapy.Request(url=self.construct_data_url(), callback=self.parse)
                # Done parsing the second request.
                return
        else:
            try:
                # Construct the servers_recommendations JSON object.
                self.servers_recommendations = json.loads(response.text)
                # Obtain the hostname of the optimal NordVPN server.
                self.optimal_server = self.servers_recommendations[0]["hostname"]
            except:
                # Print error to standard output.
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            else:
                # Print the optimal NordVPN server to standard output.
                if self.isSilent == False:
                    print(self.optimal_server)
            finally:
                # Done parsing the final request.
                return

    def construct_data_url(self):
        # This function supports the following NordVPN server options:
        #   Standard VPN: OpenVPN UDP and OpenVPN TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[3]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[5]}"
        #   Obfuscated VPN: Obfuscated UDP and Obfuscated TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[15]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[17]}"
        # Check for obfuscated VPN or standard VPN.
        if self.obfuscated == False:
            servers_groups_arg = 11
            # Check for UDP or TCP.
            if self.udp == True:
                servers_techs_arg = 3
            else:
                servers_techs_arg = 5
        else:
            servers_groups_arg = 17
            # Check for UDP or TCP.
            if self.udp == True:
                servers_techs_arg = 15
            else:
                servers_techs_arg = 17
        # Return the desired AJAX data URL.
        return "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations" + "&filters={%22country_id%22:" + str(self.get_country_id()) + ",%22servers_groups%22:[" + str(servers_groups_arg) + "],%22servers_technologies%22:[" + str(servers_techs_arg) + "]}"

    def get_country_id(self):
        try:
            # Get the country in which we are currently located.
            country = self.get_user_info_data["location"].split(",")[0].strip()
            # For each country in which there are VPN servers...
            for servers_country in self.servers_countries:
                # If our country matches on in the list...
                if country == servers_country["name"]:
                    # Select the desired country id.
                    country_id = servers_country["id"]
        except:
            # Print error to standard output.
            if self.isSilent == False:
                print("Unexpected Error: ", sys.exc_info()[0])
            # Set a default value as a fall back option.
            country_id = self.special_country_ids["USA"]
        finally:
            # Pick the appropriate country id.
            return country_id
