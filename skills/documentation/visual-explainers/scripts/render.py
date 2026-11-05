#!/usr/bin/env python3
"""Build one independent HTML file. Python 3.8+, standard library only."""
import argparse
import base64
import html
import json
import math
import mimetypes
from pathlib import Path
import re
import sys
from urllib.parse import unquote_to_bytes
from html.parser import HTMLParser
from diagram_layout import FontMetrics, label_geometry, layout_graph, rounded_path

SKILL = Path(__file__).resolve().parents[1]
ASSETS = SKILL / 'assets'
THEMES = ('violet', 'slate', 'blue', 'night')
BLOCKS = ('text','heading','list','alert','code','table','image','disclosure','columns','card','metrics','tabs','timeline','diagram','chart','equation','range','choice','html')
CHARTS = ('line','area','bar','scatter','histogram','donut','heatmap','box')
MINOR = set('a an and as at but by for from in nor of on or per the to via vs with'.split())

def esc(value): return html.escape(str(value), quote=True)
def title_case(text):
    # Preserve acronyms, identifiers, and existing internal capitalization.
    tokens = re.split(r'(`[^`]+`|\s+)', str(text))
    words = [i for i,t in enumerate(tokens) if t.strip() and not t.isspace()]
    for pos,i in enumerate(words):
        w=tokens[i]
        if w.startswith('`'): continue
        if w.lower() in MINOR and pos not in (0,len(words)-1) and not tokens[words[pos-1]].endswith((':','—')): tokens[i]=w.lower()
        else: tokens[i]=w[:1].upper()+w[1:]
    return ''.join(tokens)

def inline(value):
    """Small inline vocabulary; literal HTML stays literal. Use html blocks for markup."""
    pattern=r'(`[^`\n]+`|\*\*[^*\n]+\*\*|\*[^*\n]+\*|\[[^\]\n]+\]\([^\s)]+\))'
    result=[]
    for token in re.split(pattern,str(value)):
        if token.startswith('`') and token.endswith('`'): result.append('<code>'+esc(token[1:-1])+'</code>')
        elif token.startswith('**') and token.endswith('**'): result.append('<strong>'+esc(token[2:-2])+'</strong>')
        elif token.startswith('*') and token.endswith('*'): result.append('<em>'+esc(token[1:-1])+'</em>')
        elif re.fullmatch(r'\[[^\]]+\]\([^\s)]+\)',token):
            label,url=re.match(r'\[([^\]]+)\]\(([^\s)]+)\)',token).groups()
            if not url.startswith(('https://','http://','mailto:','#')): raise ValueError('Links must be https:, http:, mailto:, or # anchors')
            result.append('<a href="'+esc(url)+'">'+esc(label)+'</a>')
        else: result.append(esc(token))
    return ''.join(result)

class DependencyCheck(HTMLParser):
    """Inspect actual resource attributes, not optional source hyperlinks or license text."""
    def __init__(self):
        super().__init__();self.errors=[];self.ids=[];self.h1=0;self.in_style=False;self.in_script=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='style':self.in_style=True
        if tag=='script':self.in_script=a.get('type','') not in ('application/json','text/plain')
        if 'style' in a:self.check_css(a['style'])
        for key in ('fill','stroke','filter','mask','clip-path'):
            if key in a:self.check_css(a[key])
        if tag=='img' and a.get('src','').startswith('data:image/svg+xml'):
            try:
                header,payload=a['src'].split(',',1)
                raw=base64.b64decode(payload) if ';base64' in header else unquote_to_bytes(payload)
                svg_check=DependencyCheck();svg_check.feed(raw.decode('utf-8-sig'));self.errors.extend(svg_check.errors)
            except (ValueError,UnicodeError):self.errors.append('Invalid embedded SVG image')
        for key in ('src','poster','srcset','data'):
            if key in a and (key!='data' or tag=='object'):
                if not a[key].startswith(('data:','#')):self.errors.append(f'External resource: {tag} {key}={a[key]}')
        if tag=='link' and a.get('href','') and not a['href'].startswith('data:'):self.errors.append('External link resource: '+a['href'])
        if tag in ('use','image'):
            for k in ('href','xlink:href'):
                if k in a and not a[k].startswith(('#','data:')):self.errors.append('External SVG resource: '+a[k])
        if tag=='iframe':self.errors.append('iframes are not portable; use embedded HTML/SVG instead')
    def handle_endtag(self,tag):
        if tag=='style':self.in_style=False
        if tag=='script':self.in_script=False
    def check_css(self,data):
        if re.search(r'@import\b',data,re.I):self.errors.append('CSS @import is not offline')
        for m in re.finditer(r'url\(\s*[\'\"]?([^\'\"\)\s]+)',data):
            if not m[1].startswith(('data:','#')):self.errors.append('External CSS resource: '+m[1])
    def handle_data(self,data):
        if self.in_style:self.check_css(data)
        if self.in_script and re.search(r'\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\b|\bimport\s*\(|^\s*import\s',data,re.M):
            self.errors.append('Runtime network/module dependency in script; inline required data and code')
    def finish(self):
        duplicate=sorted({i for i in self.ids if self.ids.count(i)>1})
        if duplicate:self.errors.append('Duplicate IDs: '+', '.join(duplicate))
        if self.h1!=1:self.errors.append(f'Expected one H1; found {self.h1}')
        return self.errors

def check_html(text):
    c=DependencyCheck();c.feed(text);return c.finish()

class Renderer:
    def __init__(self, doc, base):
        self.doc=doc;self.base=base;self.counter=0;self.ids=set();self.used_charts=False
    def uid(self, requested=None):
        self.counter+=1;ident=requested or f've-{self.counter}'
        if not re.fullmatch('[A-Za-z][A-Za-z0-9_-]*',ident):raise ValueError('IDs must start with a letter and contain letters, digits, _ or -: '+ident)
        if ident in self.ids or ident in ('main','contents','toc-toggle','theme-toggle','theme-menu'):raise ValueError('Duplicate/reserved ID: '+ident)
        self.ids.add(ident);return ident
    def heading(self,text): return inline(title_case(text) if self.doc.get('lang','en').startswith('en') else text)
    def icon(self,name):
        file=ASSETS/'icons'/(str(name)+'.svg')
        if not re.fullmatch('[a-z0-9-]+',str(name)) or not file.exists():raise ValueError('Unknown icon: '+str(name)+'; see references/icons.md')
        text=file.read_text(encoding='utf-8');text=re.sub(r'<svg\b', '<svg class="icon" aria-hidden="true"',text,count=1)
        text=re.sub(r'<title>.*?</title>','',text,flags=re.S)
        return text
    def file(self, value): return (self.base/value).resolve()
    def data_uri(self,path):
        p=self.file(path);mime=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
        return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
    def blocks(self, blocks):
        if not isinstance(blocks,list):raise ValueError('blocks must be a list')
        return ''.join(self.block(b) for b in blocks)
    def block(self,b):
        if isinstance(b,str):return '<p>'+inline(b)+'</p>'
        if not isinstance(b,dict) or b.get('type') not in BLOCKS:raise ValueError('Unknown block type: '+str(b.get('type') if isinstance(b,dict) else b))
        t=b['type']
        if t=='text':return '<p>'+inline(b['text'])+'</p>'
        if t=='heading':
            level=b.get('level',3)
            if level not in (3,4):raise ValueError('Nested heading level must be 3 or 4; sections provide H2')
            return f'<h{level} id="{self.uid()}">'+self.heading(b['text'])+f'</h{level}>'
        if t=='list':
            tag='ol' if b.get('ordered',False) else 'ul'
            return '<'+tag+'>'+''.join('<li>'+inline(i)+'</li>' for i in b['items'])+'</'+tag+'>'
        if t=='alert':
            kind=b.get('kind','note')
            if kind not in ('note','tip','important','warning','caution'):raise ValueError('Alert kind must be note, tip, important, warning, caution')
            body=self.blocks(b['blocks']) if 'blocks' in b else '<p>'+inline(b['text'])+'</p>'
            return f'<div class="alert" data-alert="{kind}"><div class="alert-title">'+self.icon(kind)+self.heading(b.get('title',kind.title()))+'</div>'+body+'</div>'
        if t=='code':
            ident=self.uid(b.get('id'));label=b.get('language','Code')
            return '<div class="codebox"><div class="codebar"><span>'+esc(label)+'</span><button type="button" data-copy="'+ident+'">Copy</button></div><pre><code id="'+ident+'">'+esc(b['text'])+'</code></pre></div>'
        if t=='table':
            headers=b['headers'];rows=b['rows']
            if not headers or any(len(r)!=len(headers) for r in rows):raise ValueError('Table rows must match the number of headers')
            caption='<caption class="table-caption">'+inline(b['caption'])+'</caption>' if b.get('caption') else ''
            return '<div class="table-wrap"><table>'+caption+'<thead><tr>'+''.join('<th scope="col">'+inline(v)+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
        if t=='image':
            if not b.get('alt'):raise ValueError('image requires descriptive alt text')
            src=b.get('src') or self.data_uri(b['file'])
            if not src.startswith('data:image/'):raise ValueError('Images need a local file or data:image/ source; download remote images first')
            return '<figure><img class="screenshot" loading="lazy" src="'+esc(src)+'" alt="'+esc(b['alt'])+'">'+('<figcaption>'+inline(b['caption'])+'</figcaption>' if b.get('caption') else '')+'</figure>'
        if t=='disclosure':return '<details'+(' open' if b.get('open') else '')+'><summary>'+self.heading(b['title'])+'</summary><div class="disclosure-body content-stack">'+self.blocks(b['blocks'])+'</div></details>'
        if t=='columns':
            cols=b['columns']
            if not 1<=len(cols)<=3:raise ValueError('columns accepts one to three lists of blocks')
            return f'<div class="columns-container"><div class="columns" style="--columns:{len(cols)}">'+''.join('<div class="content-stack">'+self.blocks(col)+'</div>' for col in cols)+'</div></div>'
        if t=='card':return '<div class="card content-stack">'+('<h3 class="component-title">'+(self.icon(b['icon'])+' ' if b.get('icon') else '')+self.heading(b['title'])+'</h3>' if b.get('title') else '')+self.blocks(b['blocks'])+'</div>'
        if t=='metrics':return '<div class="metric-grid">'+''.join('<div class="metric-card">'+(self.icon(m['icon']) if m.get('icon') else '')+'<div class="metric">'+esc(m['value'])+'</div><div class="metric-label">'+inline(m['label'])+'</div>'+('<div class="metric-detail">'+inline(m['detail'])+'</div>' if m.get('detail') else '')+'</div>' for m in b['items'])+'</div>'
        if t=='tabs':
            ident=self.uid(b.get('id'));tabs=b['tabs']
            if not tabs:raise ValueError('tabs requires at least one tab')
            nav=[];panels=[]
            for i,tab in enumerate(tabs):
                tid=self.uid(ident+'-tab-'+str(i));pid=self.uid(ident+'-panel-'+str(i))
                nav.append(f'<button type="button" role="tab" id="{tid}" aria-controls="{pid}" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}">'+self.heading(tab['title'])+'</button>')
                panels.append(f'<div role="tabpanel" class="tab-panel content-stack" id="{pid}" aria-labelledby="{tid}" tabindex="0"'+(' hidden' if i else '')+'>'+self.blocks(tab['blocks'])+'</div>')
            return '<div class="tabs"><div class="tab-list" role="tablist" aria-label="'+esc(b.get('label','Examples'))+'">'+''.join(nav)+'</div>'+''.join(panels)+'</div>'
        if t=='timeline':return '<div class="timeline">'+''.join('<div class="timeline-item">'+('<small>'+inline(i['label'])+'</small>' if i.get('label') else '')+'<strong>'+inline(i['title'])+'</strong><p>'+inline(i['text'])+'</p></div>' for i in b['items'])+'</div>'
        if t=='equation':return '<figure class="equation"><div aria-label="'+esc(b.get('label',b['text']))+'">'+inline(b['text'])+'</div>'+('<figcaption>'+inline(b['caption'])+'</figcaption>' if b.get('caption') else '')+'</figure>'
        if t in ('range','choice'):
            ident=self.uid(b.get('id'));label='<label for="'+ident+'">'+inline(b['label'])+'</label>'
            if t=='range':
                lo,hi,value=b.get('min',0),b.get('max',100),b.get('value',b.get('min',0))
                if not lo<=value<=hi or b.get('step',1)<=0:raise ValueError('Range requires min <= value <= max and step > 0')
                control=f'<input type="range" id="{ident}" min="{lo}" max="{hi}" step="{b.get("step",1)}" value="{value}"><output for="{ident}" id="{ident}-value">{value}</output>'
            else:
                control='<select id="'+ident+'">'+''.join('<option value="'+esc(o['value'])+'"'+(' selected' if o['value']==b.get('value') else '')+'>'+esc(o['label'])+'</option>' for o in b['options'])+'</select>'
            return '<div class="control-group">'+label+control+'</div>'
        if t=='diagram':return self.diagram(b)
        if t=='chart':return self.chart(b)
        if t=='html':
            markup=self.file(b['file']).read_text(encoding='utf-8') if 'file' in b else b['html']
            # Inline local <img> resources in custom fragments too.
            def embed(m):
                url=m[2]
                if url.startswith(('data:','#')):return m[0]
                if re.match(r'\w+://',url):raise ValueError('Download remote custom image before building: '+url)
                return m[1]+self.data_uri(url)+m[3]
            return re.sub(r'(<img\b[^>]*\bsrc=[\'\"])([^\'\"]+)([\'\"])',embed,markup,flags=re.I)
        raise ValueError('Unsupported block '+t)
    def diagram(self,b):
        kind=b.get('kind','flow');title=b.get('title','');cap=b.get('caption','')
        if kind=='flow':
            pieces=[]
            has_icons=any(node.get('icon') for node in b['nodes'])
            for node in b['nodes']:
                if pieces:pieces.append('<span class="flow-connector" aria-hidden="true"><svg class="flow-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18m-6-6 6 6-6 6"/></svg></span>')
                pieces.append('<div class="node">'+(('<span class="flow-icon" aria-hidden="true">'+(self.icon(node['icon']) if node.get('icon') else '')+'</span>') if has_icons else '')+'<strong>'+inline(node['label'])+'</strong>'+('<p>'+inline(node['text'])+'</p>' if node.get('text') else '')+'</div>')
            body='<div class="flow" data-count="'+str(len(b['nodes']))+'" role="group" aria-label="'+esc(title or 'Process')+'">'+''.join(pieces)+'</div>'
        elif kind=='sequence':
            body=self.sequence_diagram(b)
        elif kind=='graph':
            body=self.graph_diagram(b)
        else:raise ValueError('Diagram kind must be flow, sequence, graph')
        return '<figure class="visual">'+('<div class="visual-label"><strong>'+self.heading(title)+'</strong></div>' if title else '')+'<div class="diagram-scroll">'+body+('</div><figcaption style="padding:0 20px 16px">'+inline(cap)+'</figcaption>' if cap else '</div>')+'</figure>'
    def diagram_metrics(self):
        if not hasattr(self,'_metrics'):
            self._metrics=FontMetrics(ASSETS/'fonts/Manrope.ttf')
        return self._metrics

    def svg_text(self,lines,x,y,size=13,cls='',anchor='middle'):
        text=f'<text class="{cls}" x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" fill="var(--ink)">'
        for i,line in enumerate(lines):
            text+=f'<tspan x="{x:.2f}" dy="{18 if i else 0}">{esc(line)}</tspan>'
        return text+'</text>'

    def diagram_marker(self,ident):
        return f'<defs><marker id="{ident}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10Z" fill="var(--accent)"/></marker></defs>'

    def graph_diagram(self,b):
        layout=layout_graph(b['nodes'],b.get('edges',[]),self.diagram_metrics())
        W,H=layout['width'],layout['height'];marker=self.uid()
        description='; '.join(next(n['label'] for n in b['nodes'] if n['id']==e['from'])+' → '+next(n['label'] for n in b['nodes'] if n['id']==e['to'])+(': '+e['label'] if e.get('label') else '') for e in b.get('edges',[]))
        body=f'<svg class="graph-svg" style="--diagram-min-width:{max(550,W*.82):.0f}px" viewBox="0 0 {W:.2f} {H:.2f}" role="img" aria-label="{esc(b.get("title","Directed Graph"))}"><desc>{esc(description)}</desc>'+self.diagram_marker(marker)
        for route in layout['edges']:
            body+=f'<path class="graph-edge" d="{rounded_path(route["points"])}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" marker-end="url(#{marker})"/>'
        for node in layout['nodes']:
            x,y,w,h=node['x'],node['y'],node['width'],node['height']
            body+=f'<g class="graph-node" data-node="{esc(node["id"])}"><rect x="{x:.2f}" y="{y:.2f}" width="{w}" height="{h}" rx="8" fill="var(--wash)" stroke="var(--line)"/>'
            body+=self.svg_text(node['lines'],x+w/2,y+h/2-(len(node['lines'])-1)*9+5,14)+'</g>'
        # Labels have their own measured lanes and are painted last.
        for route in layout['edges']:
            label=route['label']
            if label:
                x,y,w,h=label['x'],label['y'],label['width'],label['height']
                body+=f'<g class="graph-edge-label"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="5" fill="var(--paper)"/>'
                body+=self.svg_text(label['lines'],x+w/2,y+18,label['size'])+'</g>'
        return body+'</svg>'

    def sequence_diagram(self,b):
        actors=b['actors'];n=len(actors);metrics=self.diagram_metrics()
        if not 2<=n<=6:raise ValueError('Sequence diagrams support 2–6 actors')
        spacing=232;centers=[104+i*spacing for i in range(n)];W=centers[-1]+104
        actor_lines=[metrics.wrap(a,14,146) for a in actors]
        actor_h=max(48,max(len(lines) for lines in actor_lines)*18+20)
        y=20+actor_h+28;rows=[]
        for message in b['messages']:
            a,c=message['from'],message['to']
            if not isinstance(a,int) or not isinstance(c,int) or not 0<=min(a,c)<=max(a,c)<n:raise ValueError('Sequence from/to must be actor indices')
            if a==c:
                label=label_geometry(message['label'],metrics,spacing-52)
                direction=-1 if a==n-1 else 1
                label_x=centers[a]+14 if direction>0 else centers[a]-14-label['width']
                arrow_y=y+label['height']+10
                points=[(centers[a],arrow_y),(centers[a]+direction*56,arrow_y),(centers[a]+direction*56,arrow_y+26),(centers[a],arrow_y+26)]
                height=label['height']+60
            else:
                label=label_geometry(message['label'],metrics,min(abs(a-c)*spacing-36,320))
                label_x=(centers[a]+centers[c])/2-label['width']/2
                arrow_y=y+label['height']+10
                points=[(centers[a],arrow_y),(centers[c],arrow_y)]
                height=label['height']+36
            rows.append(dict(label=dict(label,x=label_x,y=y),points=points))
            y+=height
        H=y+12;marker=self.uid()
        body=f'<svg class="sequence-svg" style="--diagram-min-width:{W}px" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(b.get("title","Message Sequence"))}">'+self.diagram_marker(marker)
        body+='<desc>'+esc('; '.join(actors[m['from']]+' → '+actors[m['to']]+': '+m['label'] for m in b['messages']))+'</desc>'
        for x in centers:body+=f'<path d="M{x} {20+actor_h}V{H-8}" stroke="var(--line)" stroke-width="1.5"/>'
        for row in rows:
            body+=f'<path class="sequence-arrow" d="{rounded_path(row["points"])}" fill="none" stroke="var(--accent)" stroke-width="2" marker-end="url(#{marker})"/>'
            label=row['label'];x,y,w,h=label['x'],label['y'],label['width'],label['height']
            body+=f'<g class="sequence-label"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="4" fill="var(--paper)"/>'+self.svg_text(label['lines'],x+w/2,y+17)+'</g>'
        for x,lines in zip(centers,actor_lines):
            body+=f'<rect x="{x-80}" y="20" width="160" height="{actor_h}" rx="8" fill="var(--wash)"/>'
            body+=self.svg_text(lines,x,20+actor_h/2-(len(lines)-1)*9+5,14)
        return body+'</svg>'

    def chart(self,b):
        self.used_charts=True;kind=b['kind'];data=b['data'];ident=self.uid(b.get('id'))
        if kind not in CHARTS:raise ValueError('Chart kind must be '+', '.join(CHARTS))
        validate_chart(kind,data)
        options={k:b[k] for k in ('xLabel','yLabel','unit','xUnit','binUnit','yMax','yMin','pointPrefix','selectedIndex','valueLabel') if k in b}
        c=dict(id=ident,kind=kind,title=title_case(b['title']),data=data,xLabel='',yLabel='',unit='');c.update(options)
        return '<figure class="chart visual" id="'+ident+'" data-chart="'+esc(json.dumps(c,separators=(',',':'),allow_nan=False))+'"><div class="visual-label"><strong>'+self.heading(b['title'])+'</strong></div><div class="chart-body"><div class="chart-legend" aria-label="Legend"></div><div class="chart-canvas"></div><div class="chart-tooltip" role="tooltip" hidden></div><p class="chart-status" aria-live="polite"></p>'+('<figcaption>'+inline(b['caption'])+'</figcaption>' if b.get('caption') else '')+'<details class="chart-data"><summary>View Data</summary><div class="table-wrap"></div></details></div></figure>'
    def render(self):
        d=self.doc;theme=d.get('theme','violet')
        if theme not in THEMES:raise ValueError('theme must be '+', '.join(THEMES))
        sections=d.get('sections',[])
        body='<section class="hero"><h1>'+self.heading(d['title'])+'</h1>'+('<p class="lead">'+inline(d['lead'])+'</p>' if d.get('lead') else '')+self.blocks(d.get('intro',[]))+'</section>'
        for section in sections:
            ident=self.uid(section.get('id'));body+='<section><h2 id="'+ident+'">'+self.heading(section['title'])+'</h2><div class="content-stack">'+self.blocks(section['blocks'])+'</div></section>'
        menu=''.join('<button type="button" role="menuitemradio" data-theme-value="'+t+'" aria-checked="'+str(t==theme).lower()+'"><span class="theme-swatch theme-swatch-'+t+'" aria-hidden="true"></span><span>'+t.title()+'</span><span class="theme-check">'+self.icon('success')+'</span></button>' for t in THEMES)
        css=''
        licenses=[]
        for family,file,weight in [('Explainer Sans','Manrope.ttf','200 800'),('Explainer Mono','JetBrainsMono.ttf','100 800')]:
            uri='data:font/ttf;base64,'+base64.b64encode((ASSETS/'fonts'/file).read_bytes()).decode()
            css+=f'@font-face{{font-family:"{family}";src:url("{uri}") format("truetype");font-weight:{weight};font-style:normal;font-display:swap}}'
        for file in sorted((ASSETS/'fonts').glob('*-OFL.txt')):licenses.append(file.name+'\n'+file.read_text(encoding='utf-8'))
        css+=(ASSETS/'base.css').read_text(encoding='utf-8')
        for file in d.get('styles',[]):css+='\n'+self.file(file).read_text(encoding='utf-8')
        js=((ASSETS/'charts.js').read_text(encoding='utf-8')+'\n' if self.used_charts else '')+(ASSETS/'navigation.js').read_text(encoding='utf-8')+'\n'+(ASSETS/'core.js').read_text(encoding='utf-8')
        js+='\ndocument.querySelectorAll(\'input[type="range"]\').forEach(r=>r.addEventListener("input",()=>{const o=document.getElementById(r.id+"-value");if(o)o.value=r.value}));\n'
        for file in d.get('scripts',[]):js+='\n;(()=>{\n'+self.file(file).read_text(encoding='utf-8')+'\n})();\n'
        js=re.sub('</script',r'<\/script',js,flags=re.I)
        if re.search('</style',css,re.I):raise ValueError('Custom CSS may not contain </style')
        result='<!doctype html><html lang="'+esc(d.get('lang','en'))+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+esc(d.get('description',d.get('lead','')))+'"><title>'+esc(d['title'])+'</title><style>'+css+'</style></head><body data-theme="'+theme+'"><a class="skip" href="#main">Skip to Content</a><div class="progress" aria-hidden="true"></div><header><div class="header-start"><button id="toc-toggle" class="sidebar-toggle" type="button" aria-label="Hide Contents" title="Hide Contents" aria-controls="contents" aria-expanded="true">'+self.icon('contents')+'</button><span class="brand">'+esc(d.get('brand',d['title']))+'</span></div><div class="tools"><div class="theme-control"><button id="theme-toggle" class="header-icon-button" type="button" aria-label="Change Theme" title="Change Theme" aria-haspopup="menu" aria-expanded="false" aria-controls="theme-menu">'+self.icon('theme')+'</button><div id="theme-menu" class="theme-menu" role="menu" aria-label="Color Theme" hidden>'+menu+'</div></div><button class="header-icon-button" data-print type="button" aria-label="Print" title="Print">'+self.icon('print')+'</button></div></header><div class="contents-backdrop" aria-hidden="true"></div><div class="layout"><div class="contents-slot"><aside id="contents" aria-labelledby="contents-title"><div class="contents-heading"><p id="contents-title">On This Page</p><button class="contents-close" type="button" aria-label="Close Contents">'+self.icon('close')+'</button></div><nav aria-label="Table of Contents"></nav></aside></div><main id="main">'+body+'</main></div><script>'+js+'</script><template id="font-licenses"><pre>'+esc('\n\n'.join(licenses))+'</pre></template></body></html>'
        problems=check_html(result)
        if problems:raise ValueError('\n'.join(problems))
        return result

def validate_chart(kind,d):
    def nums(values,positive=False):
        if not values:raise ValueError('Chart data cannot be empty')
        if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or (positive and v<0) for v in values):raise ValueError('Chart values must be finite numbers'+(' >= 0' if positive else ''))
    if kind in ('line','area'):
        n=len(d['categories'])
        if not n or not d['series']:raise ValueError('Line/area needs categories and series')
        for s in d['series']:
            if len(s['values'])!=n:raise ValueError('Every series must match categories length')
            nums(s['values'])
    elif kind in ('bar','donut'):
        if len(d['categories'])!=len(d['values']):raise ValueError('categories and values must match')
        nums(d['values'],kind=='donut')
        if kind=='donut' and sum(d['values'])<=0:raise ValueError('Donut needs a positive total')
    elif kind=='scatter':
        nums([p['x'] for p in d['points']]);nums([p['y'] for p in d['points']])
    elif kind=='histogram':
        nums([b['count'] for b in d['bins']],True)
        for i,b in enumerate(d['bins']):
            if b['high']<=b['low'] or (i and b['low']!=d['bins'][i-1]['high']):raise ValueError('Histogram bins must be increasing, contiguous, equal width')
            if b['high']-b['low']!=d['bins'][0]['high']-d['bins'][0]['low']:raise ValueError('Histogram bins must be equal width')
    elif kind=='heatmap':
        if len(d['rows'])!=len(d['values']) or not d['columns']:raise ValueError('Heatmap requires row and column labels matching values')
        for row in d['values']:
            if len(row)!=len(d['columns']):raise ValueError('Heatmap matrix must match labels')
            nums(row,True)
    elif kind=='box':
        if not d['groups']:raise ValueError('Box needs groups')
        for g in d['groups']:
            v=[g[k] for k in ('min','q1','median','q3','max')];nums(v)
            if v!=sorted(v):raise ValueError('Box values must satisfy min <= q1 <= median <= q3 <= max')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path,help='Document JSON, or standalone HTML when --check is used')
    parser.add_argument('-o','--output',type=Path)
    parser.add_argument('--check',action='store_true',help='Check HTML resources and IDs without building')
    args=parser.parse_args()
    try:
        if args.check:
            problems=check_html(args.input.read_text(encoding='utf-8'))
            if problems:raise ValueError('\n'.join(problems))
            print('PASS: one H1, unique IDs, no external asset dependencies. Inspect appearance and interactions in a browser too.');return
        if not args.output:parser.error('Building requires -o output.html')
        doc=json.loads(args.input.read_text(encoding='utf-8'));result=Renderer(doc,args.input.resolve().parent).render()
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(result,encoding='utf-8')
        print(f'Built {args.output} ({len(result.encode()):,} bytes). Fonts, styles, scripts and media are embedded.')
    except (ValueError,KeyError,TypeError,OSError) as error:
        print('Build error: '+str(error),file=sys.stderr);sys.exit(1)

if __name__=='__main__':main()
