#!/usr/bin/python3

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag 

conn = sqlite3.connect('/tmp/tidb/target/TiDB.docset/Contents/Resources/docSet.dsidx')
cur = conn.cursor()
try: 
    cur.execute('DROP TABLE searchIndex;')
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT, lang TEXT DEFAULT "zh");')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path, lang);')
except: 
    pass


docpath = '/tmp/tidb/target/TiDB.docset/Contents/Resources/Documents'
page = open(os.path.join(docpath,'TOC.html')).read()
soup = BeautifulSoup(page)
any = re.compile('.*')

for tag in soup.find_all('a', {'href':any}):
    name = tag.text.strip()
    if len(name) > 1:
        path = tag.attrs['href'].strip()            
        try:
            ## system variables
            ## ./system-variables.html
            if 'system-variables.html' in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtaga in subsoup.find_all('nav', id='TOC'):
                    for subtag in subtaga.find_all('a', {'href':any}):
                        subpath = subtag.attrs['href'].strip()
                        if subpath.startswith("#") and len(subtag.find_all('code')) > 0:
                            element = subtag.code.string
                            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'variables', path + subtag['href']))

            ## command-line-flags
            ## ./command-line-flags-for-{pd,tikv,tidb}-configuration.html
            elif 'command-line-flags-for-' in path and 'configuration.html' in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtaga in subsoup.find_all('nav', id='TOC'):
                    for subtag in subtaga.find_all('a', {'href':any}):
                        subpath = subtag.attrs['href'].strip()
                        if subpath.startswith("#") and len(subtag.find_all('code')) > 0:
                            element = subtag.code.string
                            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'variables', path + subtag['href']))        
        
            ## configuration
            ## ./{pd,tikv,tidb}-configuration-file.html
            ## garbage-collection-configuration.html
            elif path.endswith('-configuration-file.html') or 'garbage-collection-configuration.html' in path \
                or (('dm/' in path or 'tidb-binlog' in path or 'tidb-lightning' in path) and 'configuration' in path) \
                or (('storage-engine' in path or 'tiflash' in path) and 'configuration' in path) :
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtaga in subsoup.find_all('nav', id='TOC'):
                    for subtag in subtaga.find_all('a', {'href':any}):
                        subpath = subtag.attrs['href'].strip()
                        if subpath.startswith("#") and len(subtag.find_all('code')) > 0:
                            element = subtag.code.string
                            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'variables', path + subtag['href']))           

            ## configuration
            elif (('dm/' in path or 'tidb-binlog' in path or 'tidb-lightning' in path) and 'configuration' in path) \
                or (('storage-engine' in path or 'tiflash' in path) and 'configuration' in path) :
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'variables', path))     

            ## functions
            ## ./functions-and-operators/*.html
            elif 'functions-and-operators' in path and 'operators.html' not in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.find_all('a', {'href':any}):
                    subpath = subtag.attrs['href'].strip()
                    if len(subtag.find_all('code')) > 0:
                        element = subtag.code.string
                        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Function', path))

            ## functions
            ## ./information-schema/*.html
            elif 'information-schema/' in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Function', path))    

            ## operators
            ## ./functions-and-operators/operators.html
            elif 'operators.html' in path:
                cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', ('Operator', 'Operator', path))
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.find_all('a', {'href':any}):
                    subpath = subtag.attrs['href'].strip()
                    if len(subtag.find_all('code')) > 0:
                        element = subtag.code.string
                        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Operator', path))        

            ## statements
            ## ./sql-statements/*.html
            elif 'sql-statements' in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Statement', path))
            
            ## Test
            ## not ./benchmark 
            elif 'benchmark/' not in path and ('bench' in path or 'test' in path):
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Test', path))   

            ## Guide
            ## ./develop/*.html
            ## ./best-practices/*.html
            ## ./faq/*.html
            elif 'develop/' in path or 'best-practices/' in path or 'faq/' in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Guide', path))         

            ## ./sync-diff-inspector   
            ## ./tiflash         
            ## ./storage-engine   
            ## ./ticdc  
            ## ./tidb-binlog     
            ## ./tiunimanager   
            ## ./br
            ## ./tidb-lightning
            ## ./clinic
            elif 'sync-diff-inspector' in path \
                or ('tiflash/' in path or 'storage-engine/' in path or 'ticdc/' in path \
                or 'tidb-binlog/' in path or 'tiunimanager/' in path or 'br/' in path \
                or 'tidb-lightning/' in path or 'clinic/' in path) and 'configuration' not in path:
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Guide', path))   

            ## Command
            ## ./tiup
            elif 'tiup/' in path:   
                if 'tiup-component' in path or 'tiup-command' in path or 'tiup-refer' in path:
                    type = 'Command'
                else:
                    type = 'Guide'
                subpage = open(os.path.join(docpath,path)).read()
                subsoup = BeautifulSoup(subpage)
                for subtag in subsoup.head.find_all('title'):
                    element = subtag.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, type, path))        

        except FileNotFoundError as e:
            print('%s: %s', e.strerror, path)

benchpath = docpath + '/benchmark' 
for root, dirs, paths in os.walk(benchpath):
    for path in paths:
        subpage = open(os.path.join(benchpath, path)).read()
        subsoup = BeautifulSoup(subpage)
        for subtag in subsoup.head.find_all('title'):
            element = subtag.string
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, 'Test',  './benchmark/' + path)) 

for path in os.listdir(docpath):
    if 'grafana' in path or 'troubleshoot' in path or 'tune-' in path or 'tuning-' in path or 'data-type' in path or 'tidb-limitations' in path \
            or 'user-defined-variables' in path or 'explain-' in path or 'transaction-' in path or 'migrate-' in path:
            
        if 'grafana' in path and 'dashboard' in path or 'user-defined-variables' in path:
            type = 'variables'
        elif 'troubleshoot' in path or 'tune-' in path or 'tuning-' in path or 'migrate-' in path:
            type = 'Guide'
        elif 'data-type' in path or 'tidb-limitations' in path or 'explain-' in path or 'transaction-' in path:
            type = 'Section'
        subpage = open(os.path.join(docpath, path)).read()
        subsoup = BeautifulSoup(subpage)
        for subtag in subsoup.head.find_all('title'):
            element = subtag.string
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (element, type, path)) 

conn.commit()
conn.close()
