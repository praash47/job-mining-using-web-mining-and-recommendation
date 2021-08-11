"""
Consumers handles all the websocket connections in the server. It does so Django channel's
generic websocket function. Consumer consumes websocket connections from frontend and scrapy.
"""
import os
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from checkers.checkjobwebsite import CheckJobWebsite
from interactor.searcher import Search


class JobMinersConsumer(WebsocketConsumer):
    """
    This class handles websocket connections between our vuejs client and scrapy
    process.
    """
    def connect(self):
        """
        Executes when the first connection is received by the websocket. It used redis's
        channels and groups for multiprocess communication in server (in our case django's
        process and scrapy's process)

        It assigns channel and group to websocket connections so that communication is established
        between processes in the server. 
        """
        # A random group name, dyoyagupucha means in newari
        # Dyo yagu - God 's
        # Pucha - Group
        self.room_group_name = 'dyoyagupucha'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        """
        On disconnect discard the group and channel.
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        """
        Receives the websocket connection after the connection is upgraded from
        HTTP (first of all connection is established with HTTP, then upgraded to
        websocket).

        It either receives a scrape command from frontend or one website's job URL
        scraping from the scrapy.

        Parameters:
        -----------
        text_data: json or str
            text data that is received from external environments (frontend or scrapy)
        """
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

            for url in job_website_urls:
                search = Search(url)
                search_url = search.get_search_url()
                # Placement of spider on website whose search URL is passed.
                os.system(f'curl http://localhost:6800/schedule.json \
                    -d project=scraper -d spider=CrawlSite -d \
                    search_page_url="{search_url}')

        elif data['action'] == 'one_website_scrape_completed':
            title = "Completed Crawling from one site! Here are the jobs:"
            
            # Frontend's data container accepts the dictionary 
            # message data in the following format:
            # content = [
            # {
            #   dict: {
            #       key: job
            #       value: url
            #   } 
            # },
            # ]
            content = []
            for job, url in data['jobs'].items():
                content.append({
                    'dict': {
                        'key': job,
                        'value': url
                    }
                }) 
            
            # Send to the whole group so that message from scrapy is 
            # forwarded to the frontend.
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
        """
        Redis handler for the title_content to send the title_content type
        container to the frontend.
        """
        message = event['message']

        self.send(text_data=message)