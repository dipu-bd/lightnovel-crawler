# -*- coding: utf-8 -*-

ajax_url = '%s/wp-admin/admin-ajax.php'
search_url = '%s/?s=%s&post_type=wp-manga&author=&artist=&release='


def initialize(self) -> None:
    self.cleaner.bad_tags.update(['h3', 'script'])
    self.cleaner.bad_css.update(['.code-block', '.adsbygoogle'])


def search_novel(self, query):
    query = query.lower().replace(' ', '+')
    soup = self.get_soup(search_url % (self.home_url.rstrip('/'), query))

    results = []
    for tab in soup.select('.c-tabs-item__content'):
        a = tab.select_one('.post-title h3 a')
        latest = tab.select_one('.latest-chap .chapter a').text
        votes = tab.select_one('.rating .total_votes').text
        results.append(
            {
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            }
        )

    return results


def read_novel_info(self):
    soup = self.get_soup(self.novel_url)

    possible_title = soup.select_one('.post-title h1')
    for span in possible_title.select('span'):
        span.extract()

    self.novel_title = possible_title.text.strip()

    img_src = soup.select_one('.summary_image a img')

    if img_src:
        self.novel_cover = self.absolute_url(img_src['src'])

    self.novel_author = ' '.join(
        [
            a.text.strip()
            for a in soup.select('.author-content a[href*="manga-author"]')
        ]
    )

    clean_novel_url = self.novel_url.split('?')[0].strip('/')
    response = self.submit_form(f'{clean_novel_url}/ajax/chapters/')

    soup = self.make_soup(response)
    get_chapters_list(self, soup)
    if len(self.chapters) == 0:
        nl_id = soup.select_one('[id^="manga-chapters-holder"][data-id]')
        if not nl_id:
            return

        self.novel_id = nl_id['data-id']
        response = self.submit_form(ajax_url % self.home_url.rstrip('/'),
                                    data={'action': 'manga_get_chapters',
                                          'manga': self.novel_id, })
        soup = self.make_soup(response)
        get_chapters_list(self, soup)


def get_chapters_list(self, soup):
    for a in reversed(soup.select('.wp-manga-chapter a')):
        chap_id = len(self.chapters) + 1
        vol_id = chap_id // 100 + 1

        if chap_id % 100 == 1:
            self.volumes.append({'id': vol_id})

        self.chapters.append(
            {
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            }
        )


def download_chapter_body(self, chapter):
    soup = self.get_soup(chapter['url'])
    contents = soup.select_one('div.reading-content')

    for img in contents.findAll('img'):
        if img.has_attr('data-src'):
            src_url = img['data-src']
            parent = img.parent
            img.extract()
            new_tag = soup.new_tag('img', src=src_url)
            parent.append(new_tag)

    return self.cleaner.extract_contents(contents)
