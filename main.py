import os
import sys

from pyttp.settings import load
settings = load()
from pyttp.scaffold import make_controller_listener

from views import GW2MainController

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 8080

controller = GW2MainController()
httpd = make_controller_listener(controller, port=port)
httpd.serve()
