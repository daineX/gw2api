from pyttp.controller import (
    Controller,
    expose,
    TemplateResponse,
    )

from api import LANGUAGES, MATCHUPS, MATCH_DETAILS

def get_lang(request):
    lang = request.GET.get('lang', 'en')
    if lang not in LANGUAGES:
        lang = 'en'
    return lang

class GW2MainController(Controller):

    @expose
    def index(self, request):
        lang = get_lang(request)
        context = dict(matches=MATCHUPS.matches(lang),
                       lang=lang)
        return TemplateResponse('index.pyml', context)

    @expose
    def match(self, request, match_id="1-1"):
        lang = get_lang(request)
        scores, maps = MATCH_DETAILS.get_details(match_id, lang)
        context = dict(scores=scores,
                       maps=maps)
        return TemplateResponse('match.pyml', context)
