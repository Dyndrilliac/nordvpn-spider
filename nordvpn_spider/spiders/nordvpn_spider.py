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
        self.isSilent = isSilent
        self.obfuscated = obfuscated
        self.udp = udp
        super(NordVPNSpider, self).__init__()

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.url == self.urls[0]:
            try:
                # Construct get_user_info_data JSON object.
                self.get_user_info_data = json.loads(response.text)
            except:
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            finally:
                return
        elif response.url == self.urls[1]:
            try:
                # Construct servers_countries JSON object.
                self.servers_countries = json.loads(response.text)
            except:
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            finally:
                yield scrapy.Request(url=self.construct_data_url(), callback=self.parse)
                return
        else:
            try:
                # Construct servers_recommendations JSON object.
                self.servers_recommendations = json.loads(response.text)
                self.optimal_server = self.servers_recommendations[0]["hostname"]
            except:
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            else:
                if self.isSilent == False:
                    print(self.optimal_server)
            finally:
                return

    def construct_data_url(self):
        # This function supports the following NordVPN server options:
        #   Standard VPN: OpenVPN UDP and OpenVPN TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[3]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[5]}"
        #   Obfuscated VPN: Obfuscated UDP and Obfuscated TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[15]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[17]}"
        # Initialize variables.
        url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations"
        country_id_arg = self.get_country_id()
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
        # Generate the arg_string.
        arg_string = "&filters={%22country_id%22:" + str(country_id_arg) + ",%22servers_groups%22:[" + str(servers_groups_arg) + "],%22servers_technologies%22:[" + str(servers_techs_arg) + "]}"
        # Modify the url.
        new_url = url + arg_string
        # Return the modified url.
        return new_url

    def get_country_id(self):
        try:
            country = self.get_user_info_data["location"].split(",")[0].strip()
            for servers_country in self.servers_countries:
                if country == servers_country["name"]:
                    # Select the desired country id.
                    country_id = servers_country["id"]
        except:
            if self.isSilent == False:
                print("Unexpected Error: ", sys.exc_info()[0])
            # Set a default value as a fall back option.
            country_id = self.special_country_ids["USA"]
        finally:
            # Pick the country id.
            return country_id
