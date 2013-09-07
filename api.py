from datetime import datetime, timedelta
import json
from multiprocessing import Queue, Process
import os
from Queue import Empty as QueueEmpty
from urllib2 import urlopen

from settings import BASE_DIR


TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

OBJECTIVE_DATA = json.loads(open(os.path.join(BASE_DIR, "objectives.json")).read())

class APIObject(object):

    URL = ''
    TIMEOUT = 10

    def __init__(self):
        self.last_update = datetime.now()
        self.cache = {}
        self.queue = Queue(20)
        self.getter = Process(target=self.async_update, args=(self.queue,))
        self.getter.start()

    def update_cache(self, args):
        url = self.URL.format(*args)
        print "APIURL", url
        data = json.loads(urlopen(url).read())
        self.cache[args] = data
        self.last_update = datetime.now()

    def async_update(self, queue):
        while True:
            args = queue.get()
            self.update_cache(args)

    def get_data(self, *args):
        now = datetime.now()
        if (self.TIMEOUT is not None
            and now > self.last_update + timedelta(seconds=self.TIMEOUT)):
                self.queue.put(args)
        if args not in self.cache:
            self.update_cache(args)
        return self.cache[args]


class Match(object):

    def __init__(self, server_names, match_data):
        self.blue = server_names[match_data["blue_world_id"]]
        self.red = server_names[match_data["red_world_id"]]
        self.green = server_names[match_data["green_world_id"]]
        self.start_time = datetime.strptime(match_data["start_time"], TIME_FORMAT)
        self.end_time = datetime.strptime(match_data["end_time"], TIME_FORMAT)
        self.match_id = match_data["wvw_match_id"]


    def __unicode__(self):
        return u'Blue: {}, Red: {}, Green: {}'.format(self.blue, self.red, self.green)


class ServerNames(APIObject):

    TIMEOUT = None

    URL = 'https://api.guildwars2.com/v1/world_names.json?lang={}'

    def get_names(self, language='en'):
        data = self.get_data(language)
        return {int(d['id']): d['name'] for d in data}


class WvWMatchups(APIObject):

    URL = 'https://api.guildwars2.com/v1/wvw/matches.json'

    def __init__(self, server_names):
        super(WvWMatchups, self).__init__()
        self.server_names = server_names

    def matches(self, lang='en'):
        data = self.get_data()
        for match_data in data["wvw_matches"]:
            yield Match(self.server_names[lang], match_data)


def scores_to_dict(scores):
    return dict(zip(('red', 'blue', 'green'), scores))


class GuildDetails(APIObject):
    URL = "https://api.guildwars2.com/v1/guild_details.json?guild_id={}"
    TIMEOUT = 3600

    def get_name(self, guild_id):
        data = self.get_data(guild_id)
        return data["guild_name"]

    def get_tag(self, guild_id):
        data = self.get_data(guild_id)
        return data["tag"]

class WvWObjective(object):

    def __init__(self, objective_data, lang):
        self.owner = objective_data["owner"]
        self.id = objective_data["id"]
        self.name = objective_data["name"][lang]
        self.owner_guild = objective_data.get("owner_guild")
        if self.owner_guild:
            self.guild_name = GUILD_DETAILS.get_name(self.owner_guild)
            self.guild_tag = GUILD_DETAILS.get_tag(self.owner_guild)
        else:
            self.guild_name = None
            self.guild_tag = None

class WvWMap(object):

    def __init__(self, map_data, lang="en"):
        self.type = map_data["type"]
        self.scores = scores_to_dict(map_data["scores"])
        self.inject_objective_data(map_data)
        self.objectives = [WvWObjective(objective_data, lang)
                           for objective_data in map_data["objectives"]]


    def inject_objective_data(self, map_data):
        loaded_data = OBJECTIVE_DATA[self.type]
        for ldata, odata in zip(loaded_data, map_data["objectives"]):
            odata.update(ldata)

class MatchDetails(APIObject):

    URL = "https://api.guildwars2.com/v1/wvw/match_details.json?match_id={}"

    def __init__(self, server_names):
        super(MatchDetails, self).__init__()
        self.server_names = server_names

    def get_details(self, match_id, lang='en'):
        data = self.get_data(match_id)
        scores = scores_to_dict(data["scores"])
        maps = [WvWMap(map, lang) for map in data["maps"]]
        return scores, maps



LANGUAGES = ('en', 'de', 'fr', 'es')
name_getter = ServerNames()
SERVER_NAMES = {lang: name_getter.get_names(lang) for lang in LANGUAGES}

MATCHUPS = WvWMatchups(SERVER_NAMES)
MATCH_DETAILS = MatchDetails(SERVER_NAMES)
GUILD_DETAILS = GuildDetails()

