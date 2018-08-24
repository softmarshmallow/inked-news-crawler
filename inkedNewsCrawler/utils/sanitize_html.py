from bs4 import BeautifulSoup, Comment


def remove_unused_tags_html(html):
    blacklist = ["script", "style"]

    soup = BeautifulSoup(html, 'lxml')

    for tag in soup.findAll():
        if tag.name.lower() in blacklist:
            # blacklisted tags are removed in their entirety
            tag.extract()


    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    return str(soup)
