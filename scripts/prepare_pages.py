#!/usr/bin/env python3
"""Prepare a static Pages artifact. Python standard library only; no web backend."""
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import argparse,json,os,re,shutil

ROOT=Path(__file__).resolve().parents[1]
SOURCE_BASE='https://www.guts.mx/'

def normalise_base(value):
    value=value.strip().rstrip('/')+'/'
    parsed=urlsplit(value)
    if parsed.scheme not in ('https','http') or not parsed.netloc or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Use an absolute http(s) site URL without query, fragment or credentials.')
    if any(part in ('.','..') for part in parsed.path.split('/')):
        raise ValueError('The base URL cannot contain dot path segments.')
    return value

def rewrite_json(value,base):
    if isinstance(value,str):return base+value[len(SOURCE_BASE):] if value.startswith(SOURCE_BASE) else value
    if isinstance(value,list):return [rewrite_json(v,base) for v in value]
    if isinstance(value,dict):return {k:rewrite_json(v,base) for k,v in value.items()}
    return value

def prepare(base,output):
    config=json.loads((ROOT/'site.config.json').read_text())
    base=normalise_base(config.get('site_url') or base)
    indexable=config.get('indexable',True)
    output=Path(output).resolve()
    if output==ROOT or ROOT.is_relative_to(output):raise ValueError('Output must be a separate directory, not the source root or its parent.')
    if output.exists() and any(output.iterdir()):raise ValueError('Choose an empty output directory to avoid stale published files.')
    output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'scripts/site-manifest.json').read_text())
    for entry in manifest+[{'path':'404.html'}]:
        relative=entry['path'];source=ROOT/relative;text=source.read_text(encoding='utf-8')
        # Rewrite only metadata/schema URLs. External contact and privacy links stay unchanged.
        head_match=re.search(r'<head>.*?</head>',text,re.S)
        head=head_match.group().replace(SOURCE_BASE,base)
        if relative!='404.html' and not indexable:
            head=re.sub(r'(<meta\s+name="robots"\s+content=")[^"]*(")',r'\g<1>noindex,follow\2',head)
        text=text[:head_match.start()]+head+text[head_match.end():]
        pattern=r'(<script\s+type="application/ld\+json"[^>]*>)(.*?)(</script>)'
        def replace_schema(match):
            value=rewrite_json(json.loads(match.group(2)),base)
            return match.group(1)+json.dumps(value,ensure_ascii=False,separators=(',',':'))+match.group(3)
        text=re.sub(pattern,replace_schema,text,flags=re.S)
        if relative=='404.html':text=text.replace('href="https://www.guts.mx/"',f'href="{base}"')
        dest=output/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
    shutil.copytree(ROOT/'assets',output/'assets',dirs_exist_ok=True)
    (output/'.nojekyll').write_text('')
    if (ROOT/'CNAME').exists():shutil.copy2(ROOT/'CNAME',output/'CNAME')
    sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    if indexable:
        for entry in manifest:
            node=ET.SubElement(sitemap,'url');ET.SubElement(node,'loc').text=base+entry['canonical_path']
    ET.ElementTree(sitemap).write(output/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (output/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+base+'sitemap.xml\n')
    (output/'deployment-info.json').write_text(json.dumps({'site_url':base,'indexable':indexable,'pages':len(manifest)},indent=2)+'\n')
    print(json.dumps({'site_url':base,'indexable':indexable,'pages':len(manifest),'output':str(output)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default=os.environ.get('PAGES_URL',SOURCE_BASE))
    parser.add_argument('--output',default=str(ROOT/'_site'))
    args=parser.parse_args();prepare(args.base_url,args.output)
