import json
import os
import sys
import threading
import time
from multiprocessing.pool import ThreadPool

import requests
from flask import Flask, jsonify, send_from_directory, request

from neteasy.cache import CacheScanner
from neteasy.model import MusicMetaInfo, Music
from neteasy.web import WebInfoExtractor

app = Flask(__name__)

with open('config.json') as f:
    config = json.load(f)
SERVER_URL = 'http://%s:%d' % (config['server']['host'], config['server']['port'])
IMPORT_CACHE_FOLDER = config['import_cache_folder'] or None
scanner = CacheScanner.get_scanner(IMPORT_CACHE_FOLDER)

META_CACHE_FOLDER = config['meta_cache_folder']
COVER_CACHE_FOLDER = config['cover_cache_folder']
MD5_CACHE_FOLDER = config['md5_cache_folder']
if not os.path.isdir(META_CACHE_FOLDER):
    os.makedirs(META_CACHE_FOLDER)
if not os.path.isdir(COVER_CACHE_FOLDER):
    os.makedirs(COVER_CACHE_FOLDER)
if not os.path.isdir(MD5_CACHE_FOLDER):
    os.makedirs(MD5_CACHE_FOLDER)

scan_total = 0
scanning = False
scan_completed = 0
_scan_completed_lock = threading.Lock()
SCAN_THREADS = config['scan_threads']
never_scan = True
music_list = []


def _scan_for_one(file):
    global scan_completed
    try:
        md5 = None
        md5_cache_file = os.path.join(MD5_CACHE_FOLDER, '%s.json' % file.mid)
        if os.path.isfile(md5_cache_file):
            with open(md5_cache_file) as f_md5_cache:
                md5_cache = json.load(f_md5_cache)
            if md5_cache['mtime'] == file.mtime:
                md5 = md5_cache['md5']
        if md5 is None:
            md5 = CacheScanner.get_file_md5(file.path)
            with open(md5_cache_file, 'w') as f_md5_cache:
                md5_cache = {'mtime': file.mtime, 'md5': md5}
                json.dump(md5_cache, f_md5_cache, indent=4)
        if md5 != file.md5:
            print('[Warning] %s is corrupted' % repr(file))
            return
        try:
            meta = _get_meta_info(file.mid)
        except Exception as e:
            print("[Warning] Failed to get the meta data of music (id=%s)" % file.mid)
            print(e)
            return
        music = Music(file.mid, meta, file)
        music_list.append(music)
    finally:
        _scan_completed_lock.acquire()
        scan_completed += 1
        _scan_completed_lock.release()


def _scan():
    global scan_total, scan_completed, music_list, scanning, never_scan
    never_scan = False
    if scanning:
        raise RuntimeError('Already scanning!')
    print('Start scanning...')
    scanning = True
    music_list = []
    files = list(scanner.scan())
    scan_total = len(files)
    scan_completed = 0
    with ThreadPool(SCAN_THREADS) as pool:
        pool.map(_scan_for_one, files)
    scanning = False
    print('Scanning finished!')


def _get_meta_info(mid):
    meta_path = os.path.join(META_CACHE_FOLDER, '%s.json' % str(mid))
    if os.path.isfile(meta_path):
        with open(meta_path) as f:
            return MusicMetaInfo.from_obj(json.load(f))
    print('Requesting web for meta data of music (id=%s)...' % mid)
    meta = WebInfoExtractor.get_music_meta(mid)

    if meta.cover_img is not None:
        ext = os.path.splitext(meta.cover_img)[1]
        cover_name = '%s%s' % (str(mid), ext)
        cover_path = os.path.join(COVER_CACHE_FOLDER, cover_name)
        img = WebInfoExtractor.get_from_url(meta.cover_img)
        with open(cover_path, 'wb') as f2:
            f2.write(img)
        meta.cover_img_alt = "/cover/%s" % cover_name
    with open(meta_path, 'w') as f:
        json.dump(meta.to_obj(), f, indent=4)
    return meta


@app.route('/')
def index():
    return app.send_static_file('base.html')


@app.route('/api/status')
def get_status():
    return jsonify(
        never_scan=never_scan,
        scanning=scanning,
        scan_total=scan_total,
        scan_completed=scan_completed
    )


@app.route('/api/list')
def get_list():
    return jsonify([m.to_obj() for m in music_list])


@app.route('/api/scan')
def scan():
    _scan()
    return jsonify([m.to_obj() for m in music_list])


@app.route('/music/<mid_format>')
def get_music_file(mid_format):
    mid, fmt = os.path.splitext(mid_format)
    fmt = fmt.strip('.')
    for m in music_list:
        if m.mid == mid:
            if m.file.file_format != fmt:
                return jsonify(error='Music [mid=%s] is not in "%s" format' % (mid, fmt)), 400
            path = m.file.path
            return send_from_directory(os.path.dirname(path), os.path.basename(path))
    return jsonify(error='Music [mid=%s] not found' % mid), 404


@app.route('/cover/<filename>')
def get_cover_image(filename):
    return send_from_directory(os.path.abspath(COVER_CACHE_FOLDER), filename)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


def run_server():
    app.run(**config['server'])


def shutdown_server():
    requests.post("%s/shutdown" % SERVER_URL)


def _wait_server_ready(callback):
    while True:
        time.sleep(0.2)
        try:
            r = requests.get("%s/api/status" % SERVER_URL)
            if r.status_code == 200:
                callback()
            else:
                print('[Warning] Server is in abnormal state')
            break
        except ConnectionError:
            pass


def run_sys_tray():
    import webbrowser
    import pystray
    from PIL import Image

    def _sys_tray_main(_icon: pystray.Icon):
        _icon.visible = True
        threading.Thread(target=_wait_server_ready, args=[_open_browser]).start()
        run_server()

    def _open_browser():
        webbrowser.open(SERVER_URL)

    def _sys_tray_stop():
        shutdown_server()
        icon.visible = False
        icon.stop()

    icon = pystray.Icon(
        name='neteasy',
        icon=Image.open('neteasy/static/image/logo-64.png'),
        title='Neteasy Music Server',
        menu=pystray.Menu(
            pystray.MenuItem('Open', _open_browser, default=True),
            pystray.MenuItem('Stop Server', _sys_tray_stop)
        )
    )

    icon.run(_sys_tray_main)


def run_cef():
    from cefpython3 import cefpython as cef

    assert cef.__version__ >= "55.3", "CEF Python v55.3+ is required"
    threading.Thread(target=run_server).start()

    class OnBeforeCloseHandler:
        def OnBeforeClose(self, browser):
            shutdown_server()

    def _open_cef_window():
        sys.excepthook = cef.ExceptHook
        cef.Initialize()
        browser = cef.CreateBrowserSync(url=SERVER_URL, window_title="NetEasy Music Player")
        browser.SetClientHandler(OnBeforeCloseHandler())
        cef.MessageLoop()
        cef.Shutdown()

    _wait_server_ready(_open_cef_window)
