import scrapy
import json
import sys

class NordVPNSpider(scrapy.Spider):
    name = "nordvpn_spider"
    url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&filters={%22country_id%22:228,%22servers_groups%22:[17],%22servers_technologies%22:[15]}"

    def __init__(self, isSilent = False):
        self.isSilent = isSilent
        super(NordVPNSpider, self).__init__()

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        try:
            self.server_recommendations = json.loads(response.text)
            self.optimal_server = self.server_recommendations[0]['hostname']
        except:
            if self.isSilent == False:
                print("Unexpected Error: ", sys.exc_info()[0])
        else:
            if self.isSilent == False:
                print(self.optimal_server)