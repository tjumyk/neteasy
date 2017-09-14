import os
root = os.path.dirname(os.path.realpath(__file__))
activate_this = root + '/.venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

#import sys
#sys.path.insert(0, root)

from neteasy.server import app as application

