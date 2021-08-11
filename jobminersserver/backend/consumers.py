from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from checkers.checkjobwebsite import CheckJobWebsite
from asgiref.sync import async_to_sync

import json

import os

from channels.generic.websocket import WebsocketConsumer

class JobMinersConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'dyoyagupucha'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        if data['action'] == 'scrape':
            self.send(text_data=json.dumps(
                {
                    'type': 'msg',
                    'message': 'Fetching 100 URLs from Google...'
                }
            ))
            rg = RequestGoogle()
            urls = rg.get_100_urls()
            
            self.send(text_data=json.dumps(
                {
                    'type': 'title_content',
                    'title': 'Fetched 100 URLs from Google',
                    'content': urls
                }
            ))

            checker = CheckJobWebsite(urls=urls)
            self.send(text_data=json.dumps(
                {
                    'type': 'msg',
                    'message': 'Scanning job websites in 100 URLs...'
                }
            ))
            job_website_urls = checker.check_urls()

            self.send(text_data=json.dumps(
                {
                    'type': 'title_content',
                    'title': 'Here are the job website URLs:',
                    'content': job_website_urls
                }
            ))

            os.system(f'curl http://localhost:6800/schedule.json \
                -d project=scraper -d spider=CrawlSite -d \
                search_page_url="https://www.kumarijob.com/search?keywords="')

        elif data['action'] == 'one_website_scrape_completed':
            title = "Completed Crawling from one site! Here are the jobs:"
            
            content = []
            for job, url in data['jobs'].items():
                content.append({
                    'dict': {
                        'key': job,
                        'value': url
                    }
                }) 
            print('sending to frontend')
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'title_content',
                    'message': json.dumps({
                        'type': 'title_content',
                        'title': title,
                        'content': content
                    })
                }
            )
    
    def title_content(self, event):
        message = event['message']

        self.send(text_data=message)