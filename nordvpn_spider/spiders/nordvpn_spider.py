import scrapy

class NordVPNSpider(scrapy.Spider):
    name = "nordvpn"

    def start_requests(self):
        urls = [
            'https://nordvpn.com/servers/tools/',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'server-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)