(function(){var C=[[0,'Dr Thaïs Aliabadi — wstęp'],[176,'Dlaczego endometrioza i PCOS nie są diagnozowane'],[496,'Niepłodność — wczesne badania'],[654,'Reklama'],[847,'Luka w edukacji zdrowotnej kobiet'],[924,'PCOS: objawy, diagnostyka, AMH'],[1288,'Nieregularne miesiączki, PCOS u nastolatek'],[1476,'Diagnostyka, USG miednicy; nazwa PCOS'],[1669,'Przerzedzanie włosów, trądzik; 4 fenotypy PCOS'],[2154,'Filary PCOS: oś HPA, androgeny, owulacja'],[2430,'Insulinooporność, tłuszcz trzewny, stan zapalny'],[2790,'Reklama'],[2950,'PCOS: stan zapalny, genetyka, styl życia'],[3151,'PCOS i płodność, zamrażanie jajeczek'],[3514,'Edukacja zdrowotna, AI; analogia z zaćmą'],[3680,'Leczenie PCOS: antykoncepcja, metformina'],[4004,'Suplementy, styl życia, GLP-1'],[4352,'Berberyna, metformina; GLP-1, alkohol'],[4753,'Recepty w PCOS; współwystępowanie z endometriozą'],[4916,'Reklama'],[4996,'Zamrażanie jajeczek, jakość jajeczek'],[5522,'Kluczowe wnioski PCOS'],[5763,'Niezdiagnozowana endometrioza a płodność'],[5966,'Endometrioza: objawy, diagnostyka'],[6150,'Zdrowie mężczyzn vs kobiet'],[6421,'Stan zapalny, implanty ektopowe, ból miednicy'],[6636,'Jakość jajeczek, endometrioza, AMH'],[6869,'Reklama'],[6973,'Badania, objawy endometriozy, testy'],[7292,'Leczenie: chirurgia, typy endometriozy'],[7522,'Przyczyny endometriozy, stan zapalny'],[7918,'Ginekologia vs położnictwo'],[8160,'Wnioski: leczenie endometriozy'],[8224,'Estrogen, progesteron, antagoniści GnRH'],[8559,'Stadium a ból, typy endometriozy'],[8629,'Ciąża, menopauza, depresja poporodowa'],[8995,'Torbiele, mięśniaki, USG'],[9245,'Ocena płodności; autoimmunologia'],[9471,'Rak piersi: kalkulator ryzyka, badania'],[10187,'Autoimmunologia, mgła mózgowa, inozytol'],[10386,'PMDD, post, dieta niskowęglowodanowa'],[10641,'Wypadanie włosów, perimenopauza'],[10840,'Progesteron, hormony, menopauza'],[11094,'Zakończenie']];
var CD=C.slice().sort(function(a,b){return b[0]-a[0]});
function getCh(t){for(var i=0;i<CD.length;i++)if(t>=CD[i][0])return CD[i][1];return''}
function getIdx(t){for(var i=C.length-1;i>=0;i--)if(t>=C[i][0])return i;return 0}
function fmt(s){s=Math.max(0,s|0);var h=s/3600|0,m=(s%3600)/60|0,x=s%60;return(h?h+':'+(m<10?'0':''):'')+m+':'+(x<10?'0':'')+x}
var box=document.getElementById('yt-box'),drag=document.getElementById('yt-drag'),rz=document.getElementById('yt-rz'),rzl=document.getElementById('yt-rzl'),rztl=document.getElementById('yt-rztl'),rztr=document.getElementById('yt-rztr'),rst=document.getElementById('yt-reset'),fr=document.getElementById('yt-player'),sub=document.getElementById('yt-subs');
var acTitle=document.querySelector('#yt-audio-ctrl .ac-title'),acCur=document.querySelector('#yt-audio-ctrl .ac-cur'),acDur=document.querySelector('#yt-audio-ctrl .ac-dur'),acBar=document.querySelector('#yt-audio-ctrl .ac-bar'),acProg=document.querySelector('#yt-audio-ctrl .ac-prog'),acPlay=document.getElementById('ac-play'),acPrev=document.getElementById('ac-prev'),acNext=document.getElementById('ac-next');
var acPlayIco=acPlay&&acPlay.firstChild;
var isMobile=window.innerWidth<1100;
if(isMobile){box.classList.add('audio');box.style.height='auto'}
if(acTitle)acTitle.textContent=C[0][1];
function cmd(fn,a){fr.contentWindow.postMessage(JSON.stringify({event:'command',func:fn,args:a||[]}),'https://www.youtube.com')}
document.addEventListener('click',function(e){var t=e.target.closest('.ts');if(!t)return;e.preventDefault();var sec=parseInt(t.getAttribute('data-t'),10);if(isNaN(sec))return;cmd('seekTo',[sec,!0]);cmd('playVideo');if(window.innerWidth<1100)fr.scrollIntoView({behavior:'smooth',block:'end'})});
var last=C[0][1],subTimer,curT=0,dur=0,playing=false;
if(sub)sub.textContent=C[0][1];
function setPlayIco(){if(acPlayIco)acPlayIco.nodeValue=playing?'⏸':'▶'}
window.addEventListener('message',function(e){if(e.origin.indexOf('youtube.com')===-1)return;var d;try{d=JSON.parse(e.data)}catch(_){return}if(d.event==='infoDelivery'&&d.info){if(typeof d.info.currentTime==='number'){curT=d.info.currentTime;var ch=getCh(curT);if(ch!==last){sub.textContent=ch;if(acTitle)acTitle.textContent=ch;last=ch;sub.classList.remove('fade');clearTimeout(subTimer);subTimer=setTimeout(function(){sub.classList.add('fade')},5000);updChapTips()}if(acCur)acCur.textContent=fmt(curT);if(dur>0&&acBar)acBar.style.width=(curT/dur*100)+'%'}if(typeof d.info.duration==='number'&&d.info.duration>0&&d.info.duration!==dur){dur=d.info.duration;if(acDur)acDur.textContent=fmt(dur)}if(typeof d.info.playerState==='number'){playing=(d.info.playerState===1);setPlayIco()}}if(d.event==='onStateChange'){playing=(d.info===1);setPlayIco()}});
fr.addEventListener('load',function(){fr.contentWindow.postMessage(JSON.stringify({event:'listening'}),'*');cmd('addEventListener',['onStateChange'])});
if(acPlay)acPlay.addEventListener('click',function(e){e.stopPropagation();cmd(playing?'pauseVideo':'playVideo')});
if(acPrev)acPrev.addEventListener('click',function(e){e.stopPropagation();var i=getIdx(curT-2);i=Math.max(0,i-1);cmd('seekTo',[C[i][0],!0]);cmd('playVideo')});
if(acNext)acNext.addEventListener('click',function(e){e.stopPropagation();var i=getIdx(curT);i=Math.min(C.length-1,i+1);cmd('seekTo',[C[i][0],!0]);cmd('playVideo')});
var acBack10=document.getElementById('ac-back10'),acFwd10=document.getElementById('ac-fwd10');
if(acBack10)acBack10.addEventListener('click',function(e){e.stopPropagation();cmd('seekTo',[Math.max(0,curT-10),!0])});
if(acFwd10)acFwd10.addEventListener('click',function(e){e.stopPropagation();cmd('seekTo',[(dur?Math.min(dur,curT+10):curT+10),!0])});
function updChapTips(){var i=getIdx(curT);var p=Math.max(0,i-1),n=Math.min(C.length-1,i+1);if(acPrev)acPrev.setAttribute('data-tip','Poprzedni rozdzia\u0142: '+C[p][1]);if(acNext)acNext.setAttribute('data-tip','Nast\u0119pny rozdzia\u0142: '+C[n][1])}
updChapTips();
if(acProg)acProg.addEventListener('click',function(e){if(!dur)return;var r=acProg.getBoundingClientRect();var p=(e.clientX-r.left)/r.width;cmd('seekTo',[p*dur,!0])});
function gxy(e){var t=e.touches?e.touches[0]:e;return{x:t.clientX,y:t.clientY}}
function promote(){if(box.classList.contains('dragged'))return;var r=box.getBoundingClientRect();box.classList.add('dragged');box.style.width=r.width+'px';box.style.height=r.height+'px';box.style.left=r.left+'px';box.style.top=r.top+'px'}
var ds=null;
function dstart(e){e.preventDefault();var p=gxy(e),r=box.getBoundingClientRect();ds={ox:p.x-r.left,oy:p.y-r.top};fr.style.pointerEvents='none'}
function dmove(e){if(!ds)return;e.preventDefault();var p=gxy(e);if(!box.classList.contains('dragged')){box.classList.add('dragged');box.style.width=box.offsetWidth+'px'}box.style.left=Math.max(0,Math.min(p.x-ds.ox,innerWidth-80))+'px';box.style.top=Math.max(0,Math.min(p.y-ds.oy,innerHeight-40))+'px'}
function dend(){if(!ds)return;ds=null;fr.style.pointerEvents=''}
var rs=null;
function rstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rs={sw:r.width,sh:r.height,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rmove(e){if(!rs)return;e.preventDefault();var p=gxy(e);box.style.width=Math.max(180,Math.min(rs.sw+(p.x-rs.sx),innerWidth-20))+'px';box.style.height=Math.max(120,Math.min(rs.sh+(p.y-rs.sy),innerHeight-20))+'px'}
function rend(){if(!rs)return;rs=null;fr.style.pointerEvents=''}
var rsl=null;
function rlstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rsl={sw:r.width,sh:r.height,sl:r.left,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rlmove(e){if(!rsl)return;e.preventDefault();var p=gxy(e);var dx=p.x-rsl.sx;var nw=Math.max(180,Math.min(rsl.sw-dx,innerWidth-20));var nh=Math.max(120,Math.min(rsl.sh+(p.y-rsl.sy),innerHeight-20));box.style.width=nw+'px';box.style.height=nh+'px';box.style.left=(rsl.sl+(rsl.sw-nw))+'px'}
function rlend(){if(!rsl)return;rsl=null;fr.style.pointerEvents=''}
var rstr=null;
function rtrstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rstr={sw:r.width,sh:r.height,st:r.top,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rtrmove(e){if(!rstr)return;e.preventDefault();var p=gxy(e);var dy=p.y-rstr.sy;var nw=Math.max(180,Math.min(rstr.sw+(p.x-rstr.sx),innerWidth-20));var nh=Math.max(120,Math.min(rstr.sh-dy,innerHeight-20));box.style.width=nw+'px';box.style.height=nh+'px';box.style.top=(rstr.st+(rstr.sh-nh))+'px'}
function rtrend(){if(!rstr)return;rstr=null;fr.style.pointerEvents=''}
var rstl=null;
function rtlstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rstl={sw:r.width,sh:r.height,sl:r.left,st:r.top,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rtlmove(e){if(!rstl)return;e.preventDefault();var p=gxy(e);var dx=p.x-rstl.sx;var dy=p.y-rstl.sy;var nw=Math.max(180,Math.min(rstl.sw-dx,innerWidth-20));var nh=Math.max(120,Math.min(rstl.sh-dy,innerHeight-20));box.style.width=nw+'px';box.style.height=nh+'px';box.style.left=(rstl.sl+(rstl.sw-nw))+'px';box.style.top=(rstl.st+(rstl.sh-nh))+'px'}
function rtlend(){if(!rstl)return;rstl=null;fr.style.pointerEvents=''}
function reset(){box.classList.remove('dragged');box.style.left='';box.style.top='';box.style.width='';box.style.height=''}
var hideBtn=document.getElementById('yt-hide'),showBtn=document.getElementById('yt-show');
function hide(){
  var br=box.getBoundingClientRect();
  var sr=showBtn.getBoundingClientRect();
  var tx,ty;
  if(sr.width){tx=(sr.left+sr.width/2)-(br.left+br.width/2);ty=(sr.top+sr.height/2)-(br.top+br.height/2)}
  else{tx=innerWidth-36-(br.left+br.width/2);ty=36-(br.top+br.height/2)}
  clearTimeout(box._hideT);clearTimeout(showBtn._tipT);
  box.classList.add('hiding');
  requestAnimationFrame(function(){box.style.transform='translate('+tx+'px,'+ty+'px) scale(.08)';box.style.opacity='0'});
  box._hideT=setTimeout(function(){
    box.classList.add('hidden');box.classList.remove('hiding');
    box.style.transform='';box.style.opacity='';
    showBtn.classList.add('on');
    requestAnimationFrame(function(){showBtn.classList.add('pulse');showTip(showBtn)});
    showBtn._tipT=setTimeout(function(){hideTip();showBtn.classList.remove('pulse')},3000);
  },500);
}
function show(){clearTimeout(showBtn._tipT);hideTip();showBtn.classList.remove('on','pulse');box.classList.remove('hidden','hiding');box.style.transform='';box.style.opacity='';showBars()}
hideBtn.addEventListener('click',function(e){e.stopPropagation();hide()});
showBtn.addEventListener('click',show);
var audioBtn=document.getElementById('yt-audio');
function updAudioBtn(){var isA=box.classList.contains('audio');var ico=audioBtn.querySelector('.ico');if(ico)ico.textContent=isA?'\u25a3':'\u266a';audioBtn.setAttribute('data-tip',isA?'Prze\u0142\u0105cz na pe\u0142ny odtwarzacz wideo z obrazem i napisami':'Prze\u0142\u0105cz na tryb tylko-d\u017awi\u0119k (ukrywa obraz, zostawia odtwarzacz audio z rozdzia\u0142ami)');audioBtn.setAttribute('aria-label',isA?'Tryb wideo':'Tryb audio')}
audioBtn.addEventListener('click',function(e){e.stopPropagation();var desktop=matchMedia('(min-width:1100px)').matches;if(!desktop){box.classList.toggle('audio');box.style.height='';updAudioBtn();return}
// FLIP: keep box BOTTOM edge (= audio-ctrl bottom) visually stable during + after toggle.
var curT=box.style.transform||'';
var curY=parseFloat((curT.match(/translateY\(([-\d.]+)px\)/)||[0,0])[1])||0;
var fromH=box.offsetHeight;
var goingToAudio=!box.classList.contains('audio');
if(goingToAudio){
  // Preserve user-set video dimensions to restore later.
  box._prevH=box.style.height||'';
}
// Suspend transitions, flip class, measure target height.
box.classList.add('no-tr');
box.classList.toggle('audio');
box.style.height='';box.style.transform='';
var toH;
if(goingToAudio){toH=box.offsetHeight;}
else{
  // Restore previous video height (if user had resized).
  if(box._prevH){box.style.height=box._prevH;toH=box.offsetHeight;}
  else{toH=box.offsetHeight;}
  box.style.height='';
}
var finalY=goingToAudio?(fromH-toH):0;
// Seed starting state.
box.style.height=fromH+'px';
box.style.transform='translateY('+curY+'px)';
void box.offsetHeight;
// Release transitions and animate to target.
box.classList.remove('no-tr');
box.classList.add('anim');
requestAnimationFrame(function(){
  box.style.height=toH+'px';
  box.style.transform='translateY('+finalY+'px)';
});
clearTimeout(box._animT);
box._animT=setTimeout(function(){
  box.classList.remove('anim');
  if(goingToAudio){
    // Keep box.h=toH and translateY to hold bottom edge visually.
    box.style.transform='translateY('+finalY+'px)';
  }else{
    // Back to video: restore user's inline height (if any), clear transform.
    box.style.height=box._prevH||'';
    box.style.transform='';
  }
},380);
updAudioBtn();});
updAudioBtn();
var barTimer;
var noHover=matchMedia('(hover: none)').matches;
function showBars(){box.classList.add('bars');clearTimeout(barTimer);if(!noHover)barTimer=setTimeout(function(){box.classList.remove('bars')},1800)}
box.addEventListener('mouseenter',showBars);
box.addEventListener('mousemove',showBars);
box.addEventListener('touchstart',showBars,{passive:true});
showBars();
var tipEl=null;
function ensureTip(){if(!tipEl){tipEl=document.createElement('div');tipEl.className='tip-portal';document.body.appendChild(tipEl)}}
function showTip(el){ensureTip();var text=el.getAttribute('data-tip')||el.getAttribute('aria-label')||'';if(!text)return;tipEl.textContent=text;var r=el.getBoundingClientRect();tipEl.classList.remove('top','bottom','left','show');var inNav=el.closest&&el.closest('#sn');if(inNav){tipEl.classList.add('left');tipEl.style.visibility='hidden';tipEl.classList.add('show');var tr=tipEl.getBoundingClientRect();var top=r.top+r.height/2-tr.height/2;top=Math.max(8,Math.min(top,innerHeight-tr.height-8));tipEl.style.left=(r.left-tr.width-12)+'px';tipEl.style.top=top+'px';tipEl.style.visibility=''}else{var below=(innerHeight-r.bottom)>r.top;tipEl.classList.add(below?'bottom':'top');tipEl.style.visibility='hidden';tipEl.classList.add('show');var tr2=tipEl.getBoundingClientRect();var left=r.left+r.width/2-tr2.width/2;left=Math.max(8,Math.min(left,innerWidth-tr2.width-8));tipEl.style.left=left+'px';tipEl.style.top=(below?(r.bottom+10):(r.top-tr2.height-10))+'px';tipEl.style.visibility=''}}
function hideTip(){if(tipEl)tipEl.classList.remove('show')}
function bindTip(el){var t,longPressed=false;function clr(){clearTimeout(t);el.classList.remove('ripping');hideTip()}function go(){clr();el.classList.remove('ripping');void el.offsetWidth;el.classList.add('ripping');t=setTimeout(function(){el.classList.remove('ripping');showTip(el)},500)}el.addEventListener('mouseenter',go);el.addEventListener('mouseleave',clr);el.addEventListener('touchstart',function(e){longPressed=false;clr();el.classList.remove('ripping');void el.offsetWidth;el.classList.add('ripping');t=setTimeout(function(){el.classList.remove('ripping');showTip(el);longPressed=true},500)},{passive:true});el.addEventListener('touchend',function(e){el.classList.remove('ripping');if(longPressed){e.preventDefault();setTimeout(clr,1800)}else{clr()}});el.addEventListener('touchcancel',clr);el.addEventListener('click',function(e){el.classList.remove('ripping');if(longPressed){e.preventDefault();e.stopImmediatePropagation();longPressed=false}},true)}
Array.prototype.forEach.call(document.querySelectorAll('[data-tip]'),bindTip);
window.addEventListener('scroll',hideTip,{passive:true});window.addEventListener('resize',hideTip);
drag.addEventListener('dblclick',reset);rst.addEventListener('click',function(e){e.stopPropagation();reset()});
drag.addEventListener('mousedown',dstart);
rz.addEventListener('mousedown',rstart);rzl.addEventListener('mousedown',rlstart);
rztl.addEventListener('mousedown',rtlstart);rztr.addEventListener('mousedown',rtrstart);
document.addEventListener('mousemove',function(e){dmove(e);rmove(e);rlmove(e);rtlmove(e);rtrmove(e)});
document.addEventListener('mouseup',function(){dend();rend();rlend();rtlend();rtrend()});
drag.addEventListener('touchstart',dstart,{passive:false});
rz.addEventListener('touchstart',rstart,{passive:false});rzl.addEventListener('touchstart',rlstart,{passive:false});
rztl.addEventListener('touchstart',rtlstart,{passive:false});rztr.addEventListener('touchstart',rtrstart,{passive:false});
document.addEventListener('touchmove',function(e){dmove(e);rmove(e);rlmove(e);rtlmove(e);rtrmove(e)},{passive:false});
document.addEventListener('touchend',function(){dend();rend();rlend();rtlend();rtrend()});
function edgeResize(el,ed){if(!el)return;var st=null;function start(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();st={w:r.width,h:r.height,l:r.left,t:r.top,x:gxy(e).x,y:gxy(e).y};fr.style.pointerEvents='none'}function move(e){if(!st)return;e.preventDefault();var p=gxy(e),dx=p.x-st.x,dy=p.y-st.y,nw=st.w,nh=st.h,nl=st.l,nt=st.t;if(ed.e)nw=Math.max(180,Math.min(st.w+dx,innerWidth-20));if(ed.w){nw=Math.max(180,Math.min(st.w-dx,innerWidth-20));nl=st.l+(st.w-nw)}if(ed.s)nh=Math.max(120,Math.min(st.h+dy,innerHeight-20));if(ed.n){nh=Math.max(120,Math.min(st.h-dy,innerHeight-20));nt=st.t+(st.h-nh)}box.style.width=nw+'px';box.style.height=nh+'px';box.style.left=nl+'px';box.style.top=nt+'px'}function end(){if(!st)return;st=null;fr.style.pointerEvents=''}el.addEventListener('mousedown',start);el.addEventListener('touchstart',start,{passive:false});document.addEventListener('mousemove',move);document.addEventListener('mouseup',end);document.addEventListener('touchmove',move,{passive:false});document.addEventListener('touchend',end)}
edgeResize(document.getElementById('yt-rn'),{n:1});edgeResize(document.getElementById('yt-rs'),{s:1});edgeResize(document.getElementById('yt-re'),{e:1});edgeResize(document.getElementById('yt-rw'),{w:1});
var sn=document.getElementById('sn'),snList=document.getElementById('sn-list'),snTop=document.getElementById('sn-top'),snPrev=document.getElementById('sn-prev'),snNext=document.getElementById('sn-next'),snMenu=document.getElementById('sn-menu');
if(sn){var sections=Array.prototype.slice.call(document.querySelectorAll('h2'));sections.forEach(function(h,i){if(!h.id)h.id='sec-'+i;var a=document.createElement('a');var txt=h.textContent.replace(/\s*\d+:\d+(?::\d+)?\s*$/,'').trim();a.href='#'+h.id;a.textContent=txt;a.setAttribute('role','menuitem');a.addEventListener('click',function(){setTimeout(function(){snList.classList.remove('open');snMenu.classList.remove('on');sn.classList.remove('open')},60)});snList.appendChild(a)});
function closeMenu(){snList.classList.remove('open');snMenu.classList.remove('on');sn.classList.remove('open')}
function curSec(){var y=window.scrollY+150,idx=0;for(var i=0;i<sections.length;i++){if(sections[i].offsetTop<=y)idx=i;else break}return idx}
snTop.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'})});
snPrev.addEventListener('click',function(){var y=window.scrollY;for(var i=sections.length-1;i>=0;i--){if(sections[i].offsetTop<y-50){sections[i].scrollIntoView({behavior:'smooth',block:'start'});return}}window.scrollTo({top:0,behavior:'smooth'})});
snNext.addEventListener('click',function(){var y=window.scrollY;for(var i=0;i<sections.length;i++){if(sections[i].offsetTop>y+50){sections[i].scrollIntoView({behavior:'smooth',block:'start'});return}}});
function posSnList(){var r=sn.getBoundingClientRect();var pillCx=r.left+r.width/2;var onRight=pillCx<innerWidth/2;snList.classList.toggle('on-right',onRight);snList.classList.toggle('on-left',!onRight)}snMenu.addEventListener('click',function(e){e.stopPropagation();var o=!snList.classList.contains('open');snList.classList.toggle('open',o);snMenu.classList.toggle('on',o);sn.classList.toggle('open',o);if(o)posSnList()});window.addEventListener('resize',function(){if(snList.classList.contains('open'))posSnList()});window.addEventListener('scroll',function(){if(snList.classList.contains('open'))posSnList()},{passive:true});
document.addEventListener('click',function(e){if(!snList.contains(e.target)&&!sn.contains(e.target))closeMenu()});
function secName(i){return sections[i]?sections[i].textContent.replace(/\s*\d+:\d+(?::\d+)?\s*$/,'').trim():''}
function updAct(){var i=curSec();Array.prototype.forEach.call(snList.querySelectorAll('a'),function(a,j){a.classList.toggle('on',j===i)});var p=Math.max(0,i-1),n=Math.min(sections.length-1,i+1);if(snPrev)snPrev.setAttribute('data-tip',i>0?'Poprzednia sekcja: '+secName(p):'Przewi\u0144 na g\u00f3r\u0119');if(snNext)snNext.setAttribute('data-tip',i<sections.length-1?'Nast\u0119pna sekcja: '+secName(n):'Koniec strony')}
window.addEventListener('scroll',updAct,{passive:true});updAct();
var snGrip=document.getElementById('sn-grip'),snRst=document.getElementById('sn-rst');
var snD=null;
function snStart(e){e.preventDefault();e.stopPropagation();var p=gxy(e),r=sn.getBoundingClientRect(),ct=parseFloat(getComputedStyle(sn).top)||0;snD={ox:p.x-r.left,oy:p.y-r.top,shift:r.top-ct};sn.style.transition='none'}
function snMove(e){if(!snD)return;e.preventDefault();var p=gxy(e);sn.classList.add('moved');sn.style.right='auto';sn.style.left=Math.max(4,Math.min(p.x-snD.ox,innerWidth-sn.offsetWidth-4))+'px';var vt=Math.max(4,Math.min(p.y-snD.oy,innerHeight-sn.offsetHeight-4));sn.style.top=(vt-snD.shift)+'px';if(snList.classList.contains('open'))posSnList()}
function snEnd(){if(!snD)return;snD=null;sn.style.transition=''}
if(snGrip){snGrip.addEventListener('mousedown',snStart);snGrip.addEventListener('touchstart',snStart,{passive:false})}
document.addEventListener('mousemove',snMove);document.addEventListener('mouseup',snEnd);
document.addEventListener('touchmove',snMove,{passive:false});document.addEventListener('touchend',snEnd);
if(snRst)snRst.addEventListener('click',function(e){e.stopPropagation();sn.style.left='';sn.style.top='';sn.style.right='';sn.classList.remove('moved')});var _bpMq=matchMedia('(max-width:1099px)');function _bpReset(){sn.style.left='';sn.style.top='';sn.style.right='';sn.classList.remove('moved','open');var bx=document.getElementById('yt-box');if(bx){bx.style.left='';bx.style.top='';bx.style.right='';bx.style.bottom='';bx.style.width='';bx.style.height='';bx.classList.remove('dragged')}}if(_bpMq.addEventListener)_bpMq.addEventListener('change',_bpReset);else _bpMq.addListener(_bpReset)}
})();
