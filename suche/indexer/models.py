'''
Indexer model for django
copyright (c) 2014 by anup pokhrel
'''

from django.db import models
from urllib.parse import urlparse

class SucheURL(models.Model):
    '''
    SucheURL represents a unique URL.
    Each unique URL has it's own rank and records.
    '''
    url = models.CharField(max_length=200,primary_key=True)

    rank = models.FloatField(default = 0.0)
    title = models.TextField(default = '')
    body = models.TextField(default = '')

    def __str__(self):
        return self.url

    # some helper functions for URL
    def isvalid(url):
        '''
        returns if a URL is valid or not.nnn
        We reject extensions without htm, html and php at all times (like js, css, png, etc)
        Also, during testing time, reject any URLs not in specified domain list. Alos, only http
        protocol is allowed
        '''
        allowedurls = ['http://bbc.com','http://en.wikipedia.org/','http://reddit.com']
        valid = False
        for aurl in allowedurls:
            if url.startswith(aurl):
                valid = True
        if not valid:
            return False
        #check other conditions
        return True

    def filterURL(url):
        '''
        filterurl removes the unnecessary parameters from the URL. 
        Get parameters are removed, javascript hashes are removed, 
        '''
        from urllib.parse import urlparse
        o = urlparse(url)
        url_without_query_string = o.scheme + "://" + o.netloc + o.path
        return url_without_query_string

    def getDomain(self):
        '''
        returns the domain of the current URL
        '''
        o = urlparse(self.url)
        domain = o.scheme + "://" + o.netloc
        return domain

    def update_rank(self):
        '''
        Update the page rank of this URL
        Here is what we do: we find all the URLs linking to this URL from another domain.
        We calculate the rank of this website by the equation

        TODO: A seperate bot will randomly iterate through the URLs calculating their page rank
        Page rank settles to a steady value after certain iterations.
        '''
        #first of all, get a list of all links that point to the current URL
        damping = 0.85 # our damping factor
        #get the list of all URLs linking to this URL
        links = Link.objects.filter(tourl = self)
        mydomain = self.getDomain()

        sumpr = 0
        for link in links:
            url = link.fromurl
            if mydomain != url.getDomain():
                # if the link is from another domain
                # sumpr = pagerank of url / no of links originating in url
                sumpr += url.rank / Link.objects.filter(fromurl = url).count()
        self.rank = (1-damping) + damping * sumpr

class Link(models.Model):
    '''
    This class represents a link from one url to another url in the form of
    anchor
    '''
    fromurl = models.ForeignKey(SucheURL, related_name = "link_origin")
    tourl = models.ForeignKey(SucheURL, related_name = "link_destination")
    text = models.TextField(default = '', max_length = 50) # allow 50 characters in anchor for now

    def __str__(self):
        return self.fromurl.url + " - "+self.tourl.url

class Word(models.Model):
    '''
    This word represents the word in the HTML documents
    this is different from the linguistic word table as this
    word contains list of words contained in any one of
    the HTML document
    '''
    word = models.TextField(max_length = 50)
    wordcount = models.IntegerField(default = 0)
    def __str__(self):
        return self.word

class Result(models.Model):
    '''
    This stores the search result for a single word and single URL
    '''
    word = models.ForeignKey(Word)
    url = models.ForeignKey(SucheURL)
    wordrank = models.IntegerField(default = 0)
    titlewordcount = models.IntegerField(default = 0)
    linkswordcount = models.IntegerField(default = 0)
    userrank = models.IntegerField(default = 0) # this depends on user activity
    urlpoint = models.IntegerField(default = 0)

    def __str__(self):
        return self.word.word + ' - '+ self.url.url
