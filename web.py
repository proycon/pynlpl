from pattern.web import Google, plaintext

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
        
    if not engine:
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
            concindex = None            
            for i in range(1,len(content)):
                if content[i] == '.' or content[i] == '?' or content[i] == '!' or content[i] == '\n':
                    if wordindex >= begin and ((concfilter and concindex >= begin) or (not concfilter)):
                        if len(content[begin:wordindex].strip()) > 5 or len(content[wordindex+len(word):i+1].strip()) > 5:
                            yield (content[begin:wordindex].strip(), content[wordindex:wordindex+len(word)].strip(), content[wordindex+len(word):i+1], result.url)
                    wordindex = concindex = None
                    begin = i + 1
                if content[i:i+len(word)].lower() == word.lower():
                    wordindex = i
                if concfilter and content[i:len(concfilter)].lower() == concfilter.lower():
                    concindex = i
