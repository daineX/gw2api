from os.path import dirname, expanduser, join

BASE_DIR = dirname(__file__)

IMAGE_UPLOAD_FOLDER = expanduser("~/.pyttp/images")
IMAGE_SERVE_ROOT = "/images"

TEMPLATE_SEARCH_PATH = join(BASE_DIR, "templates")
