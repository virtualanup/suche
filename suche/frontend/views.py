from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpRequest
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.contrib import messages
from linguistic.queryhandler import QueryHandler
from engine.result import SucheResult
from engine.search import SucheSearch
from indexer.models import SucheURL
from crawler.models import Rawdata
from django.shortcuts import get_object_or_404
from plugin.pluginProcess import *

def home(request):
    '''
    This is the search engine home page handler.
    '''

    template = loader.get_template('frontend/home.html')

    query = request.REQUEST.get('q','')
    correctedquery = ''
    parsedquery=''
    if query:
        # if the user entered some text, record it
        correctedquery = QueryHandler.correct_query(query)        
        QueryHandler.register_query(correctedquery)
             
        
    context = RequestContext(request, {
        'title': "Suche",
        'query' : query,
        'correctedquery' : correctedquery,
        'user' : request.user,
        
    })
    return HttpResponse(template.render(context))

def autocomplete(request):
    '''
    Auto complete for suche
    auto completes the user entered sentence
    to test this view,
    http://127.0.0.1:8000/autocomplete?callback=autocomplete&search=a
    '''

    completions = []
    if 'search' in request.REQUEST:
        completions = QueryHandler.get_completions(request.REQUEST['search'])
        resp='<table style="width:100%;" class="text-left">'

        for compl in completions:
            resp=resp+'<tr class="autoRow"><td>'
            compl2=compl.replace(request.REQUEST['search'],'<strong>'+request.REQUEST['search']+'</strong>')
            resp=resp+str(compl2)
            resp=resp+'</tr>'
    resp=resp+"</table>"
    return HttpResponse(resp)

def searchresult(request):
    '''
      returns the search result div
      the url is /searchresult
    '''
    query = request.REQUEST.get('q','')
    query=' '.join(query.split())
    if not query:
        return HttpResponse("Please enter your query")

    search = SucheSearch()
    correct = True

    try:
        if request.GET['force'] == '1':
            correct = False
    except:
        pass
    search.SetQuery(query,correct)
    search.search()
    '''query
    parsing
    '''
    parsedquery=QueryHandler.parse_query(search.correctedquery)
    pluginOp=''
    hasPluginOp=False
        #check if op is to be shown
    if parsedquery[0]==(-1):
        pluginOp='no match'
    else:
        if parsedquery[0].plugin.showsOp:
            hasPluginOp=True
            q=PluginProcessor(parsedquery[0],parsedquery[1])
            pluginOp=q.dispatchandRead()
            if(pluginOp==b'err'):
                hasPluginOp=False
    
    template = loader.get_template('frontend/result.html')

    context = RequestContext(request, {
        'query' : search.query,
        'correctedquery' : search.correctedquery,
        'corrected' : search.isQueryCorrected,
        'results':search.results,
        'resultcount' : len(search.results),
        'totalresults': search.totalresult,
        'hasresult' : True if len(search.results) > 0 else False,
        'hasPluginOp':hasPluginOp,
        'pluginOp':pluginOp,
    })
    return HttpResponse(template.render(context))
def websitecache(request):
    url = request.GET.get('page','')
    if len(url) > 4:
        urlobj = get_object_or_404(SucheURL, url=url)
        data = get_object_or_404(Rawdata,url = urlobj)
        return HttpResponse(data.old_data)
    # show 404 error page
    raise Http404
