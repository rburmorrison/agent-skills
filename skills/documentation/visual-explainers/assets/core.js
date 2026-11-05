
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const headings=$$('main h2,main h3').filter(h=>!h.classList.contains('component-title')&&!h.closest('[role="tabpanel"]'));
const nav=$('nav');
headings.forEach((h,i)=>{if(!h.id)h.id='section-'+i;let a=document.createElement('a');a.href='#'+h.id;a.textContent=h.textContent;if(h.tagName==='H3')a.className='sub';nav.append(a)});
let headerOffset=95;
function measureHeader(){const header=$('header');headerOffset=getComputedStyle(header).position==='sticky'?header.getBoundingClientRect().height+20:20;document.documentElement.style.setProperty('--header-offset',headerOffset+'px')}
function spy(){let current=headings[0];for(const h of headings){if(h.getBoundingClientRect().top<=headerOffset+4)current=h}if(innerHeight+scrollY>=document.documentElement.scrollHeight-5)current=headings.at(-1);$$('nav a').forEach(a=>{if(current&&a.hash==='#'+current.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')});let height=document.documentElement.scrollHeight-innerHeight;$('.progress').style.width=(height>0?scrollY/height*100:0)+'%'}
addEventListener('scroll',spy,{passive:true});addEventListener('resize',()=>{measureHeader();spy()});measureHeader();spy();
$('#toc-toggle').addEventListener('click',()=>{
  const hidden=$('#toc-toggle').getAttribute('aria-expanded')==='true';
  $('#contents').inert=hidden;
  $('#contents').setAttribute('aria-hidden',String(hidden));
  document.body.classList.toggle('contents-hidden',hidden);
  $('#toc-toggle').setAttribute('aria-expanded',String(!hidden));
  const label=hidden?'Show Contents':'Hide Contents';
  $('#toc-toggle').setAttribute('aria-label',label);
  $('#toc-toggle').title=label;
  measureHeader();spy();
});
$('.layout').addEventListener('transitionend',spy);
$$('details').forEach(d=>d.addEventListener('toggle',spy));
const themeToggle=$('#theme-toggle'),themeMenu=$('#theme-menu'),themeOptions=$$('[data-theme-value]');
function syncTheme(){themeOptions.forEach(b=>b.setAttribute('aria-checked',String(b.dataset.themeValue===document.body.dataset.theme)))}
function closeTheme(restore=false){themeMenu.hidden=true;themeToggle.setAttribute('aria-expanded','false');if(restore)themeToggle.focus()}
function openTheme(last=false){themeMenu.hidden=false;themeToggle.setAttribute('aria-expanded','true');const current=themeOptions.find(b=>b.getAttribute('aria-checked')==='true');(last?themeOptions.at(-1):current||themeOptions[0]).focus()}
themeToggle.addEventListener('click',()=>themeMenu.hidden?openTheme():closeTheme(true));
themeToggle.addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();openTheme(e.key==='ArrowUp')}else if(e.key==='Escape')closeTheme(true)});
themeMenu.addEventListener('keydown',e=>{let i=themeOptions.indexOf(document.activeElement);if(e.key==='ArrowDown')i=(i+1)%themeOptions.length;else if(e.key==='ArrowUp')i=(i+themeOptions.length-1)%themeOptions.length;else if(e.key==='Home')i=0;else if(e.key==='End')i=themeOptions.length-1;else if(e.key==='Escape'){e.preventDefault();closeTheme(true);return}else if(e.key==='Tab'){closeTheme(true);return}else return;e.preventDefault();themeOptions[i].focus()});
themeOptions.forEach(b=>b.addEventListener('click',()=>{document.body.dataset.theme=b.dataset.themeValue;syncTheme();closeTheme(true)}));
document.addEventListener('pointerdown',e=>{if(!e.target.closest('.theme-control'))closeTheme()});
document.addEventListener('focusin',e=>{if(!themeMenu.hidden&&!e.target.closest('.theme-control'))closeTheme()});
syncTheme();

const images=$$('main img');
if(images.length){
  const viewer=document.createElement('dialog');
  viewer.className='image-viewer';viewer.setAttribute('aria-label','Enlarged Image');
  viewer.innerHTML='<div class="image-viewer-bar"><span>Image Preview</span><div><button class="image-size" type="button" aria-pressed="false">Actual Size</button><button class="image-close" type="button" aria-label="Close Image"></button></div></div><div class="image-viewer-stage"><img alt=""></div><p class="image-viewer-caption"></p>';
  viewer.querySelector('.image-close').innerHTML="<svg class=\"icon\" viewBox=\"0 0 24 24\" aria-hidden=\"true\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.75\"><path d=\"m6 6 12 12M18 6 6 18\"/></svg>";
  document.body.append(viewer);
  const preview=viewer.querySelector('img'),size=viewer.querySelector('.image-size');
  let opener=null,previousOverflow='';
  images.forEach(img=>{
    const trigger=document.createElement('button');trigger.type='button';trigger.className='image-trigger';
    trigger.setAttribute('aria-label','Enlarge Image: '+(img.alt||'Image'));trigger.setAttribute('aria-haspopup','dialog');
    img.before(trigger);trigger.append(img);
    trigger.addEventListener('click',()=>{
      opener=trigger;preview.src=img.currentSrc||img.src;preview.alt=img.alt;
      viewer.querySelector('.image-viewer-caption').textContent=img.closest('figure')?.querySelector('figcaption')?.textContent||'';
      viewer.classList.remove('actual-size');size.textContent='Actual Size';size.setAttribute('aria-pressed','false');
      previousOverflow=document.documentElement.style.overflow;document.documentElement.style.overflow='hidden';
      viewer.showModal();
    });
  });
  size.addEventListener('click',()=>{
    const actual=viewer.classList.toggle('actual-size');size.textContent=actual?'Fit to Screen':'Actual Size';size.setAttribute('aria-pressed',String(actual));
  });
  viewer.querySelector('.image-close').addEventListener('click',()=>viewer.close());
  viewer.addEventListener('click',e=>{
    const r=viewer.getBoundingClientRect();
    if(e.target===viewer&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))viewer.close();
  });
  viewer.addEventListener('close',()=>{document.documentElement.style.overflow=previousOverflow;opener?.focus({preventScroll:true})});
}

$$('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const code=document.getElementById(b.dataset.copy);try{await navigator.clipboard.writeText(code.textContent);b.textContent='Copied'}catch{const r=document.createRange();r.selectNodeContents(code);const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected; press Ctrl/Cmd+C'}setTimeout(()=>b.textContent='Copy',2600)}));

document.querySelector('[data-print]')?.addEventListener('click',()=>window.print());
document.querySelectorAll('.tabs').forEach(group=>{
 const tabs=[...group.querySelectorAll(':scope > .tab-list > [role="tab"]')];
 function choose(button){tabs.forEach(t=>{const active=t===button;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!active});window.dispatchEvent(new Event('resize'))}
 tabs.forEach((t,i)=>{t.addEventListener('click',()=>choose(t));t.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight')next=(i+1)%tabs.length;else if(e.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;else if(e.key==='Home')next=0;else if(e.key==='End')next=tabs.length-1;else return;e.preventDefault();choose(tabs[next]);tabs[next].focus()})});
});
window.Explainer={chart:(id,patch)=>window.ExplainerCharts?.update(id,patch)};
