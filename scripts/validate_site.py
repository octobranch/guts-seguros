#!/usr/bin/env python3
"""Static quality checks for GUTS Pages, using only the Python standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.tags=[];self.ids=[];self.stack=[];self.title=[];self.h1=[];self.main=[];self.schema=[];self.questions=[];self.answers=[];self.capture=None;self.capture_depth=0;self.capture_buffer=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);self.tags.append((tag,attrs))
        if 'id'in attrs:self.ids.append(attrs['id'])
        if tag not in VOID:self.stack.append(tag)
        if tag=='summary' or (tag=='p' and 'faq-answer'in attrs.get('class','').split()) or (tag=='script' and attrs.get('type')=='application/ld+json'):
            self.capture=tag if tag!='p' else 'answer';self.capture_depth=len(self.stack);self.capture_buffer=[]
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
    def handle_data(self,data):
        if 'title'in self.stack:self.title.append(data)
        if 'h1'in self.stack:self.h1.append(data)
        if 'main'in self.stack and 'script' not in self.stack:self.main.append(data)
        if self.capture:self.capture_buffer.append(data)
    def handle_endtag(self,tag):
        if self.capture and self.capture_depth==len(self.stack):
            data=''.join(self.capture_buffer).strip()
            if self.capture=='summary':self.questions.append(data)
            elif self.capture=='answer':self.answers.append(data)
            elif self.capture=='script':self.schema.append(json.loads(data))
            self.capture=None
        if tag in self.stack:
            i=len(self.stack)-1-self.stack[::-1].index(tag);self.stack=self.stack[:i]
    def meta(self,key):return next((a.get('content','') for t,a in self.tags if t=='meta' and (a.get('name')==key or a.get('property')==key)),'')
    def links(self,rel):return [a for t,a in self.tags if t=='link' and a.get('rel')==rel]

def validate(folder):
    folder=Path(folder).resolve();manifest=json.loads((ROOT/'scripts/site-manifest.json').read_text());issues=[];pages={}
    deploy=folder/'deployment-info.json'
    base=json.loads(deploy.read_text())['site_url'] if deploy.exists() else 'https://www.guts.mx/'
    indexable=json.loads(deploy.read_text()).get('indexable',True) if deploy.exists() else True
    def require(condition,message):
        if not condition:issues.append(message)
    for entry in manifest:
        file=folder/entry['path'];require(file.is_file(),'Missing '+entry['path'])
        if not file.exists():continue
        text=file.read_text();page=Page(text);pages[entry['path']]=page
        title=''.join(page.title).strip();h1=''.join(page.h1).strip();description=page.meta('description');primary=entry['primary'].casefold()
        prefix=entry['path']+': '
        require(sum(t=='h1' for t,a in page.tags)==1,prefix+'one H1 required')
        require(len(page.ids)==len(set(page.ids)),prefix+'duplicate IDs')
        require(primary in title.casefold(),prefix+'primary keyword missing from title')
        require(primary in description.casefold(),prefix+'primary keyword missing from description')
        require(primary in h1.casefold(),prefix+'primary keyword missing from H1')
        require(80<=len(description)<=210,prefix+'description outside review range')
        require(sum(t=='table' for t,a in page.tags)>=2,prefix+'two useful comparison tables required')
        require(any(t=='ol' for t,a in page.tags),prefix+'step list required')
        require(len(' '.join(page.main).split())>=500,prefix+'service/home content too thin')
        canon=page.links('canonical');require(len(canon)==1 and canon[0]['href']==base+entry['canonical_path'],prefix+'canonical mismatch')
        alternates={a.get('hreflang'):a.get('href') for a in page.links('alternate')}
        pair=[e for e in manifest if e['pair']==entry['pair']]
        expected={('es-MX' if e['language']=='es' else 'en'):base+e['canonical_path'] for e in pair};expected['x-default']=expected['es-MX']
        require(alternates==expected,prefix+'hreflang pair mismatch')
        require(page.meta('og:url')==base+entry['canonical_path'],prefix+'OG URL mismatch')
        require(page.meta('og:title')==title,prefix+'OG title mismatch')
        require(('noindex' not in page.meta('robots'))==indexable,prefix+'robots visibility mismatch')
        require(len(page.schema)==1,prefix+'one schema graph required')
        if page.schema:
            graph=page.schema[0]['@graph'];faq=next((n for n in graph if n.get('@type')=='FAQPage'),None)
            require(faq is not None,prefix+'FAQ schema missing')
            if faq:
                require([q['name'] for q in faq['mainEntity']]==page.questions,prefix+'FAQ questions do not match visible text')
                require([q['acceptedAnswer']['text'] for q in faq['mainEntity']]==page.answers,prefix+'FAQ answers do not match visible text')
            node_ids={n['@id'] for n in graph if '@id'in n}
            def walk(value):
                if isinstance(value,dict):
                    if set(value)=={'@id'}:require(value['@id']in node_ids,prefix+'unresolved graph node '+value['@id'])
                    for v in value.values():walk(v)
                elif isinstance(value,list):
                    for v in value:walk(v)
            walk(graph)
        require(len(page.links('stylesheet'))==1,prefix+'one shared stylesheet required')
        require(any(t=='script' and a.get('src','').endswith('assets/js/main.js') and 'defer'in a for t,a in page.tags),prefix+'deferred shared JS missing')
        require(not re.search(r'aggregateRating|hasCredential|529981234567|hola@guts.mx|@@[A-Z]+@@',text),prefix+'unverified claim or unresolved placeholder')
        for tag,attrs in page.tags:
            if tag=='img':require(bool(attrs.get('alt')) and attrs.get('width') and attrs.get('height'),prefix+'image missing alt/dimensions')
            if tag=='th':require(attrs.get('scope')in ('row','col'),prefix+'table heading needs scope')
            if tag=='a' and attrs.get('target')=='_blank':require('noopener'in attrs.get('rel',''),prefix+'unprotected external new-tab link')
            if tag=='a' and attrs.get('id')=='whatsapp-float':require(attrs.get('href','').startswith('https://wa.me/522411123580?text='),prefix+'WhatsApp destination changed')
    # Check local resources and every fragment against the actual target page.
    for entry in manifest:
        if entry['path']not in pages:continue
        page=pages[entry['path']];file=folder/entry['path']
        for tag,attrs in page.tags:
            attr='src' if tag in ('img','script') else 'href' if tag in ('a','use') or (tag=='link' and attrs.get('rel')in ('stylesheet','icon')) else None
            if not attr or not attrs.get(attr):continue
            url=attrs[attr];parsed=urlsplit(url)
            if parsed.scheme or parsed.netloc:continue
            require(not url.startswith('/'),entry['path']+': root-relative link breaks project Pages '+url)
            target=(file.parent/unquote(parsed.path)).resolve() if parsed.path else file
            if target.is_dir():target=target/'index.html'
            require(target.is_relative_to(folder) and target.exists(),entry['path']+': missing local target '+url)
            if parsed.fragment and target.suffix=='.html' and target.exists():
                key=target.relative_to(folder).as_posix();other=pages.get(key) or Page(target.read_text())
                require(unquote(parsed.fragment)in other.ids,entry['path']+': broken fragment '+url)
    titles=[''.join(p.title).strip() for p in pages.values()];require(len(set(titles))==len(titles),'Duplicate page titles')
    if (folder/'sitemap.xml').exists():
        sitemap=ET.parse(folder/'sitemap.xml');urls={n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        require(urls==({base+e['canonical_path'] for e in manifest} if indexable else set()),'Sitemap does not match indexable pages')
    else:require(False,'sitemap.xml missing')
    require((folder/'robots.txt').exists(),'robots.txt missing')
    require((folder/'404.html').exists(),'404.html missing')
    if (folder/'404.html').exists():require('noindex'in Page((folder/'404.html').read_text()).meta('robots'),'404 must be noindex')
    if issues:
        for issue in issues:print('FAIL '+issue)
        raise SystemExit(f'{len(issues)} checks failed.')
    print(json.dumps({'status':'passed','pages':len(pages),'base_url':base,'checks':['primary keywords','unique metadata','2 tables/page','guides and steps','local resources','all internal anchors','ES/EN alternates','schema references','FAQ text parity','sitemap','404','WhatsApp']},ensure_ascii=False))

if __name__=='__main__':validate(sys.argv[1] if len(sys.argv)>1 else ROOT)
