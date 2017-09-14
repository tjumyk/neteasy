import requests
from bs4 import BeautifulSoup

from neteasy.model import Singer, Album, MusicMetaInfo

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
session = requests.session()
session.headers['user-agent'] = USER_AGENT
session.headers['referer'] = 'http://music.163.com/'


class WebInfoExtractor:
    @staticmethod
    def get_music_meta(mid):
        r = session.get("http://music.163.com/song?id=%s" % mid)
        doc = BeautifulSoup(r.content, "html.parser")
        e_info = doc.select('.m-lycifo')[0]

        cover_img = e_info.select('.u-cover img')[0]['data-src']
        e_content = e_info.select('.cnt')[0]
        title = e_content.select('.hd .tit em')[0].get_text()

        singers = {}
        album = None
        e_desc_links = e_content.select('.des a')
        for a in e_desc_links:
            href = a['href']
            if href.startswith('/artist?'):
                singer_id = href.split('=')[-1]
                singer_name = a.get_text()
                singers[singer_id] = Singer(singer_id, singer_name)
            elif href.startswith('/album?'):
                album_id = href.split('=')[-1]
                album_title = a.get_text()
                album = Album(album_id, album_title)
        assert title and singers and album and cover_img
        return MusicMetaInfo(mid, title, list(singers.values()), album, cover_img)

    @staticmethod
    def get_from_url(url):
        return session.get(url).content
