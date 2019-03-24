import scrapy
import json
import sys


class NordVPNSpider(scrapy.Spider):
    name = "nordvpn_spider"
    url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&filters={%22country_id%22:228,%22servers_groups%22:[11]}"
    server_recommendations = None
    optimal_server = None

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        try:
            self.server_recommendations = json.loads(response.text)
            self.optimal_server = self.server_recommendations[0]['hostname']
        except:
            print("Unexpected Error: ", sys.exc_info()[0])
        else:
            print(self.optimal_server)