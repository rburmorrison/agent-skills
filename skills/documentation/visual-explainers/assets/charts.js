/* Offline SVG charts. Declarative data, shared inspection, no third-party runtime. */
(() => {
  const NS='http://www.w3.org/2000/svg', instances=new Map();
  const palette=['var(--accent)','var(--chart-secondary)','var(--chart-third)','var(--chart-fourth)','var(--chart-fifth)'];
  const fmt=n=>typeof n==='number'&&Number.isInteger(n)?new Intl.NumberFormat('en-US').format(n):String(n);
  const axisFmt=n=>fmt(Number(n.toPrecision(8)));
  const color=i=>palette[i%palette.length];
  function svgNode(tag,attrs={},text){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!==undefined)e.textContent=text;return e}
  function htmlNode(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
  function numberUnit(n,unit){return fmt(n)+(unit?' '+unit:'')}
  function dataRows(c){const d=c.data;
    if(c.kind==='line'||c.kind==='area')return {headers:[c.xLabel||'Category',...d.series.map(s=>s.name)],rows:d.categories.map((n,i)=>[n,...d.series.map(s=>s.values[i])])};
    if(c.kind==='bar'||c.kind==='donut')return {headers:['Category',c.yLabel||c.unit||'Value'],rows:d.categories.map((n,i)=>[n,d.values[i]])};
    if(c.kind==='scatter')return {headers:['Observation',c.xLabel,c.yLabel],rows:d.points.map(p=>[p.label,p.x,p.y])};
    if(c.kind==='histogram')return {headers:['Interval ('+(c.binUnit||'units')+')',c.yLabel||'Count'],rows:d.bins.map(b=>[b.low+'–'+b.high,b.count])};
    if(c.kind==='heatmap')return {headers:[c.yLabel||'Row',...d.columns],rows:d.rows.map((r,i)=>[r,...d.values[i]])};
    if(c.kind==='box')return {headers:['Group','Min','Q1','Median','Q3','Max'],rows:d.groups.map(g=>[g.name,g.min,g.q1,g.median,g.q3,g.max])};
  }
  function table(state){const t=dataRows(state.config),el=htmlNode('table'),head=htmlNode('thead'),tr=htmlNode('tr'),body=htmlNode('tbody');t.headers.forEach(h=>{const th=htmlNode('th','',h);th.scope='col';tr.append(th)});head.append(tr);t.rows.forEach(row=>{const r=htmlNode('tr');row.forEach(v=>r.append(htmlNode('td','',fmt(v))));body.append(r)});el.append(head,body);state.root.querySelector('.chart-data .table-wrap').replaceChildren(el)}
  function legend(state,entries){const l=state.root.querySelector('.chart-legend');l.replaceChildren();entries.forEach((name,i)=>{const span=htmlNode('span'),swatch=htmlNode('i',state.config.kind==='line'&&i===1?'dashed':'');swatch.style.setProperty('--legend-color',color(i));swatch.setAttribute('aria-hidden','true');span.append(swatch,document.createTextNode(name));l.append(span)})}
  function niceStep(value){const power=10**Math.floor(Math.log10(Math.max(value,1e-9))),f=value/power;return (f<=1?1:f<=2?2:f<=5?5:10)*power}
  function domain(values,c={}){let lo=Math.min(0,...values),hi=Math.max(0,...values);if(lo===hi)hi=lo+1;const pad=(hi-lo)*.06;lo=lo<0?lo-pad:lo;hi=hi>0?hi+pad:hi;const step=niceStep((hi-lo)/4);return [c.yMin??Math.floor(lo/step)*step,c.yMax??Math.ceil(hi/step)*step]}
  function ticks(min,max){const step=niceStep((max-min)/5),out=[];for(let v=Math.ceil(min/step)*step;v<=max+step*.001;v+=step)out.push(Math.abs(v)<step*.001?0:v);return out}
  function yAxis(svg,c,W,H,m,max,min=0){for(const value of ticks(min,max)){const y=H-m.b-(H-m.b-m.t)*(value-min)/(max-min);svg.append(svgNode('path',{d:`M${m.l} ${y}H${W-m.r}`,class:'chart-grid'}),svgNode('text',{x:m.l-10,y:y+4,'text-anchor':'end',class:'chart-axis'},axisFmt(value)))}if(c.yLabel)svg.append(svgNode('text',{x:m.l,y:16,class:'chart-axis-title'},c.yLabel));if(c.xLabel)svg.append(svgNode('text',{x:(m.l+W-m.r)/2,y:H-5,'text-anchor':'middle',class:'chart-axis-title'},c.xLabel))}
  function labelX(svg,label,x,y){svg.append(svgNode('text',{x,y,'text-anchor':'middle',class:'chart-axis'},label))}
  function barLabel(svg,label,x,y,width){const text=String(label),size=Math.max(3,Math.floor((width-8)/6.6));if(text.length<=size){labelX(svg,text,x,y);return}const words=text.split(/\s+/),lines=[];let line='';for(const word of words){if((line+' '+word).trim().length>size&&line){lines.push(line);line=word}else line=(line+' '+word).trim()}if(line)lines.push(line);if(lines.length===1&&text.length>size){lines[0]=text.slice(0,size);lines[1]=text.slice(size)}const el=svgNode('text',{x,y,'text-anchor':'middle',class:'chart-axis'});el.append(svgNode('title',{},text));lines.slice(0,2).forEach((l,i)=>el.append(svgNode('tspan',{x,dy:i?14:0},l.length>size?l.slice(0,Math.max(1,size-1))+'…':l)));svg.append(el)}
  function mark(state,element,record){const i=state.records.length;element.setAttribute('data-mark',i);element.setAttribute('tabindex',i===0?'0':'-1');element.setAttribute('role','button');element.setAttribute('aria-label',record.title+'. '+record.rows.map(([k,v])=>k+': '+v).join('; '));state.records.push({...record,element});return element}
  function render(state){
    const c=state.config,d=c.data,host=state.canvas,W=Math.max(280,Math.round(host.clientWidth)),H=c.kind==='heatmap'?310:320,m={l:c.kind==='heatmap'?92:54,r:18,t:32,b:54};
    const svg=svgNode('svg',{viewBox:`0 0 ${W} ${H}`,role:'group','aria-label':c.title});svg.append(svgNode('title',{},c.title));
    state.records=[];state.svg=svg;state.dim={W,H,m};state.crosshair=null;state.selection=null;state.active=-1;state.tip.hidden=true;
    const plotW=W-m.l-m.r,plotH=H-m.t-m.b;
    const series=c.kind==='line'||c.kind==='area';
    if(series){
      const n=d.categories.length,[min,max]=domain(d.series.flatMap(s=>s.values),c),x=i=>m.l+(n===1?plotW/2:plotW*i/(n-1)),y=v=>H-m.b-plotH*(v-min)/(max-min);
      yAxis(svg,c,W,H,m,max,min);legend(state,d.series.length>1?d.series.map(s=>s.name):[]);
      const slots=Math.max(2,Math.min(n,Math.floor(plotW/(Math.max(...d.categories.map(v=>String(v).length))*6.8+18)))),shown=new Set(Array.from({length:slots},(_,i)=>Math.round(i*(n-1)/(slots-1))));d.categories.forEach((v,i)=>{if(shown.has(i))labelX(svg,v,x(i),H-m.b+22)});
      const hit=svgNode('rect',{x:m.l,y:m.t,width:plotW,height:plotH,fill:'transparent','data-plot-hit':'true'});svg.append(hit);
      d.series.forEach((s,j)=>{
        const points=s.values.map((v,i)=>[x(i),y(v)]),path=points.map((p,i)=>(i?'L':'M')+p.join(' ')).join(' ');
        if(c.kind==='area')svg.append(svgNode('path',{d:path+`L${x(n-1)} ${y(0)}L${x(0)} ${y(0)}Z`,fill:color(j),opacity:.16,'pointer-events':'none'}));
        svg.append(svgNode('path',{d:path,class:'chart-line',stroke:color(j),'stroke-dasharray':j===1?'6 4':'none','pointer-events':'none'}));
      });
      d.categories.forEach((label,i)=>{const el=svgNode('circle',{cx:x(i),cy:y(d.series[0].values[i]),r:4,fill:color(0),stroke:'var(--paper)','stroke-width':1.5});svg.append(mark(state,el,{title:(c.pointPrefix||'')+label,rows:d.series.map(s=>[s.name,numberUnit(s.values[i],c.unit)]),x:x(i),y:y(d.series[0].values[i])}))});
      state.crosshair=svgNode('path',{class:'chart-crosshair',visibility:'hidden'});state.selection=svgNode('circle',{r:6,class:'chart-selection',visibility:'hidden'});svg.append(state.crosshair,state.selection);
    }else if(c.kind==='bar'||c.kind==='histogram'){
      const hist=c.kind==='histogram',values=hist?d.bins.map(b=>b.count):d.values,n=values.length,[min,max]=domain(values,c),step=plotW/n,yAt=v=>H-m.b-plotH*(v-min)/(max-min),zero=yAt(0);
      yAxis(svg,c,W,H,m,max,min);legend(state,[]);
      values.forEach((v,i)=>{const x=m.l+i*step+(hist?1:step*.17),width=hist?step-2:step*.66,y=Math.min(zero,yAt(v));
        const label=hist?`${d.bins[i].low}–${d.bins[i].high} ${c.binUnit||''}`:d.categories[i];
        const el=svgNode('rect',{x,y,width:Math.max(1,width),height:Math.abs(yAt(v)-zero),rx:hist?1:4,fill:'var(--accent)',opacity:.86});
        svg.append(mark(state,el,{title:label,rows:[[c.yLabel||'Value',numberUnit(v,c.unit)]],x:x+width/2,y}));
        if(hist){if(i===0)labelX(svg,d.bins[i].low,m.l,H-m.b+22);if(W>450||i%2===1||i===n-1)labelX(svg,d.bins[i].high,m.l+(i+1)*step,H-m.b+22)}else{barLabel(svg,label,x+width/2,H-m.b+20,step)}
      });
    }else if(c.kind==='scatter'){
      const [xmin,xmax]=domain(d.points.map(p=>p.x)),[ymin,ymax]=domain(d.points.map(p=>p.y),c);
      yAxis(svg,c,W,H,m,ymax,ymin);legend(state,[]);for(const v of ticks(xmin,xmax))labelX(svg,axisFmt(v),m.l+plotW*(v-xmin)/(xmax-xmin),H-m.b+22);
      svg.append(svgNode('rect',{x:m.l,y:m.t,width:plotW,height:plotH,fill:'transparent','data-plot-hit':'true'}));
      d.points.forEach(p=>{const x=m.l+plotW*(p.x-xmin)/(xmax-xmin),y=H-m.b-plotH*(p.y-ymin)/(ymax-ymin),el=svgNode('circle',{cx:x,cy:y,r:5,fill:'var(--accent)',opacity:.85});svg.append(mark(state,el,{title:p.label,rows:[[c.xLabel,numberUnit(p.x,c.xUnit)],[c.yLabel,numberUnit(p.y,c.unit)]],x,y}))});
    }else if(c.kind==='donut'){
      const total=d.values.reduce((a,b)=>a+b,0),cx=W/2,cy=H/2-8,r=101,inner=62;let angle=-Math.PI/2;legend(state,d.categories);
      const at=(radius,a)=>[cx+Math.cos(a)*radius,cy+Math.sin(a)*radius];
      d.values.forEach((v,i)=>{const end=angle+Math.min(v/total*Math.PI*2,Math.PI*2-0.00001),large=end-angle>Math.PI?1:0,p1=at(r,angle),p2=at(r,end),p3=at(inner,end),p4=at(inner,angle),path=`M${p1}A${r} ${r} 0 ${large} 1 ${p2}L${p3}A${inner} ${inner} 0 ${large} 0 ${p4}Z`,mid=(angle+end)/2,pos=at((r+inner)/2,mid),el=svgNode('path',{d:path,fill:color(i),stroke:'var(--paper)','stroke-width':3});svg.append(mark(state,el,{title:d.categories[i],rows:[[c.valueLabel||c.yLabel||'Value',numberUnit(v,c.unit)],['Share',(v/total*100).toFixed(1)+'%']],x:pos[0],y:pos[1]}));angle=end});
      svg.append(svgNode('text',{x:cx,y:cy-2,'text-anchor':'middle',fill:'var(--ink)','font-size':26,'font-weight':700},fmt(total)),svgNode('text',{x:cx,y:cy+22,'text-anchor':'middle',class:'chart-axis'},c.unit+' Total'));
    }else if(c.kind==='heatmap'){
      const rows=d.rows.length,cols=d.columns.length,max=Math.max(1,...d.values.flat()),cw=plotW/cols,ch=plotH/rows;legend(state,[]);const scale=htmlNode('span','heatmap-scale');scale.append(htmlNode('span','','0'),htmlNode('i',''),htmlNode('span','',numberUnit(Math.max(...d.values.flat()),c.unit)));state.root.querySelector('.chart-legend').append(scale);
      d.rows.forEach((row,ri)=>{svg.append(svgNode('text',{x:m.l-9,y:m.t+(ri+.5)*ch+4,'text-anchor':'end',class:'chart-axis'},W<450?row.slice(0,3):row));d.columns.forEach((col,ci)=>{const v=d.values[ri][ci],x=m.l+ci*cw+2,y=m.t+ri*ch+2,el=svgNode('rect',{x,y,width:Math.max(1,cw-4),height:ch-4,rx:3,fill:'var(--accent)',opacity:.12+.82*v/max});svg.append(mark(state,el,{title:row+' · '+col,rows:[[c.valueLabel||'Value',numberUnit(v,c.unit)]],x:x+cw/2-2,y:y+ch/2-2}));if(cw>48)svg.append(svgNode('text',{x:x+cw/2-2,y:y+ch/2+2,'text-anchor':'middle',fill:'var(--ink)','font-size':11,'pointer-events':'none'},v))})});
      d.columns.forEach((col,i)=>{if(W>=450||i%2===0)labelX(svg,col,m.l+(i+.5)*cw,H-m.b+22)});svg.append(svgNode('text',{x:(m.l+W-m.r)/2,y:H-5,'text-anchor':'middle',class:'chart-axis-title'},c.xLabel));
    }else if(c.kind==='box'){
      const [min,max]=domain(d.groups.flatMap(g=>[g.min,g.max]),c),y=v=>H-m.b-plotH*(v-min)/(max-min),step=plotW/d.groups.length;legend(state,[]);yAxis(svg,c,W,H,m,max,min);
      d.groups.forEach((g,i)=>{const x=m.l+(i+.5)*step,bw=Math.min(64,step*.58),el=svgNode('g');el.append(svgNode('rect',{x:x-bw/2-6,y:y(g.max)-5,width:bw+12,height:y(g.min)-y(g.max)+10,fill:'transparent'}),svgNode('path',{d:`M${x} ${y(g.max)}V${y(g.min)}M${x-bw*.3} ${y(g.max)}H${x+bw*.3}M${x-bw*.3} ${y(g.min)}H${x+bw*.3}`,stroke:'var(--accent)','stroke-width':2,fill:'none'}),svgNode('rect',{x:x-bw/2,y:y(g.q3),width:bw,height:y(g.q1)-y(g.q3),fill:'var(--wash)',stroke:'var(--accent)','stroke-width':2,rx:3}),svgNode('path',{d:`M${x-bw/2} ${y(g.median)}H${x+bw/2}`,stroke:'var(--accent)','stroke-width':3}));svg.append(mark(state,el,{title:g.name,rows:[['Minimum',numberUnit(g.min,c.unit)],['Q1',numberUnit(g.q1,c.unit)],['Median',numberUnit(g.median,c.unit)],['Q3',numberUnit(g.q3,c.unit)],['Maximum',numberUnit(g.max,c.unit)]],x,y:y(g.median)}));labelX(svg,g.name,x,H-m.b+22)});
    }
    host.replaceChildren(svg);table(state);
    const initial=state.records[Math.min(c.selectedIndex??0,state.records.length-1)];
    if(initial)state.status.textContent=summary(initial);
    if(c.selectedIndex!==undefined&&state.records[c.selectedIndex])highlight(state,c.selectedIndex);
  }
  function summary(r){return r.title+' — '+r.rows.map(([k,v])=>k+': '+v).join('; ')}
  function highlight(s,index){s.records.forEach((r,i)=>r.element.classList.toggle('is-active',i===index));const r=s.records[index];if(!r)return;if(s.crosshair){const {H,m}=s.dim;s.crosshair.setAttribute('d',`M${r.x} ${m.t}V${H-m.b}`);s.crosshair.setAttribute('visibility','visible');s.selection.setAttribute('cx',r.x);s.selection.setAttribute('cy',r.y);s.selection.setAttribute('visibility','visible')}}
  function show(s,index,event){const r=s.records[index];if(!r)return;highlight(s,index);s.active=index;s.status.textContent=summary(r);
    const title=htmlNode('strong','',r.title),dl=htmlNode('dl');r.rows.forEach(([k,v])=>dl.append(htmlNode('dt','',k),htmlNode('dd','',v)));s.tip.replaceChildren(title,dl);s.tip.hidden=false;
    const root=s.root.getBoundingClientRect(),box=s.svg.getBoundingClientRect();let x,y;
    if(event){x=event.clientX-root.left+14;y=event.clientY-root.top+14}else{x=box.left-root.left+r.x/s.dim.W*box.width+14;y=box.top-root.top+r.y/s.dim.H*box.height-s.tip.offsetHeight-12}
    x=Math.max(8,Math.min(x,s.root.clientWidth-s.tip.offsetWidth-8));const bottom=Math.min(s.root.clientHeight-8,innerHeight-root.top-8);if(y+s.tip.offsetHeight>bottom)y=(event?event.clientY-root.top:box.top-root.top+r.y/s.dim.H*box.height)-s.tip.offsetHeight-12;y=Math.max(8,Math.min(y,bottom-s.tip.offsetHeight));s.tip.style.left=x+'px';s.tip.style.top=y+'px';
  }
  function hide(s){s.tip.hidden=true;s.records.forEach(r=>r.element.classList.remove('is-active'));if(s.crosshair){if(s.config.selectedIndex!==undefined)highlight(s,s.config.selectedIndex);else{s.crosshair.setAttribute('visibility','hidden');s.selection.setAttribute('visibility','hidden')}}}
  document.querySelectorAll('[data-chart]').forEach(root=>{
    const state={root,config:JSON.parse(root.dataset.chart),canvas:root.querySelector('.chart-canvas'),tip:root.querySelector('.chart-tooltip'),status:root.querySelector('.chart-status')};instances.set(state.config.id,state);render(state);
    function inspect(e){const el=e.target.closest?.('[data-mark]');if(el){show(state,+el.dataset.mark,e);return}if(!['line','area','scatter'].includes(state.config.kind))return;const b=state.svg.getBoundingClientRect(),{W,H,m}=state.dim,x=(e.clientX-b.left)/b.width*W,y=(e.clientY-b.top)/b.height*H;if(x<m.l||x>W-m.r||y<m.t||y>H-m.b){hide(state);return}let best=0,dist=Infinity;state.records.forEach((r,i)=>{const n=state.config.kind==='scatter'?Math.hypot(x-r.x,y-r.y):Math.abs(x-r.x);if(n<dist){dist=n;best=i}});show(state,best,e)}
    state.canvas.addEventListener('pointermove',inspect);state.canvas.addEventListener('click',inspect);
    state.canvas.addEventListener('pointerleave',()=>{const a=document.activeElement;if(state.canvas.contains(a)&&a.hasAttribute('data-mark'))show(state,+a.dataset.mark);else hide(state)});
    state.canvas.addEventListener('focusin',e=>{if(e.target.hasAttribute('data-mark'))show(state,+e.target.dataset.mark)});
    state.canvas.addEventListener('focusout',e=>{if(!state.canvas.contains(e.relatedTarget))hide(state)});
    state.canvas.addEventListener('keydown',e=>{const el=e.target.closest?.('[data-mark]');if(!el)return;let i=+el.dataset.mark,n=state.records.length;if(state.config.kind==='heatmap'&&['ArrowDown','ArrowUp'].includes(e.key)){const stride=state.config.data.columns.length;i=(i+(e.key==='ArrowDown'?stride:n-stride))%n}else if(['ArrowRight','ArrowDown'].includes(e.key))i=(i+1)%n;else if(['ArrowLeft','ArrowUp'].includes(e.key))i=(i+n-1)%n;else if(e.key==='Home')i=0;else if(e.key==='End')i=n-1;else if(e.key==='Escape'){hide(state);return}else if(e.key==='Enter'||e.key===' '){e.preventDefault();show(state,i);return}else return;e.preventDefault();state.records.forEach(r=>r.element.setAttribute('tabindex','-1'));state.records[i].element.setAttribute('tabindex','0');state.records[i].element.focus()});
    let width=state.canvas.clientWidth,scheduled=false;new ResizeObserver(()=>{const next=state.canvas.clientWidth;if(Math.abs(next-width)<1)return;width=next;if(!scheduled){scheduled=true;requestAnimationFrame(()=>{scheduled=false;render(state)})}}).observe(state.canvas);
  });
  window.ExplainerCharts={update(id,patch){const state=instances.get(id);if(!state)return;Object.assign(state.config,patch);render(state)}};
})();
