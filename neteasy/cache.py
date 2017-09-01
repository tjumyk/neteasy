import getpass
import glob
import hashlib
import os
import platform

from neteasy.model import MusicFile

BLOCK_SIZE = 65536


class CacheScanner:
    @staticmethod
    def get_scanner(cache_folder=None):
        system = platform.system()
        if system == 'Linux':
            return LinuxCacheScanner(cache_folder)
        elif system == 'Windows':
            return WindowsCacheScanner(cache_folder)
        else:
            print('We do not support your system (%s) now' % system)
            raise NotImplementedError()

    def __init__(self, cache_folder):
        self.cache_folder = cache_folder

    def scan(self):
        raise NotImplementedError()

    @staticmethod
    def check_file_md5(file_path, md5):
        with open(file_path, 'rb') as _f:
            hasher = hashlib.md5()
            block = _f.read(BLOCK_SIZE)
            while block:
                hasher.update(block)
                block = _f.read(BLOCK_SIZE)
            return hasher.hexdigest() == md5


class LinuxCacheScanner(CacheScanner):
    def __init__(self, cache_folder):
        if cache_folder is None:
            user = getpass.getuser()
            cache_folder = '/home/%s/.cache/netease-cloud-music/CachedSongs' % user
            print('Using default cache folder path: %s' % cache_folder)
        if not LinuxCacheScanner._check_cache_folder(cache_folder):
            raise RuntimeError('Invalid cache folder path: %s' % cache_folder)
        super(LinuxCacheScanner, self).__init__(cache_folder)

    @staticmethod
    def _check_cache_folder(path):
        if not os.path.isdir(path):
            return False
        if any(glob.iglob(os.path.join(path, '*.mp3'))):
            return True
        if any(glob.iglob(os.path.join(path, '*.flac'))):
            return True
        if not any(os.listdir(path)):  # accept empty folder
            return True

    @staticmethod
    def _scan_format(folder, file_format):
        for f in glob.iglob(os.path.join(folder, '*.%s' % file_format)):
            file_name = os.path.basename(f)
            mid, zone, md5 = file_name[:-len(file_format) - 1].split('-')
            mtime = os.path.getmtime(f)
            yield MusicFile(mid, f, md5, file_format, mtime)

    def scan(self):
        for file_format in ['mp3', 'flac']:
            for f in LinuxCacheScanner._scan_format(self.cache_folder, file_format):
                yield f


class WindowsCacheScanner(CacheScanner):
    def __init__(self, cache_folder):
        if cache_folder is None:
            user = getpass.getuser()
            cache_folder = r'C:\Users\%s\AppData\Local\Netease\CloudMusic\Cache\Cache' % user
            print('Using default cache folder path: %s' % cache_folder)
        if not WindowsCacheScanner._check_cache_folder(cache_folder):
            raise RuntimeError('Invalid cache folder path: %s' % cache_folder)
        super(WindowsCacheScanner, self).__init__(cache_folder)

    @staticmethod
    def _check_cache_folder(path):
        if not os.path.isdir(path):
            return False
        if any(glob.iglob(os.path.join(path, '*.uc'))):
            return True
        if any(glob.iglob(os.path.join(path, '*.idx'))):
            return True
        if not any(os.listdir(path)):  # accept empty folder
            return True

    @staticmethod
    def _scan_format(folder, file_format):
        # Currently, this is identical to the one in LinuxCacheScanner, not sure if it also applies to MacOS version
        for f in glob.iglob(os.path.join(folder, '*.%s' % file_format)):
            file_name = os.path.basename(f)
            file_name_without_extension = file_name[:-len(file_format) - 1]
            mid, zone, md5 = file_name_without_extension.split('-')
            mtime = os.path.getmtime(f)
            yield MusicFile(mid, f, md5, file_format, mtime)

    def scan(self):
        for f in WindowsCacheScanner._scan_format(self.cache_folder, 'uc'):
            yield f


if __name__ == '__main__':
    s = CacheScanner.get_scanner()
    for m in s.scan():
        print(m)
