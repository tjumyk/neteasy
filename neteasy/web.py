import requests
from bs4 import BeautifulSoup

from neteasy.model import Singer, Album, MusicMetaInfo

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'


class WebInfoExtractor:
    @staticmethod
    def get_music_meta(mid):
        r = requests.get("http://music.163.com/song?id=%s" % mid, headers={'user-agent': USER_AGENT})
        doc = BeautifulSoup(r.content, "html.parser")
        e_info = doc.select('.m-lycifo')[0]

        cover_img = e_info.select('.u-cover img')[0]['data-src']
        e_content = e_info.select('.cnt')[0]
        title = e_content.select('.hd .tit em')[0].get_text()

        singers = []
        album = None
        e_descriptions = e_content.select('.des')
        for e_desc in e_descriptions:
            text = e_desc.get_text()
            if '歌手' in text:
                for a in e_desc.select('a'):
                    href = a['href']
                    if href.startswith('/artist?'):
                        singer_id = href.split('=')[-1]
                        singer_name = a.get_text()
                        singers.append(Singer(singer_id, singer_name))
            elif '专辑' in text:
                for a in e_desc.select('a'):
                    href = a['href']
                    if href.startswith('/album?'):
                        album_id = href.split('=')[-1]
                        album_title = a.get_text()
                        album = Album(album_id, album_title)
                        break
        return MusicMetaInfo(mid, title, singers, album, cover_img)


if __name__ == '__main__':
    print(WebInfoExtractor.get_music_meta('108468'))
