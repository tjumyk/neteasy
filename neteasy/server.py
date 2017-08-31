import json
import os

from flask import Flask, jsonify, send_from_directory

from neteasy.cache import CacheScanner
from neteasy.model import MusicMetaInfo, Music
from neteasy.web import WebInfoExtractor

app = Flask(__name__)

with open('config.json') as f:
    config = json.load(f)
import_cache_folder = config['import_cache_folder'] or None
scanner = CacheScanner.get_scanner(import_cache_folder)

META_CACHE_FOLDER = config['meta_cache_folder']
if not os.path.isdir(META_CACHE_FOLDER):
    os.makedirs(META_CACHE_FOLDER)

scan_total = 0
scanning = False
scan_completed = 0
never_scan = True
music_list = []


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
    for f in files:
        if not CacheScanner.check_file_md5(f.path, f.md5):
            print('[Warning] %s is corrupted' % f)
            continue
        meta = _get_meta_info(f.mid)
        music = Music(f.mid, meta, f)
        music_list.append(music)
        scan_completed += 1
    scanning = False
    print('Scanning finished!')


def _get_meta_info(mid):
    meta_path = os.path.join(META_CACHE_FOLDER, '%s.json' % str(mid))
    if os.path.isfile(meta_path):
        with open(meta_path) as f:
            return MusicMetaInfo.from_obj(json.load(f))
    print('Requesting web for meta data of music (id=%s)...' % mid)
    meta = WebInfoExtractor.get_music_meta(mid)
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


@app.route('/file/<mid>')
def get_music_file(mid):
    for m in music_list:
        if m.mid == mid:
            path = m.file.path
            return send_from_directory(os.path.dirname(path), os.path.basename(path))
    return jsonify(error='Music [mid=%s] not found' % mid), 404


def run_server():
    app.run(**config['server'])
