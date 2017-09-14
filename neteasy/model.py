class MusicFile:
    def __init__(self, mid, path, md5, file_format, creation_time):
        self.mid = mid
        self.path = path
        self.md5 = md5
        self.file_format = file_format
        self.creation_time = creation_time

    def to_obj(self):
        return dict(self.__dict__)

    @staticmethod
    def from_obj(obj):
        return MusicFile(**obj)

    def __repr__(self):
        return "<MusicFile mid=%s format=%s md5=%s>" % (self.mid, self.file_format, self.md5)

    def __str__(self):
        return "ID: %s\nPath: %s\nMD5: %s\nFile Format: %s\nCreation Time: %s" % (
            self.mid,
            self.path,
            self.md5,
            self.file_format,
            self.creation_time
        )


class Album:
    def __init__(self, aid, title):
        self.aid = aid
        self.title = title

    def to_obj(self):
        return dict(self.__dict__)

    @staticmethod
    def from_obj(obj):
        return Album(**obj)

    def __repr__(self):
        return "<Album aid=%s title=%s>" % (self.aid, self.title)


class Singer:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name

    def to_obj(self):
        return dict(self.__dict__)

    @staticmethod
    def from_obj(obj):
        return Singer(**obj)

    def __repr__(self):
        return "<Singer sid=%s name=%s>" % (self.sid, self.name)


class MusicMetaInfo:
    def __init__(self, mid, title, singers, album, cover_img, cover_img_alt=None):
        self.mid = mid
        self.title = title
        self.singers = singers
        self.album = album
        self.cover_img = cover_img
        self.cover_img_alt = cover_img_alt

    def to_obj(self):
        d = dict(self.__dict__)
        d['singers'] = [s.to_obj() for s in self.singers]
        d['album'] = self.album.to_obj()
        return d

    @staticmethod
    def from_obj(obj):
        obj['singers'] = [Singer.from_obj(s) for s in obj['singers']]
        obj['album'] = Album.from_obj(obj['album'])
        return MusicMetaInfo(**obj)

    def __str__(self):
        return "ID: %s\nTitle: %s\nSingers: %s\nAlbum: %s\nCover Image: %s\nCover Image Alt: %s" % (
            self.mid,
            self.title,
            ', '.join([str(s) for s in self.singers]),
            self.album,
            self.cover_img,
            self.cover_img_alt
        )


class Music:
    def __init__(self, mid, meta: MusicMetaInfo, file: MusicFile):
        self.mid = mid
        self.meta = meta
        self.file = file

    def to_obj(self):
        d = dict(self.__dict__)
        d['meta'] = self.meta.to_obj()
        d['file'] = self.file.to_obj()
        return d

    @staticmethod
    def from_obj(obj):
        obj['meta'] = MusicMetaInfo.from_obj(obj['meta'])
        obj['file'] = MusicFile.from_obj(obj['file'])
        return Music(**obj)

    def __str__(self):
        return "-------\n%s\n%s\n-------\n" % (
            self.meta.__str__(),
            self.file.__str__()
        )
