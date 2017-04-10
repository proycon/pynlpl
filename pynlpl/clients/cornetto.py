# -*- coding: utf-8 -*-

###############################################################
#  PyNLPl - Remote Cornetto Client
#       Adapted from code by Fons Laan (ILPS-ISLA, UvA)
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# This is a Python library for connecting to a Cornetto database.
# Originally coded by Fons Laan (ILPS-ISLA, University of Amsterdam) 
# for DutchSemCor.
#
# The library currently has only a minimal set of functionality compared
# to the original. It will be extended on a need-to basis.
#
###############################################################


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import    
    

import sys
import httplib2                    # version 0.6.0+
if sys.version < '3':
    import urlparse
    import httplib                    
else:
    from urllib import parse as urlparse # renamed to urllib.parse in Python 3.0
    import http.client as httplib #renamed in Python 3 
import urllib, base64
from sys import stderr 
#import pickle

printf = lambda x: sys.stdout.write(x+ "\n")

from lxml import etree


class CornettoClient(object):
    def __init__(self, user='gast',password='gast',host='debvisdic.let.vu.nl', port=9002, path = '/doc', scheme='https',debug=False):
        self.host = host
        self.port = port
        self.path = path
        self.scheme = scheme
        self.debug = debug
        self.userid = user
        self.passwd = password

    def connect(self):
        if self.debug:
            printf( "cornettodb/views/remote_open()" )
        # permission denied on cornetto with apache
        #    http = httplib2.Http( ".cache" )
        try:
            http = httplib2.Http(disable_ssl_certificate_validation=True)
        except TypeError:
            print >>stderr, "[CornettoClient] WARNING: Older version of httplib2! Can not disable_ssl_certificate_validation" 
            http = httplib2.Http() #for older httplib2 

        # VU DEBVisDic authentication
        http.add_credentials( self.userid, self.passwd )


        params   = ""
    #    query    = "action=init"                    # obsolete
        query    = "action=connect"
        fragment = ""

        db_url_tuple = ( self.scheme, self.host + ':' + str(self.port), self.path, params, query, fragment )
        db_url = urlparse.urlunparse( db_url_tuple )

        if self.debug:
            printf( "db_url: %s" % db_url )
            printf( "http.request()..." );

        try:
            resp, content = http.request( db_url, "GET" )
            if self.debug:
                printf( "resp:\n%s" % resp )
                printf( "content:\n%s" % content )
        except:
            printf( "...failed." );
            # when CORNETTO_HOST is off-line, we do not have a response
            resp = None
            content = None

        return http, resp, content

    def get_syn_ids_by_lemma(self, lemma):
        """Returns a list of synset IDs based on a lemma"""
        if not isinstance(lemma,unicode):
            lemma = unicode(lemma,'utf-8')


        http, resp, content = self.connect()

        params   = ""
        fragment = ""

        path = "cdb_syn"
        if self.debug:
            printf( "cornettodb/views/query_remote_syn_lemma: db_opt: %s" % path )

        query_opt = "dict_search"
        if self.debug:
            printf( "cornettodb/views/query_remote_syn_lemma: query_opt: %s" % query_opt )
    
        qdict = {}
        qdict[ "action" ] = "queryList"
        qdict[ "word" ]   = lemma.encode('utf-8')


        query = urllib.urlencode( qdict )

        db_url_tuple = ( self.scheme, self.host + ':' + str(self.port), path, params, query, fragment )
        db_url = urlparse.urlunparse( db_url_tuple )
        if self.debug:
            printf( "db_url: %s" % db_url )

        resp, content = http.request( db_url, "GET" )
        if self.debug:
            printf( "resp:\n%s" % resp )
            printf( "content:\n%s" % content )
        #    printf( "content is of type: %s" % type( content ) )

        dict_list = []
        dict_list = eval( content )        # string to list

        synsets = []
        items = len( dict_list )
        if self.debug:
            printf( "items: %d" % items )

        # syn dict: like lu dict, but without pos: part-of-speech
        for dict in dict_list:
            if self.debug:
                printf( dict )

            seq_nr = dict[ "seq_nr" ]   # sense number
            value  = dict[ "value" ]    # lexical unit identifier
            form   = dict[ "form" ]     # lemma
            label  = dict[ "label" ]    # label to be shown

            if self.debug:
                printf( "seq_nr: %s" % seq_nr )
                printf( "value:  %s" % value )
                printf( "form:   %s" % form )
                printf( "label:  %s" % label )

            if value != "":
                synsets.append( value )

        return synsets


    def get_lu_ids_by_lemma(self, lemma, targetpos = None):
        """Returns a list of lexical unit IDs based on a lemma and a pos tag"""
        if not isinstance(lemma,unicode):
            lemma = unicode(lemma,'utf-8')


        http, resp, content = self.connect()

        params   = ""
        fragment = ""

        path = "cdb_lu"

        query_opt = "dict_search"

        qdict = {}
        qdict[ "action" ] = "queryList"
        qdict[ "word" ]   = lemma.encode('utf-8')


        query = urllib.urlencode( qdict )

        db_url_tuple = ( self.scheme, self.host + ':' + str(self.port), path, params, query, fragment )
        db_url = urlparse.urlunparse( db_url_tuple )
        if self.debug:
            printf( "db_url: %s" % db_url )

        resp, content = http.request( db_url, "GET" )
        if self.debug:
            printf( "resp:\n%s" % resp )
            printf( "content:\n%s" % content )
        #    printf( "content is of type: %s" % type( content ) )

        dict_list = []
        dict_list = eval( content )        # string to list

        ids = []
        items = len( dict_list )
        if self.debug:
            printf( "items: %d" % items )

        for d in dict_list:
            if self.debug:
                printf( d )

            seq_nr = d[ "seq_nr" ]   # sense number
            value  = d[ "value" ]    # lexical unit identifier
            form   = d[ "form" ]     # lemma
            label  = d[ "label" ]    # label to be shown
            pos  = d[ "pos" ]    # label to be shown

            if self.debug:
                printf( "seq_nr: %s" % seq_nr )
                printf( "value:  %s" % value )
                printf( "form:   %s" % form )
                printf( "label:  %s" % label )

            if value != "" and ((not targetpos) or (targetpos and pos == targetpos)):
                ids.append( value )

        return ids



    def get_synset_xml(self,syn_id):
        """
        call cdb_syn with synset identifier -> returns the synset xml;
        """

        http, resp, content = self.connect()

        params   = ""
        fragment = ""

        path = "cdb_syn"
        if self.debug:
            printf( "cornettodb/views/query_remote_syn_id: db_opt: %s" % path )

        # output_opt: plain, html, xml
        # 'xml' is actually xhtml (with markup), but it is not valid xml!
        # 'plain' is actually valid xml (without markup)
        output_opt = "plain"
        if self.debug:
            printf( "cornettodb/views/query_remote_syn_id: output_opt: %s" % output_opt )

        action = "runQuery"
        if self.debug:
            printf( "cornettodb/views/query_remote_syn_id: action: %s" % action )
            printf( "cornettodb/views/query_remote_syn_id: query: %s" % syn_id )

        qdict = {}
        qdict[ "action" ]  = action
        qdict[ "query" ]   = syn_id
        qdict[ "outtype" ] = output_opt

        query = urllib.urlencode( qdict )

        db_url_tuple = ( self.scheme, self.host + ':' + str(self.port), path, params, query, fragment )
        db_url = urlparse.urlunparse( db_url_tuple )
        if self.debug:
            printf( "db_url: %s" % db_url )

        resp, content = http.request( db_url, "GET" )
        if self.debug:
            printf( "resp:\n%s" % resp )
        #    printf( "content:\n%s" % content )
        #    printf( "content is of type: %s" % type( content ) )        #<type 'str'>

        xml_data = eval( content )
        return etree.fromstring( xml_data )


    def get_lus_from_synset(self, syn_id):
        """Returns a list of (word, lu_id) tuples given a synset ID"""

        root = self.get_synset_xml(syn_id)
        elem_synonyms = root.find( ".//synonyms" )


        lus = []
        for elem_synonym in elem_synonyms:
            synonym_str = elem_synonym.get( "c_lu_id-previewtext" )        # get "c_lu_id-previewtext" attribute
            # synonym_str ends with ":<num>"
            synonym = synonym_str.split( ':' )[ 0 ].strip()
            lus.append( (synonym, elem_synonym.get( "c_lu_id") ) )
        return lus


    def get_lu_from_synset(self, syn_id, lemma = None):
        """Returns (lu_id, synonyms=[(word, lu_id)] ) tuple given a synset ID and a lemma"""
        if not lemma:
            return self.get_lus_from_synset(syn_id) #alias
        if not isinstance(lemma,unicode):
            lemma = unicode(lemma,'utf-8')

        root = self.get_synset_xml(syn_id)
        elem_synonyms = root.find( ".//synonyms" )

        lu_id = None
        synonyms = []
        for elem_synonym in elem_synonyms:
            synonym_str = elem_synonym.get( "c_lu_id-previewtext" )        # get "c_lu_id-previewtext" attribute
            # synonym_str ends with ":<num>"
            synonym = synonym_str.split( ':' )[ 0 ].strip()

            if synonym != lemma:
                synonyms.append( (synonym, elem_synonym.get("c_lu_id")) )
                if self.debug:
                    printf( "synonym add: %s" % synonym )
            else:
                lu_id = elem_synonym.get( "c_lu_id" )        # get "c_lu_id" attribute
                if self.debug:
                    printf( "lu_id: %s" % lu_id )
                    printf( "synonym skip lemma: %s" % synonym )
        return lu_id, synonyms



##################################################################################################################
#            ORIGINAL AND AS-OF-YET UNUSED CODE (included for later porting)
##################################################################################################################

"""
--------------------------------------------------------------------------------
Original Author:     Fons Laan, ILPS-ISLA, University of Amsterdam
Original Project:    DutchSemCor
Original Name:        cornettodb/views.py
Original Version:    0.2
Goal:        Cornetto views definitions

Original functions:
    index( request )
    local_open()
    remote_open( self.debug )
    search( request )
    search_local( dict_in, search_query )
    search_remote( dict_in, search_query )
    cornet_check_lusyn( utf8_lemma )
    query_remote_lusyn_id( syn_id_self.debug, http, utf8_lemma, syn_id )
    query_cornet( keyword, category )
    query_remote_syn_lemma( self.debug, http, utf8_lemma )
    query_remote_syn_id( self.debug, http, utf8_lemma, syn_id, domains_abbrev )
    query_remote_lu_lemma( self.debug, http, utf8_lemma )
    query_remote_lu_id( self.debug, http, lu_id )
FL-04-Sep-2009: Created
FL-03-Nov-2009: Removed http global: sometimes it was None; missed initialization?
FL-01-Feb-2010: Added Category filtering
FL-15-Feb-2010: Tag counts -> separate qx query
FL-07-Apr-2010: Merge canonical + textual examples
FL-10-Jun-2010: Latest Change
MvG-29-Sep-2010: Turned into minimal CornettoClient class, some new functions added, many old ones disabled until necessary
"""

#    def query_remote(self, dict_in, search_query ):
#        if self.debug: printf( "cornettodb/views/query_remote" )

#        http, resp, content = self.remote_open()

#        if resp is None:
#            raise Exception("No response")


#        status = int( resp.get( "status" ) )
#        if self.debug: printf( "status: %d" % status )

#        if status != 200:
#            # e.g. 400: Bad Request, 404: Not Found
#            raise Exception("Error in request")


#        path = dict_in[ 'dbopt' ]
#        if self.debug: printf( "cornettodb/views/query_remote: db_opt: %s" % path )

#        output_opt = dict_in[ 'outputopt' ]
#        if self.debug: printf( "cornettodb/views/query_remote: output_opt: %s" % output_opt )

#        query_opt = dict_in[ 'queryopt' ]
#        if self.debug: printf( "cornettodb/views/query_remote: query_opt: %s" % query_opt )

#        params   = ""
#        fragment = ""

#        qdict = {}
#        if query_opt == "dict_search":
#        #    query = "action=queryList&word=" + search_query
#            qdict[ "action" ] = "queryList"
#            qdict[ "word" ]   = search_query

#        elif query_opt == "query_entry":
#        #    query = "action=runQuery&query=" + search_query
#        #    query += "&outtype=" + output_opt
#            qdict[ "action" ]  = "runQuery"
#            qdict[ "query" ]   = search_query
#            qdict[ "outtype" ] = output_opt

#        # instead of "subtree" there is also "tree" and "full subtree"
#        elif query_opt == "subtree_entry":
#        #    query = "action=subtree&query=" + search_query
#        #    query += "&arg=ILR"            # ILR = Internal Language Relations, RILR = Reversed ...
#        #    query += "&outtype=" + output_opt
#            qdict[ "action" ]  = "subtree"
#            qdict[ "query" ]   = search_query
#            qdict[ "arg" ]     = "ILR"    # ILR = Internal Language Relations, RILR = Reversed ...
#            qdict[ "outtype" ] = output_opt

#        # More functions, see DEBVisDic docu:
#        #    Save entry
#        #    Delete entry
#        #    Next sense number
#        #    "Translate" synsets 

#        query = urllib.urlencode( qdict )

#        db_url_tuple = ( self.scheme, self.host+ ':' + str(self.post), self.path, params, query, fragment )
#        db_url = urlparse.urlunparse( db_url_tuple )
#        if self.debug: printf( "db_url: %s" % db_url )

#        resp, content = http.request( db_url, "GET" )
#        printf( "resp:\n%s" % resp )
#        if self.debug: printf( "content:\n%s" % content )

#        if content.startswith( '[' ) and content.endswith( ']' ):
#            reply = eval( content )        # string -> list
#            islist = True
#        else:
#            reply = content
#            islist = False

#        return reply


#    def cornet_check_lusyn( self, utf8_lemma ):
#        http, resp, content = remote_open( self.debug )

#        # get the raw (unfiltered) lexical unit identifiers for this lemma
#        lu_ids_lemma = query_remote_lu_lemma( http, utf8_lemma )

#        # get the synset identifiers for this lemma
#        syn_ids_lemma = query_remote_syn_lemma( http, utf8_lemma )

#        lu_ids_syn = []
#        for syn_id in syn_ids_lemma:
#            lu_id = query_remote_lusyn_id( http, utf8_lemma, syn_id )
#            lu_ids_syn.append( lu_id )

#        return lu_ids_lemma, syn_ids_lemma, lu_ids_syn



#    def query_remote_lusyn_id( http, utf8_lemma, syn_id ):
#        """
#        query_remote_lusyn_id\
#        call cdb_syn with synset identifier -> synset xml -> lu_id lemma
#        """
#        scheme   = settings.CORNETTO_PROTOCOL
#        netloc   = settings.CORNETTO_HOST + ':' +  str( settings.CORNETTO_PORT )
#        params   = ""
#        fragment = ""

#        path = "cdb_syn"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lusyn_id: db_opt: %s" % path )

#        # output_opt: plain, html, xml
#        # 'xml' is actually xhtml (with markup), but it is not valid xml!
#        # 'plain' is actually valid xml (without markup)
#        output_opt = "plain"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lusyn_id: output_opt: %s" % output_opt )

#        action = "runQuery"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lusyn_id: action: %s" % action )
#            printf( "cornettodb/views/query_remote_lusyn_id: query: %s" % syn_id )
#    
#        qdict = {}
#        qdict[ "action" ]  = action
#        qdict[ "query" ]   = syn_id
#        qdict[ "outtype" ] = output_opt

#        query = urllib.urlencode( qdict )

#        db_url_tuple = ( scheme, netloc, path, params, query, fragment )
#        db_url = urlparse.urlunparse( db_url_tuple )
#        if self.debug:
#            printf( "db_url: %s" % db_url )

#        resp, content = http.request( db_url, "GET" )
#        if self.debug:
#            printf( "resp:\n%s" % resp )
#        #    printf( "content:\n%s" % content )
#        #    printf( "content is of type: %s" % type( content ) )        # <type 'str'>

#        xml_data = eval( content )
#        root = etree.fromstring( xml_data )

#        synonyms = []
#        # find <synonyms> anywhere in the tree
#        elem_synonyms = root.find( ".//synonyms" )
#        for elem_synonym in elem_synonyms:
#            synonym_str = elem_synonym.get( "c_lu_id-previewtext" )        # get "c_lu_id-previewtext" attribute
#            # synonym_str ends with ":<num>"
#            synonym = synonym_str.split( ':' )[ 0 ].strip()

#            utf8_synonym = synonym.encode( 'utf-8' )
#            if utf8_synonym != utf8_lemma:
#                synonyms.append( synonym )
#                if self.debug:
#                    printf( "synonym add: %s" % synonym )
#            else:
#                lu_id = elem_synonym.get( "c_lu_id" )                    # get "c_lu_id" attribute
#                if self.debug:
#                    printf( "lu_id: %s" % lu_id )
#                    printf( "synonym skip lemma: %s" % synonym )

#        return lu_id



#    def query_cornet( annotator_id, utf8_lemma, category ):
#        """\
#        cornet_query()
#        A variant of query_remote(), combining several queries for the dutchsemcor GUI
#        -1- call cdb_syn with lemma -> syn_ids;
#        -2- for each syn_id, call cdb_syn ->synset xml
#        -3- for each synset xml, find lu_id
#        -4- for each lu_id, call cdb_lu ->lu xml
#        -5- collect required info from lu & syn xml    
#        """

#        self.debug = False    # this function

#        printf( "cornettodb/views/cornet_query()" )
#        if utf8_lemma is None or utf8_lemma == "":
#            printf( "No lemma" )
#            return
#        else:
#            printf( "lemma: %s" % utf8_lemma.decode( 'utf-8' ).encode( 'latin-1' ) )
#            printf( "category: %s" % category )

#        http, resp, content = remote_open( self.debug )

#        if resp is None:
#            template = "cornettodb/error.html"
#            dictionary = { 'DSC_HOME' : settings.DSC_HOME }
#            return template, dictionary


#        status = int( resp.get( "status" ) )
#        printf( "status: %d" % status )

#        if status != 200:
#            # e.g. 400: Bad Request, 404: Not Found
#            printf( "status: %d\nreason: %s" % ( resp.status, resp.reason ) )
#            dict_err = \
#            { 
#                "status" : settings.CORNETTO_HOST + " error: " + str(status),
#                "msg"    : resp.reason
#            }
#            return dict_err

#        # read the domain cvs file, and return the dictionaries
#        domains_dutch, domains_abbrev = get_domains()

#        syn_ids    = []    # used syn_ids, skipping filtered
#        lu_ids     = []    # used lu_ids, skipping filtered
#        lu_ids_syn = []    # lu_ids derived from syn_ids, unfiltered

#        # get the raw (unfiltered) synset identifiers for this lemma
#        syn_lemma_self.debug = False
#        syn_ids_raw = query_remote_syn_lemma( syn_lemma_self.debug, http, utf8_lemma )

#        # get the raw (unfiltered) lexical unit identifiers for this lemma
#        lu_lemma_self.debug = False
#        lu_ids_raw = query_remote_lu_lemma( lu_lemma_self.debug, http, utf8_lemma )

#        # required lu info from the lu xml:
#        resumes_lu = []
#        morphos_lu = []
#        examplestext_lulist = []    # list-of-lists
#        examplestype_lulist = []    # list-of-lists
#        examplessubtype_lulist = []    # list-of-lists

#        # required syn info from the synset xml:
#        definitions_syn    = []        # list
#        differentiaes_syn  = []        # list
#        synonyms_synlist   = []        # list-of-lists
#        relations_synlist  = []        # list-of-lists
#        hyperonyms_synlist = []        # list-of-lists
#        hyponyms_synlist   = []        # list-of-lists
#        relations_synlist  = []        # list-of-lists
#        relnames_synlist   = []        # list-of-lists
#        domains_synlist    = []        # list-of-lists

#        remained = 0    # maybe less than lu_ids because of category filtering

#        for syn_id in syn_ids_raw:
#            if self.debug:
#                printf( "syn_id: %s" % syn_id )

#            syn_id_self.debug = False
#            lu_id, definition, differentiae, synonyms, hyperonyms, hyponyms, relations, relnames, domains = \
#                query_remote_syn_id( syn_id_self.debug, http, utf8_lemma, syn_id, domains_abbrev )

#            lu_ids_syn.append( lu_id )

#            lui_id_self.debug = False
#            if self.debug:
#                printf( "lu_id: %s" % lu_id )
#            formcat, morpho, resume, examples_text, examples_type, examples_subtype = \
#                query_remote_lu_id( lui_id_self.debug, http, lu_id )

#            if not ( \
#                ( category == '?' )                       or \
#                ( category == 'a' and formcat == 'adj' )  or \
#                ( category == 'n' and formcat == 'noun' ) or \
#                ( category == 'v' and formcat == 'verb' ) ):
#                if self.debug:
#                    printf( "filtered category: formcat=%s, lu_id=%s" % (formcat, lu_id) )
#                continue

#            # collect all information
#            syn_ids.append( syn_id )
#            lu_ids.append( lu_id )

#            definitions_syn.append( definition )
#            differentiaes_syn.append( differentiae )
#            synonyms_synlist.append( synonyms )
#            hyperonyms_synlist.append( hyperonyms )
#            relations_synlist.append( relations )
#            relnames_synlist.append( relnames )
#            hyponyms_synlist.append( hyponyms )
#            domains_synlist.append( domains )

#            resumes_lu.append( resume )
#            morphos_lu.append( morpho )

#            examplestext_lulist.append( examples_text )
#            examplestype_lulist.append( examples_type )
#            examplessubtype_lulist.append( examples_subtype )

#            if self.debug:
#                printf( "morpho: %s\nresume: %s\nexamples:" % (morpho, resume) )
#                for canoexample in canoexamples:
#                    printf( canoexample.encode('latin-1') )    # otherwise fails with non-ascii chars
#                for textexample in textexamples:
#                    printf( textexample.encode('latin-1') )    # otherwise fails with non-ascii chars

#        lusyn_mismatch = False    # assume no problem
#        # Compare number of lu ids with syn_ids
#        if len( lu_ids_raw ) != len( syn_ids_raw):    # length mismatch
#            lusyn_mismatch = True
#            printf( "query_cornet: %d lu ids, %d syn ids: NO MATCH" % (len(lu_ids_raw), len(syn_ids_raw) ) )

#        # Check lu_ids from syn to lu_ids_raw (from lemma)
#        for i in range( len( lu_ids_raw ) ):
#            lu_id_raw = lu_ids_raw[ i ]
#            try:
#                idx = lu_ids_syn.index( lu_id_raw )
#                if lu_ids_syn.count( lu_id_raw ) != 1:
#                    lusyn_mismatch = True
#                    printf( "query_cornet: %s lu id: DUPLICATES" % lu_id_raw )
#            except:
#                lusyn_mismatch = True
#                printf( "query_cornet: %s lu id: NOT FOUND" % lu_id_raw )


#        dictlist = []

#        for i in range( len( syn_ids ) ):
#        #    printf( "i: %d" % i )

#            dict = {}
#            dict[ "no" ] = i

#            lu_id = lu_ids[ i ]
#            dict[ "lu_id" ] = lu_id

#            syn_id = syn_ids[ i ]
#            dict[ "syn_id" ] = syn_id

#            dict[ "tag_count" ] = '?'

#            resume = resumes_lu[ i ]
#            dict[ "resume" ] = resume

#            morpho = morphos_lu[ i ]
#            dict[ "morpho" ] = morpho

#            examplestext = examplestext_lulist[ i ]
#            dict[ "examplestext"] = examplestext

#            examplestype = examplestype_lulist[ i ]
#            dict[ "examplestype"] = examplestype

#            examplessubtype = examplessubtype_lulist[ i ]
#            dict[ "examplessubtype"] = examplessubtype

#            definition = definitions_syn[ i ]
#            dict[ "definition" ] = definition

#            differentiae = differentiaes_syn[ i ]
#            dict[ "differentiae" ] = differentiae

#            synonyms = synonyms_synlist[ i ]
#            dict[ "synonyms"] = synonyms

#            hyperonyms = hyperonyms_synlist[ i ]
#            dict[ "hyperonyms"] = hyperonyms

#            hyponyms = hyponyms_synlist[ i ]
#            dict[ "hyponyms"] = hyponyms

#            relations = relations_synlist[ i ]
#            dict[ "relations"] = relations

#            relnames = relnames_synlist[ i ]
#            dict[ "relnames"] = relnames

#            domains = domains_synlist[ i ]
#            dict[ "domains"] = domains

#            dictlist.append( dict )    

#        # pack in "superdict"
#        result = \
#        { 
#            "status"          : "ok",
#            "source"          : "cornetto",
#            "lusyn_mismatch"  : lusyn_mismatch,
#            "lusyn_retrieved" : len( syn_ids_raw ),
#            "lusyn_remained"  : len( syn_ids ),
#            "lists_data"      : dictlist
#        }

#        return result



#    def query_remote_lu_lemma( utf8_lemma ):
#        """\
#        call cdb_lu with lemma -> yields lexical units
#        """
#        scheme   = settings.CORNETTO_PROTOCOL
#        netloc   = settings.CORNETTO_HOST + ':' +  str( settings.CORNETTO_PORT )
#        params   = ""
#        fragment = ""

#        path = "cdb_lu"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_lemma: db_opt: %s" % path )

#        action = "queryList"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_lemma: action: %s" % action )

#        qdict = {}
#        qdict[ "action" ] = action
#        qdict[ "word" ]   = utf8_lemma

#        query = urllib.urlencode( qdict )

#        db_url_tuple = ( scheme, netloc, path, params, query, fragment )
#        db_url = urlparse.urlunparse( db_url_tuple )
#        if self.debug:
#            printf( "db_url: %s" % db_url )

#        resp, content = http.request( db_url, "GET" )
#        if self.debug:
#            printf( "resp:\n%s" % resp )
#            printf( "content:\n%s" % content )
#        #    printf( "content is of type: %s" % type( content ) )

#        dict_list = []
#        dict_list = eval( content )        # string to list

#        ids = []
#        items = len( dict_list )
#        if self.debug:
#            printf( "items: %d" % items )

#        # lu dict: like syn dict, but with pos: part-of-speech
#        for dict in dict_list:
#            if self.debug:
#                printf( dict )

#            seq_nr = dict[ "seq_nr" ]   # sense number
#            value  = dict[ "value" ]    # lexical unit identifier
#            form   = dict[ "form" ]     # lemma
#            pos    = dict[ "pos" ]      # part of speech
#            label  = dict[ "label" ]    # label to be shown

#            if self.debug:
#                printf( "seq_nr: %s" % seq_nr )
#                printf( "value:  %s" % value )
#                printf( "form:   %s" % form )
#                printf( "pos:    %s" % pos )
#                printf( "label:  %s" % label )

#            if value != "":
#                ids.append( value )

#        return ids



#    def lemma2formcats( utf8_lemma ):
#        """\
#        get the form-cats for this lemma.
#        """
#        self.debug = False

#        http, resp, content = remote_open( self.debug )

#        if resp is None:
#            template = "cornettodb/error.html"
#            dictionary = { 'DSC_HOME' : settings.DSC_HOME }
#            return template, dictionary


#        status = int( resp.get( "status" ) )
#        if status != 200:
#            # e.g. 400: Bad Request, 404: Not Found
#            printf( "status: %d\nreason: %s" % ( resp.status, resp.reason ) )
#            template = "cornettodb/error.html"
#            message = "Cornetto " + _( "initialization" )
#            dict = \
#            { 
#                'DSC_HOME':    settings.DSC_HOME,
#                'message':    message,
#                'status':    resp.status,
#                'reason':    resp.reason, \
#            }
#            return template, dictionary


#        # get the lexical unit identifiers for this lemma
#        lu_ids = query_remote_lu_lemma( self.debug, http, utf8_lemma )

#        scheme   = settings.CORNETTO_PROTOCOL
#        netloc   = settings.CORNETTO_HOST + ':' +  str( settings.CORNETTO_PORT )
#        params   = ""
#        fragment = ""

#        path = "cdb_lu"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_id_formcat: db_opt: %s" % path )

#        output_opt = "plain"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_id_formcat: output_opt: %s" % output_opt )

#        action = "runQuery"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_id_formcat: action: %s" % action )

#        formcats = []
#        for lu_id in lu_ids:
#            if self.debug:
#                printf( "cornettodb/views/query_remote_lu_id_formcat: query: %s" % lu_id )

#            qdict = {}
#            qdict[ "action" ]  = action
#            qdict[ "query" ]   = lu_id
#            qdict[ "outtype" ] = output_opt

#            query = urllib.urlencode( qdict )

#            db_url_tuple = ( scheme, netloc, path, params, query, fragment )
#            db_url = urlparse.urlunparse( db_url_tuple )
#            if self.debug:
#                printf( "db_url: %s" % db_url )

#            resp, content = http.request( db_url, "GET" )
#            if self.debug:
#                printf( "resp:\n%s" % resp )

#            xml_data = eval( content )
#            root = etree.fromstring( xml_data )

#            # morpho
#            morpho = ""
#            elem_form = root.find( ".//form" )
#            if elem_form is not None:
#                formcat = elem_form.get( "form-cat" )        # get "form-cat" attribute
#                if formcat is None:
#                    formcat = '?'

#                count = formcats.count( formcat )
#                if count == 0:
#                    formcats.append( formcat )

#        return formcats



#    def query_remote_lu_id(lu_id ):
#        """\
#        call cdb_lu with lexical unit identifier -> yields the lexical unit xml;
#        from the xml collect the morpho-syntax, resumes+definitions, examples.
#        """
#        scheme   = settings.CORNETTO_PROTOCOL
#        netloc   = settings.CORNETTO_HOST + ':' +  str( settings.CORNETTO_PORT )
#        params   = ""
#        fragment = ""

#        path = "cdb_lu"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_id: db_opt: %s" % path )

#        # output_opt: plain, html, xml
#        # 'xml' is actually xhtml (with markup), but it is not valid xml!
#        # 'plain' is actually valid xml (without markup)
#        output_opt = "plain"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_id: output_opt: %s" % output_opt )

#        action = "runQuery"
#        if self.debug:
#            printf( "cornettodb/views/query_remote_lu_id: action: %s" % action )
#            printf( "cornettodb/views/query_remote_lu_id: query: %s" % lu_id )
#    
#        qdict = {}
#        qdict[ "action" ]  = action
#        qdict[ "query" ]   = lu_id
#        qdict[ "outtype" ] = output_opt

#        query = urllib.urlencode( qdict )

#        db_url_tuple = ( scheme, netloc, path, params, query, fragment )
#        db_url = urlparse.urlunparse( db_url_tuple )
#        if self.debug:
#            printf( "db_url: %s" % db_url )

#        resp, content = http.request( db_url, "GET" )
#        if self.debug:
#            printf( "resp:\n%s" % resp )
#        #    printf( "content:\n%s" % content )
#        #    printf( "content is of type: %s" % type( content ) )        #<type 'str'>

#        xml_data = eval( content )
#        root = etree.fromstring( xml_data )

#        # morpho
#        morpho = ""
#        elem_form = root.find( ".//form" )
#        if elem_form is not None:
#            formcat = elem_form.get( "form-cat" )        # get "form-cat" attribute
#            if formcat is not None:
#                if formcat == "adj":
#                    morpho = 'a'

#                elif formcat == "noun":
#                    morpho = 'n'

#                    elem_article = root.find( ".//sy-article" )
#                    if elem_article is not None and elem_article.text is not None:
#                        article = elem_article.text        # lidwoord
#                        morpho += "-" + article

#                    elem_count = root.find( ".//sem-countability" )
#                    if elem_count is not None and elem_count.text is not None:
#                        countability = elem_count.text
#                        if countability == "count":
#                            morpho += "-t"
#                        elif countability == "uncount":
#                            morpho += "-nt"

#                elif formcat == "verb":
#                    morpho = 'v'

#                    elem_trans = root.find( ".//sy-trans" )
#                    if elem_trans is not None and elem_trans.text is not None:
#                        transitivity = elem_trans.text
#                        if transitivity == "tran":
#                            morpho += "-tr"
#                        elif transitivity == "intr":
#                            morpho += "-intr"
#                        else:        # should not occur
#                            morpho += "-"
#                            morpho += transitivity

#                    elem_separ = root.find( ".//sy-separ" )
#                    if elem_separ is not None and elem_separ.text is not None:
#                        separability = elem_separ.text
#                        if separability == "sch":
#                            morpho += "-sch"
#                        elif separability == "onsch":
#                            morpho += "-onsch"
#                        else:        # should not occur
#                            morpho += "-"
#                            morpho += separability

#                    elem_reflexiv = root.find( ".//sy-reflexiv" )
#                    if elem_reflexiv is not None and elem_reflexiv.text is not None:
#                        reflexivity = elem_reflexiv.text
#                        if reflexivity == "refl":
#                            morpho += "-refl"
#                        elif reflexivity == "nrefl":
#                            morpho += "-nrefl"
#                        else:        # should not occur
#                            morpho += "-"
#                            morpho += reflexivity

#                elif formcat == "adverb":
#                    morpho = 'd'

#                else:
#                    morpho = '?'

#        # find <sem-resume> anywhere in the tree
#        elem_resume = root.find( ".//sem-resume" )
#        if elem_resume is not None:
#            resume = elem_resume.text
#        else:
#            resume = ""

#        examples_text = []
#        examples_type = []
#        examples_subtype = []

#        # find <form_example> anywhere in the tree
#        examples = root.findall( ".//example" )
#        for example in examples:
#            example_id = example.get( "r_ex_id" )

#            elem_type = example.find( "syntax_example/sy-type" )
#            if elem_type is not None:
#                type_text = elem_type.text
#                if type_text is None:
#                    type_text = ""
#            else:
#                type_text = ""

#            elem_subtype = example.find( "syntax_example/sy-subtype" )
#            if elem_subtype is not None:
#                subtype_text = elem_subtype.text
#                if subtype_text is None:
#                    subtype_text = ""
#            else:
#                subtype_text = ""

#            # there can be a canonical and/or textual example, 
#            # they share the type and subtype
#            elem_canonical = example.find( "form_example/canonicalform" )    # find <canonicalform> child
#            if elem_canonical is not None and elem_canonical.text is not None:
#                example_text = elem_canonical.text
#                example_out = example_text.encode( "iso-8859-1", "replace" )

#                if self.debug:
#                    printf( "subtype, r_ex_id: %s: %s" % ( example_id, example_out ) )
#                if subtype_text != "idiom":
#                    examples_text.append( example_text )
#                    examples_type.append( type_text )
#                    examples_subtype.append( subtype_text )
#                else:
#                    if self.debug:
#                        printf( "filter idiom: %s" % example_out)
#    
#            elem_textual = example.find( "form_example/textualform" )        # find <textualform> child
#            if elem_textual is not None and elem_textual.text is not None:
#                example_text = elem_textual.text
#                example_out = example_text.encode( "iso-8859-1", "replace" )

#                if self.debug:
#                    printf( "subtype r_ex_id: %s: %s" % ( example_id, example_out ) )
#                if subtype_text != "idiom":
#                    examples_text.append( example_text )
#                    examples_type.append( type_text )
#                    examples_subtype.append( subtype_text )
#                else:
#                    if self.debug:
#                        printf( "filter idiom: %s" % example_out)

#        return formcat, morpho, resume, examples_text, examples_type, examples_subtype


        

#    def get_synset(self, syn_id, utf8_lemma, domains_abbrev ):
#        """Parse synset data"""
#        root = self.get_synset_xml(syn_id)

#        synonyms = []
#        # find <synonyms> anywhere in the tree
#        elem_synonyms = root.find( ".//synonyms" )
#        for elem_synonym in elem_synonyms:
#            synonym_str = elem_synonym.get( "c_lu_id-previewtext" )        # get "c_lu_id-previewtext" attribute
#            # synonym_str ends with ":<num>"
#            synonym = synonym_str.split( ':' )[ 0 ].strip()

#            utf8_synonym = synonym.encode( 'utf-8' )
#            if utf8_synonym != utf8_lemma:
#                synonyms.append( synonym )
#                if self.debug:
#                    printf( "synonym add: %s" % synonym )
#            else:
#                lu_id = elem_synonym.get( "c_lu_id" )        # get "c_lu_id" attribute
#                if self.debug:
#                    printf( "lu_id: %s" % lu_id )
#                    printf( "synonym skip lemma: %s" % synonym )

#        definition = ""
#        elem_definition = root.find( ".//definition" )
#        if elem_definition is not None and elem_definition.text is not None:
#            definition = elem_definition.text

#        differentiae = ""
#        elem_differentiae = root.find( "./differentiae/" )
#        if elem_differentiae is not None and elem_differentiae.text is not None:
#            differentiae = elem_differentiae.text

#        if self.debug:
#            print( "definition: %s" % definition.encode( 'utf-8' ) )
#            print( "differentiae: %s" % differentiae.encode( 'utf-8' ) )

#        hyperonyms = []
#        hyponyms = []
#        relations_all = []
#        relnames_all = []
#        # find internal <wn_internal_relations> anywhere in the tree
#        elem_intrelations = root.find( ".//wn_internal_relations" )
#        for elem_relation in elem_intrelations:
#            relations = []
#            relation_str = elem_relation.get( "target-previewtext" )    # get "target-previewtext" attribute
#            name = elem_relation.get( "relation_name" )
#            target = elem_relation.get( "targer" )
#            relation_list = relation_str.split( ',' )
#            for relation_str in relation_list:
#                relation = relation_str.split( ':' )[ 0 ].strip()
#                relations.append( relation )

#                relations_all.append( relation )
#                relnames_all.append( name )

#            if name == "HAS_HYPERONYM":
#                if self.debug:
#                    printf( "target: %s" % target )
#                hyperonyms.append( relations )
#            elif name == "HAS_HYPONYM":
#                if self.debug:
#                    printf( "target: %s" % target )
#                hyponyms.append( relations )

#        # we could keep the relation sub-lists separate on the basis of their "target" attribute
#        # but for now we flatten the lists
#        hyperonyms = flatten( hyperonyms )
#        hyponyms   = flatten( hyponyms )
#        if self.debug:
#            printf( "hyperonyms: %s" % hyperonyms )
#            printf( "hyponyms: %s" % hyponyms )

#        domains = []
#        # find <wn_domains> anywhere in the tree
#        wn_domains = root.find( ".//wn_domains" )
#        for dom_relation in wn_domains:
#            domains_en = dom_relation.get( "term" )                        # get "term" attribute
#            if self.debug:
#                if domains_en:
#                    printf( "domain: %s" % domains_en )
#        
#            # use dutch domain name[s], abbreviated
#            domain_list = domains_en.split( ' ' )
#            for domain_en in domain_list:
#                try:
#                    domain_nl = domains_abbrev[ domain_en ]
#                    if domain_nl.endswith( '.' ):        # remove trailing '.'
#                        domain_nl = domain_nl[ : -1]    # remove last character
#                except:
#                    printf( "failed to convert domain: %s" % domain_en )
#                    domain_nl = domain_en

#                if domains.count( domain_nl ) == 0:        # append if new
#                    domains.append( domain_nl )

#        return lu_id, definition, differentiae, synonyms, hyperonyms, hyponyms, relations_all, relnames_all, domains



