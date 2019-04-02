import scrapy
import json
import sys

class NordVPNSpider(scrapy.Spider):
    name = "nordvpn_spider"
    url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data"
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

    def __init__(self, isSilent = False, obfuscated = True, udp = True):
        # Initialize the spider's custom settings.
        self.isSilent = isSilent
        self.obfuscated = obfuscated
        self.udp = udp
        # Call the super-class constructor.
        super(NordVPNSpider, self).__init__()

    def start_requests(self):
        # Crawl the get_user_info_data URL and parse the results.
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        if response.url == self.url:
            try:
                # Construct the get_user_info_data JSON object.
                self.get_user_info_data = json.loads(response.text)
            except:
                # Print error to standard output.
                if self.isSilent == False:
                    print("Unexpected Error: ", sys.exc_info()[0])
            finally:
                # Crawl the generated data URL using the responses to our previous queries and parse the results.
                # Note that if you want to force the spider to return the optimal server in a specified country, this is the best place to do so.
                # Simply provide a country string argument for construct_data_url().
                yield scrapy.Request(url=self.construct_data_url(), callback=self.parse)
                # Example of forcing the spider to return the optimal server in the United Kingdom:
                #   yield scrapy.Request(url=self.construct_data_url("United Kingdom"), callback=self.parse)
                # Example of forcing the spider to return the optimal server in the United States:
                #   yield scrapy.Request(url=self.construct_data_url("United States"), callback=self.parse)
                # Done parsing the first request.
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

    def construct_data_url(self, country=None):
        # This function supports the following NordVPN server options:
        #   Standard VPN: OpenVPN UDP and OpenVPN TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[3]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[11],%22servers_technologies%22:[5]}"
        #   Obfuscated VPN: Obfuscated UDP and Obfuscated TCP.
        #       * Example UDP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[15]}"
        #       * Example TCP arg string in United States: "&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[17]}"
        # Determine country id.
        if country == None:
            country_id_arg = self.get_country_id()
        else:
            country_id_arg = self.get_country_id(country)
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
        return "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations" + "&filters={%22country_id%22:" + str(country_id_arg) + ",%22servers_groups%22:[" + str(servers_groups_arg) + "],%22servers_technologies%22:[" + str(servers_techs_arg) + "]}"

    def get_country_id(self, country=None):
        try:
            if country == None:
                # Get the country in which we are currently located.
                country = self.get_user_info_data["location"].split(",")[0].strip()
                # Select the desired country id.
                country_id = self.country_ids[country]
            else:
                country_id = self.country_ids[country]
        except:
            # Print error to standard output.
            if self.isSilent == False:
                print("Unexpected Error: ", sys.exc_info()[0])
        finally:
            # Pick the appropriate country id.
            return country_id
