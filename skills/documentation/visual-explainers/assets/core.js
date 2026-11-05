
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const headings=$$('main h2,main h3').filter(h=>!h.classList.contains('component-title')&&!h.closest('[role="tabpanel"]'));
const nav=$('nav');
headings.forEach((h,i)=>{if(!h.id)h.id='section-'+i;let a=document.createElement('a');a.href='#'+encodeURIComponent(h.id);a.dataset.headingId=h.id;a.textContent=h.textContent;if(h.tagName==='H3')a.className='sub';nav.append(a)});
let headerOffset=95,tocNavigation=null,currentHeadingId=null,spyScheduled=false;
function measureHeader(){
  const header=$('header'),height=header.getBoundingClientRect().height;
  headerOffset=getComputedStyle(header).position==='sticky'?height+20:20;
  document.documentElement.style.setProperty('--header-offset',headerOffset+'px');
  document.documentElement.style.setProperty('--header-height',height+'px');
}
function headingVisible(h){
  return !h.closest('details:not([open]),[hidden]')&&h.getClientRects().length>0&&getComputedStyle(h).visibility!=='hidden';
}
function spy(){
  const y=scrollY,maxScroll=Math.max(0,document.documentElement.scrollHeight-innerHeight);
  if(tocNavigation&&(!headingVisible(tocNavigation.target)||(!tocNavigation.moving&&Math.abs(y-tocNavigation.landedY)>1)))tocNavigation=null;
  currentHeadingId=ExplainerNavigation.selectHeading(headings.map((h,order)=>({id:h.id,order,top:h.getBoundingClientRect().top,visible:headingVisible(h)})),{
    readingLine:headerOffset,scrollY:y,maxScroll,preferredId:tocNavigation?.target.id,currentId:currentHeadingId
  });
  $$('nav a').forEach(a=>{if(a.dataset.headingId===currentHeadingId)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')});
  $('.progress').style.width=(maxScroll>0?Math.min(100,y/maxScroll*100):0)+'%';
}
function scheduleSpy(){
  if(spyScheduled)return;
  spyScheduled=true;requestAnimationFrame(()=>{spyScheduled=false;spy()});
}
function stopTocMotion(){
  if(!tocNavigation?.moving)return;
  tocNavigation=null;window.scrollTo({top:scrollY,behavior:'instant'});scheduleSpy();
}
function navigateToHeading(target){
  const state={target,moving:true,landedY:null};tocNavigation=state;
  for(let parent=target.parentElement;parent;parent=parent.parentElement){if(parent.tagName==='DETAILS')parent.open=true}
  if(mobileContents.matches)closeContents(false);
  measureHeader();target.tabIndex=-1;target.focus({preventScroll:true});
  const hash='#'+encodeURIComponent(target.id);
  if(location.hash!==hash){try{history.pushState(null,'',hash)}catch{/* Scrolling still works when history updates are unavailable. */}}
  const destination=()=>Math.max(0,Math.min(target.getBoundingClientRect().top+scrollY-headerOffset,Math.max(0,document.documentElement.scrollHeight-innerHeight)));
  let top=destination();
  const behavior=matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth';
  spy();window.scrollTo({top,behavior});
  let previous=scrollY,quiet=0;const started=performance.now();
  function settled(){
    if(tocNavigation!==state)return;
    const shifted=destination();
    if(Math.abs(shifted-top)>2){top=shifted;quiet=0;window.scrollTo({top,behavior})}
    const y=scrollY;quiet=Math.abs(y-previous)<.5?quiet+1:0;previous=y;
    if(Math.abs(y-top)<=1||(quiet>=4&&performance.now()-started>200)||performance.now()-started>4000){
      state.moving=false;state.landedY=y;spy();return;
    }
    requestAnimationFrame(settled);
  }
  requestAnimationFrame(settled);
}
addEventListener('scroll',scheduleSpy,{passive:true});
addEventListener('resize',()=>{if(!tocNavigation?.moving)tocNavigation=null;measureHeader();scheduleSpy()});
function manualScrollIntent(e){
  if(e.target.closest?.('aside,dialog,input,textarea,select,[contenteditable="true"]'))return;
  stopTocMotion();
}
addEventListener('wheel',manualScrollIntent,{passive:true});
addEventListener('touchstart',manualScrollIntent,{passive:true});
addEventListener('keydown',e=>{if(['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(e.key)&&!e.target.closest?.('button'))manualScrollIntent(e)});
addEventListener('pointerdown',e=>{if(!e.target.closest?.('header,aside,dialog'))stopTocMotion()},{passive:true});
function restoreHashSelection(){
  let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1)))}catch{return}
  if(target&&headings.includes(target)&&headingVisible(target))tocNavigation={target,moving:false,landedY:scrollY};
  spy();
}
addEventListener('popstate',()=>{tocNavigation=null;scheduleSpy()});
addEventListener('hashchange',()=>requestAnimationFrame(restoreHashSelection));
addEventListener('load',()=>{if(!tocNavigation)restoreHashSelection()});
measureHeader();spy();
const contents=$('#contents'),contentsToggle=$('#toc-toggle'),mobileContents=matchMedia('(max-width:850px)');
let desktopContentsOpen=true,mobileContentsOpen=false,contentsOverflow=null;
function syncContents(restore=false){
  const mobile=mobileContents.matches,open=mobile?mobileContentsOpen:desktopContentsOpen;
  document.body.classList.toggle('contents-hidden',!desktopContentsOpen);
  document.body.classList.toggle('contents-open',mobile&&open);
  contents.inert=!open;contents.setAttribute('aria-hidden',String(!open));
  contentsToggle.setAttribute('aria-expanded',String(open));
  contentsToggle.setAttribute('aria-label',open?'Hide Contents':'Show Contents');
  contentsToggle.title=open?'Hide Contents':'Show Contents';
  $('main').inert=mobile&&open;$('.tools').inert=mobile&&open;
  if(mobile){contents.setAttribute('role','dialog');contents.setAttribute('aria-modal','true')}
  else{contents.removeAttribute('role');contents.removeAttribute('aria-modal')}
  if(mobile&&open){
    if(contentsOverflow===null)contentsOverflow=document.documentElement.style.overflow;
    document.documentElement.style.overflow='hidden';
  }else if(contentsOverflow!==null){document.documentElement.style.overflow=contentsOverflow;contentsOverflow=null}
  if(restore)contentsToggle.focus({preventScroll:true});
  measureHeader();spy();
}
function closeContents(restore=true){mobileContentsOpen=false;syncContents(restore)}
contentsToggle.addEventListener('click',()=>{
  if(mobileContents.matches){
    stopTocMotion();mobileContentsOpen=!mobileContentsOpen;syncContents(!mobileContentsOpen);
    if(mobileContentsOpen){const active=nav.querySelector('[aria-current]')||$('.contents-close');active.focus({preventScroll:true});const item=active.getBoundingClientRect(),panel=contents.getBoundingClientRect();if(item.bottom>panel.bottom-16)contents.scrollTop+=item.bottom-panel.bottom+16;else if(item.top<panel.top+16)contents.scrollTop-=panel.top+16-item.top}
  }else{desktopContentsOpen=!desktopContentsOpen;syncContents()}
});
$('.contents-close').addEventListener('click',()=>closeContents());
$('.contents-backdrop').addEventListener('click',()=>closeContents());
contents.addEventListener('keydown',e=>{
  if(!mobileContents.matches||!mobileContentsOpen)return;
  if(e.key==='Escape'){e.preventDefault();closeContents();return}
  if(e.key==='Tab'){
    const stops=[...contents.querySelectorAll('button,a[href]')],first=stops[0],last=stops.at(-1);
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
    else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
  }
});
nav.addEventListener('click',e=>{
  const link=e.target.closest('a');if(!link||e.button>0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
  const target=document.getElementById(link.dataset.headingId);if(!target)return;
  e.preventDefault();navigateToHeading(target);
});
mobileContents.addEventListener('change',()=>{
  const hadFocus=contents.contains(document.activeElement);
  mobileContentsOpen=false;syncContents(hadFocus&&(mobileContents.matches||!desktopContentsOpen));
});
syncContents();
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
