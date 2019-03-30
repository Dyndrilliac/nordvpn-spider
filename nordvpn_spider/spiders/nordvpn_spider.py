import scrapy
import json
import sys

class NordVPNSpider(scrapy.Spider):
    name = "nordvpn_spider"
    urls = [
            "https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data",
            "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_countries",
            "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations",
        ]
    objects = [
            None,
            None,
            None,
        ]

    def __init__(self, isSilent = False, obfuscated = True, udp = True):
        self.isSilent = isSilent
        self.obfuscated = obfuscated
        self.udp = udp
        super(NordVPNSpider, self).__init__()

    def start_requests(self):
        for url in self.urls:
            if url == "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations":
                new_url = self.construct_data_url(url)
                yield scrapy.Request(url=new_url, callback=self.parse)
            else:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, retry = True):
        if response.url == self.urls[0]:
            try:
                # Construct get_user_info_data JSON object.
                self.objects[0] = json.loads(response.text)
                self.get_user_info_data = self.objects[0]
            except:
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
        elif response.url == self.urls[1]:
            try:
                # Construct servers_countries JSON object.
                self.objects[1] = json.loads(response.text)
                self.servers_countries = self.objects[1]
            except:
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
        else:
            try:
                # Construct servers_recommendations JSON object.
                self.objects[2] = json.loads(response.text)
                self.servers_recommendations = self.objects[2]
                self.optimal_server = self.servers_recommendations[0]["hostname"]
            except:
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            else:
                if self.isSilent == False:
                    print(self.optimal_server)

    def construct_data_url(self, url):
        # This function supports the following NordVPN server options:
        #   Standard VPN: OpenVPN UDP and OpenVPN TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[3]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[5]}"
        #   Obfuscated VPN: Obfuscated UDP and Obfuscated TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[15]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[17]}"
        # Initialize variables.
        arg_string = "&filters={%22country_id%22:"
        country_id_arg = self.get_country_id()
        servers_groups_arg = None
        servers_techs_arg = None
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
        arg_string = arg_string + str(country_id_arg) + ",%22servers_groups%22:[" + str(servers_groups_arg) + "],%22servers_technologies%22:[" + str(servers_techs_arg) + "]}"
        # Modify the url.
        new_url = url + arg_string
        # Return the modified url.
        return new_url
    
    def get_country_id(self):
        # Note some useful constants.
        new_country_id = 227 # 227 = United Kingdom
        new_country_id = 228 # 228 = United States
        # Main algorithm
        #
        
        #
        # Pick country id.
        country_id = new_country_id
        # Print the country id.
        print(country_id)
        return country_id
