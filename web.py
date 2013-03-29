import sys
if sys.version == '3':
    raise ImportError("Pattern does not yet support Python 3")
from pattern.web import Google, Bing, plaintext


def bingcorpsearch(word,concfilter = '', extraquery='',license=None, start=1, count=50):
    """Searches the web for sentences containing a certain keyword, and possibly a co-occurence word. Generator yielding (leftcontext,word,rightcontext,url) tuples.
       First queries Google, and then retrieves the pages of the top search results.
       Uses 'pattern' (CLiPS, Antwerpen University)
       """
    if not concfilter:
        query = word
    else:
        query = word + ' ' + concfilter
    if extraquery:
       query += ' ' + extraquery

    engine = Bing(license=license)
        
    processed = {}
    
    for result in engine.search(query, start=start,count=count):
        if not result.url in processed:
            processed[result.url] = True
            try:
                content = plaintext(result.download())
            except:
                continue
                
            begin = 0
            wordindex = None
            wordlength = 0
            concindex = None            
            for i in range(1,len(content)):
                if content[i] == '.' or content[i] == '?' or content[i] == '!' or content[i] == '\n':
                    if wordindex >= begin and ((concfilter and concindex >= begin) or (not concfilter)):
                        if len(content[begin:wordindex].strip()) > 5 or len(content[wordindex+wordlength:i+1].strip()) > 5:
                            yield (content[begin:wordindex].strip(), content[wordindex:wordindex+wordlength].strip(), content[wordindex+wordlength:i+1], result.url)
                    wordindex = concindex = None
                    begin = i + 1
                if len(word)+i <= len(content) and content[i:i+len(word)].lower() == word.lower():
                    wordindex = i
                    wordlength = len(word)
                    for j in range(len(word),len(content)):                        
                        if i+j < len(content) and (content[i+j] == ' ' or  content[i+j] == '?' or content[i+j] == '!' or content[i+j] == '\n'):
                            wordlength = j
                            break                                                                
                if concfilter and content[i:len(concfilter)].lower() == concfilter.lower():
                    concindex = i


def googlecorpsearch(word,concfilter = '', extraquery='',license=None, start=1, count=8):
    """Searches the web for sentences containing a certain keyword, and possibly a co-occurence word. Generator yielding (leftcontext,word,rightcontext,url) tuples.
       First queries Google, and then retrieves the pages of the top search results.
       Uses 'pattern' (CLiPS, Antwerpen University)
       """
    if not concfilter:
        query = 'allintext: ' + word 
    else:
        query = 'allintext: "' + word + ' * ' + concfilter + '" OR "' + concfilter + ' * ' + word + '"'
    if extraquery:
        query += ' ' + extraquery
        

    engine = Google(license=license)
        
    processed = {}
    
    for result in engine.search(query, start=start,count=count):
        if not result.url in processed:
            processed[result.url] = True
            try:
                content = plaintext(result.download())
            except:
                continue
                
            begin = 0
            wordindex = None
            wordlength = 0
            concindex = None            
            for i in range(1,len(content)):
                if content[i] == '.' or content[i] == '?' or content[i] == '!' or content[i] == '\n':
                    if wordindex >= begin and ((concfilter and concindex >= begin) or (not concfilter)):
                        if len(content[begin:wordindex].strip()) > 5 or len(content[wordindex+wordlength:i+1].strip()) > 5:
                            yield (content[begin:wordindex].strip(), content[wordindex:wordindex+wordlength].strip(), content[wordindex+wordlength:i+1], result.url)
                    wordindex = concindex = None
                    begin = i + 1
                if len(word)+i <= len(content) and content[i:i+len(word)].lower() == word.lower():
                    wordindex = i
                    wordlength = len(word)
                    for j in range(len(word),len(content)):                        
                        if i+j < len(content) and (content[i+j] == ' ' or  content[i+j] == '?' or content[i+j] == '!' or content[i+j] == '\n'):
                            wordlength = j
                            break                                                                
                if concfilter and content[i:len(concfilter)].lower() == concfilter.lower():
                    concindex = i
