# -*- coding: utf-8 -*-
#!/usr/bin/python2.6
# webservertest.py


from bottle import route, post, run,  debug,  response,  request, CheetahTemplate as template
from bottle import TEMPLATE_PATH as TEMPLATE_PATH,  send_file,  PasteServer


@route('/index')
def index():
    response.content_type = 'text/html; charset=utf8'
    return 'tested'

def main():


    run(reloader=False,  host='0.0.0.0',  server=PasteServer,  port=80)  
        
    
    
    
if __name__ == "__main__":
    main()