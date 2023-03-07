#!/usr/bin/python3
import panflute as pf

def action(elem, doc):
    if isinstance(elem, pf.Link):
        if elem.url.endswith('.md'):
            elem.url = elem.url[:-3] + '.html'
        elif elem.url.find('.md#'):
            elem.url = elem.url.replace('.md#', '.html#')
    return elem

if __name__ == '__main__':
    pf.run_filter(action)

