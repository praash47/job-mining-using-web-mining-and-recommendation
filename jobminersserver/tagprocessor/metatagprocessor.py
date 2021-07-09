from tagprocessor import TagProcessor

class MetaTagProcessor(TagProcessor):
    def __init__(self, html):
        TagProcessor.__init__(self, html, tag='meta')

    def get_keywords(self):
        keywords = self.get_property('keywords', name=True)
    
    def get_description(self):
        return self.get_property('description', name=True)

    def get_og_title(self):
        return self.get_property('title', og=True)

    def get_og_description(self):
        return self.get_property('description', og=True)

    def get_property(self, property_name, name=False, og=False):
        property_content = str()
        if name: property_content = self.get_content_from_name(property_name)
        else: 
            if og: property_content = self.get_content_from_property(property_name, og) 
            else: property_content = self.get_content_from_property(property_name)
        # turn into a list
        property_content = property_content.split(" ")
        # strip . and ' ', turn into lowercase
        property_content = [content.strip().strip('.').strip('/').strip('|').strip('-')\
            .strip(',').lower() for content in property_content]

        return property_content

if __name__ == "__main__":
    html = \
    """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title> Search Jobs in Nepal - Job Vacancies in Nepal | merojob </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <meta name="description" content="Find most recent jobs in Nepal at merojob. We offer career opportunities &amp; advice for job seekers and hiring &amp; recruitment services for organization. " />
    <meta name="keywords" content="merojob.com, jobs in Nepal, jobsite in Nepal, job vacancies in Nepal, job vacancy in Nepal, job site in Nepal recent job vacancies in Nepal, job opportunities in Nepal, job sites in Nepal, find jobs in Nepal, find jobs in Nepal, job search in Nepal, job search. " />
    <meta name="author" content="  merojob.com  " />
    <link rel="canonical" href="https://merojob.com" />
    <meta property='og:title' content='Search Jobs in Nepal - Job Vacancies in Nepal | merojob' />
    <meta property='og:image' content="https://static.merojob.com/images/logo/logo-og-image.jpg" />
    <meta property='og:description' content='Find most recent jobs in Nepal at merojob. We offer career opportunities &amp; advice for job seekers and hiring &amp; recruitment services for organization.' />
    <meta property='og:url' content='https://merojob.com/'>
    <meta property="og:type" content="website" />
    <meta property="fb:app_id" content="230516776988241" />
    <meta name="theme-color" content="#002A5B">
    <meta name="google-site-verification" content="KVzb1w4KL9v9xYDmCb-NYo9d0jRnm4e4cirTwVM9lfY" />
    <link rel="shortcut icon" type="image/png" href="https://static.merojob.com/images/mj-logo.png" />
    <link type="text/css" href="https://static.merojob.com/dist/main.be44ee1b062e98fd9f2e.bundle.css" rel="stylesheet" />
    <link rel="manifest" href="https://static.merojob.com/manifest.json">
    </head>
    <body>Test HTML</body></html>
    """
    meta_tag = MetaTagProcessor(html)
    title = TagProcessor(html, tag='title')
    print(set(
        meta_tag.get_keywords() + meta_tag.get_description() + meta_tag.get_og_title() + meta_tag.get_og_description()
        + title.get_content()
    ))