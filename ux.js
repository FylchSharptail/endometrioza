/* endometrioza UX layer v1 - resume/search/bookmarks/deep-links/reading/export/keys */
(function(){
'use strict';
var LS='endo-ux-v1';
var S={};try{S=JSON.parse(localStorage.getItem(LS)||'{}')}catch(_){}
S.bookmarks=S.bookmarks||[];S.visited=S.visited||{};
var saveT;function save(){clearTimeout(saveT);saveT=setTimeout(function(){try{localStorage.setItem(LS,JSON.stringify(S))}catch(_){}},500)}
function fmt(s){s=Math.max(0,s|0);var h=s/3600|0,m=(s%3600)/60|0,x=s%60;return(h?h+':'+(m<10?'0':''):'')+m+':'+(x<10?'0':'')+x}
function ytCmd(f,a){var fr=document.getElementById('yt-player');if(!fr||!fr.contentWindow)return;try{fr.contentWindow.postMessage(JSON.stringify({event:'command',func:f,args:a||[]}),'*')}catch(_){}}

var curT=0,ytPlaying=false;
window.addEventListener('message',function(e){
  if((e.origin||'').indexOf('youtube.com')<0)return;
  var d;try{d=JSON.parse(e.data)}catch(_){return}
  if(d.event==='infoDelivery'&&d.info){
    if(typeof d.info.currentTime==='number'){curT=d.info.currentTime;if(curT>3){S.lastTime=curT;save()}}
    if(typeof d.info.playerState==='number')ytPlaying=(d.info.playerState===1);
  }
  if(d.event==='onStateChange')ytPlaying=(d.info===1);
});

if('IntersectionObserver' in window){
  var io=new IntersectionObserver(function(ents){
    ents.forEach(function(ent){if(ent.isIntersecting){var id=ent.target.id;if(id&&!S.visited[id]){S.visited[id]=Date.now();save()}}});
  },{threshold:0.5});
  document.querySelectorAll('h2[id]').forEach(function(h){io.observe(h)});
}

function toast(msg){var t=document.createElement('div');t.className='ux-toast';t.textContent=msg;document.body.appendChild(t);requestAnimationFrame(function(){t.classList.add('show')});setTimeout(function(){t.classList.remove('show');setTimeout(function(){t.remove()},300)},1800)}

var hlSpans=[];
function clearHL(){hlSpans.forEach(function(s){var p=s.parentNode;if(p){p.replaceChild(document.createTextNode(s.textContent),s);p.normalize()}});hlSpans=[]}
function applyHL(q){
  clearHL();if(!q||q.length<2)return 0;
  var ql=q.toLowerCase();var root=document.querySelector('.wrap')||document.body;
  var walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){
    if(!n.nodeValue||n.nodeValue.toLowerCase().indexOf(ql)<0)return NodeFilter.FILTER_REJECT;
    if(n.parentNode.closest('#sn,#yt-box,script,style,.skip-link,mark.ux-hl'))return NodeFilter.FILTER_REJECT;
    return NodeFilter.FILTER_ACCEPT;
  }});
  var nodes=[],n;while(n=walker.nextNode())nodes.push(n);
  nodes.forEach(function(node){
    var t=node.nodeValue,low=t.toLowerCase(),i=low.indexOf(ql),last=0,frag=document.createDocumentFragment();
    if(i<0)return;
    while(i>=0){
      if(i>last)frag.appendChild(document.createTextNode(t.slice(last,i)));
      var sp=document.createElement('mark');sp.className='ux-hl';sp.textContent=t.slice(i,i+ql.length);
      frag.appendChild(sp);hlSpans.push(sp);last=i+ql.length;i=low.indexOf(ql,last);
    }
    if(last<t.length)frag.appendChild(document.createTextNode(t.slice(last)));
    node.parentNode.replaceChild(frag,node);
  });
  return hlSpans.length;
}

var KEYS=[['Space','Odtwarzaj / pauza'],['← →','±5 s (Shift: ±10 s)'],['J L','−10 / +10 s'],['K','Pauza'],['N P','Następny / poprzedni rozdział'],['S','Wyszukiwanie'],['M','Menu sekcji'],['R','Tryb czytania'],['B','Zakładka bieżącej sekcji'],['Esc','Zamknij nakładkę'],['?','Ta lista skrótów']];
function showKeys(){
  if(document.querySelector('.ux-overlay'))return;
  var ov=document.createElement('div');ov.className='ux-overlay';ov.setAttribute('role','dialog');ov.setAttribute('aria-label','Skróty klawiszowe');
  var html='<div class="ux-panel"><h3>Skróty klawiszowe</h3><table>';
  KEYS.forEach(function(k){html+='<tr><td><kbd>'+k[0].split(' ').join('</kbd> <kbd>')+'</kbd></td><td>'+k[1]+'</td></tr>'});
  html+='</table><button type="button" class="ux-close">Zamknij (Esc)</button></div>';
  ov.innerHTML=html;document.body.appendChild(ov);requestAnimationFrame(function(){ov.classList.add('show')});
  function close(){ov.classList.remove('show');setTimeout(function(){ov.remove()},250);document.removeEventListener('keydown',onK)}
  ov.querySelector('.ux-close').addEventListener('click',close);
  ov.addEventListener('click',function(e){if(e.target===ov)close()});
  function onK(e){if(e.key==='Escape'){e.preventDefault();close()}}
  document.addEventListener('keydown',onK);
  setTimeout(function(){ov.querySelector('.ux-close').focus()},60);
}

function exportMd(){
  var title=document.title||'Endometrioza';
  var out='# '+title+'\n\n';
  out+='Źródło: '+location.origin+location.pathname+'\n';
  out+='Data eksportu: '+new Date().toISOString().slice(0,10)+'\n\n';
  out+='> Materiał edukacyjny. Nie stanowi porady medycznej. Skonsultuj się z lekarzem.\n\n---\n';
  var root=document.querySelector('.wrap')||document.body;
  (function walk(el){
    for(var i=0;i<el.children.length;i++){
      var c=el.children[i];if(!c)continue;
      if(c.closest('#sn,#yt-box'))continue;
      var tag=c.tagName;
      if(tag==='H1'){out+='\n# '+c.textContent.trim()+'\n\n'}
      else if(tag==='H2'){out+='\n## '+c.textContent.trim()+'\n\n'}
      else if(tag==='H3'){out+='\n### '+c.textContent.trim()+'\n\n'}
      else if(tag==='H4'){out+='\n#### '+c.textContent.trim()+'\n\n'}
      else if(tag==='P'){var t=c.textContent.trim();if(t)out+=t+'\n\n'}
      else if(tag==='UL'||tag==='OL'){Array.prototype.forEach.call(c.children,function(li){var t=li.textContent.trim();if(t)out+='- '+t+'\n'});out+='\n'}
      else if(tag==='TABLE'){out+='\n[TABELA — zobacz online]\n\n'}
      else{walk(c)}
    }
  })(root);
  var blob=new Blob([out],{type:'text/markdown;charset=utf-8'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='endometrioza.md';document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1000);
  toast('Pobrano endometrioza.md');
}

function currentSecId(){var hs=document.querySelectorAll('h2[id]');for(var i=hs.length-1;i>=0;i--){if(hs[i].getBoundingClientRect().top<120)return hs[i].id}return hs[0]&&hs[0].id||''}
function copyDeepLink(){
  var sec=currentSecId();var t=curT>3?Math.round(curT):0;
  var u=location.origin+location.pathname+(sec?'#'+sec:'')+(t?(sec?'&':'#')+'t='+t:'');
  function done(){toast('Skopiowano: '+(sec||'top')+(t?' @'+fmt(t):''))}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(done,function(){prompt('Skopiuj:',u)})}
  else{prompt('Skopiuj:',u)}
}

function toggleReading(){document.body.classList.toggle('ux-reading');S.reading=document.body.classList.contains('ux-reading');save();toast(S.reading?'Tryb czytania: ON':'Tryb czytania: OFF')}

function toggleBookmark(id){if(!id)return;var i=S.bookmarks.indexOf(id);if(i>=0)S.bookmarks.splice(i,1);else S.bookmarks.push(id);save();updateBookmarkStars();renderBookmarks();toast(i>=0?'Usunięto zakładkę':'Dodano zakładkę')}
function updateBookmarkStars(){document.querySelectorAll('#sn-list > a .sn-star').forEach(function(star){var id=star.parentNode.hash.slice(1);star.textContent=S.bookmarks.indexOf(id)>=0?'★':'☆'})}

var snList,snMenu,resumeBtn,searchIn,bookmarksBox,footer;
function buildMenu(){
  snList=document.getElementById('sn-list');snMenu=document.getElementById('sn-menu');
  if(!snList||!snMenu||snList.dataset.uxReady)return;
  snList.dataset.uxReady='1';

  resumeBtn=document.createElement('button');resumeBtn.type='button';resumeBtn.id='sn-resume';resumeBtn.hidden=true;
  resumeBtn.addEventListener('click',function(){if(!S.lastTime)return;ytCmd('seekTo',[S.lastTime,true]);ytCmd('playVideo');snMenu.click()});
  snList.insertBefore(resumeBtn,snList.firstChild);
  refreshResume();

  var sh=document.createElement('div');sh.id='sn-sh';
  sh.innerHTML='<input id="sn-q" type="search" placeholder="Szukaj w treści..." aria-label="Szukaj w treści" autocomplete="off" spellcheck="false"><span id="sn-qc" aria-live="polite"></span>';
  resumeBtn.nextSibling?snList.insertBefore(sh,resumeBtn.nextSibling):snList.appendChild(sh);
  searchIn=document.getElementById('sn-q');
  var qc=document.getElementById('sn-qc');
  searchIn.addEventListener('input',function(){
    var v=searchIn.value.trim();var vl=v.toLowerCase();
    snList.querySelectorAll('a').forEach(function(a){if(a.closest('#sn-bm'))return;var t=(a.firstChild&&a.firstChild.nodeValue||a.textContent).toLowerCase();a.style.display=!vl||t.indexOf(vl)>=0?'':'none'});
    var n=applyHL(v);qc.textContent=v?(n?n+' wyst.':'brak'):'';
  });
  searchIn.addEventListener('keydown',function(e){
    if(e.key==='Escape'){if(searchIn.value){searchIn.value='';searchIn.dispatchEvent(new Event('input'));e.preventDefault();e.stopPropagation()}}
    else if(e.key==='Enter'){var a=snList.querySelector('a:not([style*="display: none"])');if(a){e.preventDefault();a.click()}}
  });

  snList.querySelectorAll('a').forEach(function(a){
    if(a.querySelector('.sn-star'))return;
    var id=a.hash.slice(1);
    var star=document.createElement('span');star.className='sn-star';star.textContent=S.bookmarks.indexOf(id)>=0?'★':'☆';
    star.setAttribute('role','button');star.setAttribute('tabindex','0');star.setAttribute('aria-label','Przełącz zakładkę');
    function tog(e){e.preventDefault();e.stopPropagation();toggleBookmark(id)}
    star.addEventListener('click',tog);star.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){tog(e)}});
    a.appendChild(star);
  });

  bookmarksBox=document.createElement('div');bookmarksBox.id='sn-bm';snList.appendChild(bookmarksBox);renderBookmarks();

  footer=document.createElement('div');footer.id='sn-foot';
  footer.innerHTML=
    '<button type="button" data-a="copy" aria-label="Kopiuj link" title="Kopiuj link">link</button>'+
    '<button type="button" data-a="read" aria-label="Tryb czytania" title="Tryb czytania (R)">czyt</button>'+
    '<button type="button" data-a="export" aria-label="Eksport" title="Eksport do .md">md</button>'+
    '<button type="button" data-a="print" aria-label="Drukuj" title="Drukuj">drk</button>'+
    '<button type="button" data-a="keys" aria-label="Skróty" title="Skróty (?)">?</button>';
  snList.appendChild(footer);
  footer.addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;e.stopPropagation();
    var a=b.dataset.a;
    if(a==='copy')copyDeepLink();
    else if(a==='read')toggleReading();
    else if(a==='export')exportMd();
    else if(a==='print')window.print();
    else if(a==='keys')showKeys();
  });
}

function refreshResume(){
  if(!resumeBtn)return;
  if(S.lastTime&&S.lastTime>5){resumeBtn.hidden=false;resumeBtn.textContent='▶ Wznów od '+fmt(S.lastTime)}
  else resumeBtn.hidden=true;
}

function renderBookmarks(){
  if(!bookmarksBox)return;
  if(!S.bookmarks.length){bookmarksBox.innerHTML='';return}
  var html='<div class="sn-bm-h">Zakładki</div>';
  S.bookmarks.forEach(function(id){
    var h=document.getElementById(id);if(!h)return;
    var txt=h.textContent.replace(/\s*\d+:\d+(?::\d+)?\s*$/,'').trim();
    html+='<a href="#'+id+'" data-bm="'+id+'"><span class="sn-bm-t">'+txt.replace(/</g,'&lt;')+'</span><span class="sn-star" role="button" tabindex="0" aria-label="Usuń zakładkę">★</span></a>';
  });
  bookmarksBox.innerHTML=html;
  bookmarksBox.querySelectorAll('.sn-star').forEach(function(s){s.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();toggleBookmark(s.parentNode.dataset.bm)})});
  bookmarksBox.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){setTimeout(function(){snMenu&&snMenu.classList.contains('on')&&snMenu.click()},60)})});
}

document.addEventListener('visibilitychange',function(){if(document.hidden&&curT>3){S.lastTime=curT;save()}else{refreshResume()}});
window.addEventListener('pagehide',function(){if(curT>3){S.lastTime=curT;save()}});

function applyHash(){
  var h=location.hash.slice(1);if(!h)return;
  var anchor=h.split('&')[0].split('?')[0].split('=')[0];
  var tm=h.match(/[&?#]t=(\d+)/)||h.match(/^t=(\d+)/);
  if(anchor&&anchor!=='t'){var el=document.getElementById(anchor);if(el)setTimeout(function(){el.scrollIntoView({behavior:'smooth',block:'start'})},200)}
  if(tm){var t=parseInt(tm[1],10);setTimeout(function(){ytCmd('seekTo',[t,true])},1800)}
}

document.addEventListener('keydown',function(e){
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  var t=e.target;if(t&&(/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)||t.isContentEditable))return;
  var k=e.key;
  if(k===' '){e.preventDefault();ytCmd(ytPlaying?'pauseVideo':'playVideo')}
  else if(k==='ArrowLeft'&&!e.shiftKey){e.preventDefault();ytCmd('seekTo',[Math.max(0,curT-5),true])}
  else if(k==='ArrowRight'&&!e.shiftKey){e.preventDefault();ytCmd('seekTo',[curT+5,true])}
  else if(k==='ArrowLeft'&&e.shiftKey){e.preventDefault();ytCmd('seekTo',[Math.max(0,curT-10),true])}
  else if(k==='ArrowRight'&&e.shiftKey){e.preventDefault();ytCmd('seekTo',[curT+10,true])}
  else if(k==='j'||k==='J'){ytCmd('seekTo',[Math.max(0,curT-10),true])}
  else if(k==='l'||k==='L'){ytCmd('seekTo',[curT+10,true])}
  else if(k==='k'||k==='K'){ytCmd('pauseVideo')}
  else if(k==='n'||k==='N'){var bN=document.getElementById('ac-next');if(bN)bN.click()}
  else if(k==='p'||k==='P'){var bP=document.getElementById('ac-prev');if(bP)bP.click()}
  else if(k==='s'||k==='S'){e.preventDefault();if(snMenu&&!snMenu.classList.contains('on'))snMenu.click();setTimeout(function(){searchIn&&searchIn.focus()},120)}
  else if(k==='r'||k==='R'){toggleReading()}
  else if(k==='b'||k==='B'){toggleBookmark(currentSecId())}
  else if(k==='m'||k==='M'){if(snMenu)snMenu.click()}
  else if(k==='?'){showKeys()}
});

function mountProgress(){
  if(document.getElementById('ux-prog'))return;
  var p=document.createElement('div');p.id='ux-prog';p.setAttribute('aria-hidden','true');
  p.style.cssText='position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,#1b3a5c,#4a9eff);z-index:1060;pointer-events:none;will-change:width;transition:width .08s linear';
  document.body.appendChild(p);
  var ticking=false;
  function update(){
    var h=document.documentElement,b=document.body;
    var st=h.scrollTop||b.scrollTop;
    var sh=(h.scrollHeight||b.scrollHeight)-h.clientHeight;
    var pct=sh>0?Math.max(0,Math.min(100,(st/sh)*100)):0;
    p.style.width=pct+'%';
    ticking=false;
  }
  function onScroll(){if(!ticking){requestAnimationFrame(update);ticking=true}}
  window.addEventListener('scroll',onScroll,{passive:true});
  window.addEventListener('resize',onScroll,{passive:true});
  update();
}
function init(){buildMenu();if(S.reading)document.body.classList.add('ux-reading');applyHash();mountProgress()}
if(document.readyState==='complete'||document.readyState==='interactive')setTimeout(init,100);
else document.addEventListener('DOMContentLoaded',function(){setTimeout(init,100)});
window.addEventListener('hashchange',applyHash);
})();
