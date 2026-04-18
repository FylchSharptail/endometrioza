(function(){var C=[[0,'Dr Thaïs Aliabadi — wstęp'],[176,'Dlaczego endometrioza i PCOS nie są diagnozowane'],[496,'Niepłodność — wczesne badania'],[654,'Reklama'],[847,'Luka w edukacji zdrowotnej kobiet'],[924,'PCOS: objawy, diagnostyka, AMH'],[1288,'Nieregularne miesiączki, PCOS u nastolatek'],[1476,'Diagnostyka, USG miednicy; nazwa PCOS'],[1669,'Przerzedzanie włosów, trądzik; 4 fenotypy PCOS'],[2154,'Filary PCOS: oś HPA, androgeny, owulacja'],[2430,'Insulinooporność, tłuszcz trzewny, stan zapalny'],[2790,'Reklama'],[2950,'PCOS: stan zapalny, genetyka, styl życia'],[3151,'PCOS i płodność, zamrażanie jajeczek'],[3514,'Edukacja zdrowotna, AI; analogia z zaćmą'],[3680,'Leczenie PCOS: antykoncepcja, metformina'],[4004,'Suplementy, styl życia, GLP-1'],[4352,'Berberyna, metformina; GLP-1, alkohol'],[4753,'Recepty w PCOS; współwystępowanie z endometriozą'],[4916,'Reklama'],[4996,'Zamrażanie jajeczek, jakość jajeczek'],[5522,'Kluczowe wnioski PCOS'],[5763,'Niezdiagnozowana endometrioza a płodność'],[5966,'Endometrioza: objawy, diagnostyka'],[6150,'Zdrowie mężczyzn vs kobiet'],[6421,'Stan zapalny, implanty ektopowe, ból miednicy'],[6636,'Jakość jajeczek, endometrioza, AMH'],[6869,'Reklama'],[6973,'Badania, objawy endometriozy, testy'],[7292,'Leczenie: chirurgia, typy endometriozy'],[7522,'Przyczyny endometriozy, stan zapalny'],[7918,'Ginekologia vs położnictwo'],[8160,'Wnioski: leczenie endometriozy'],[8224,'Estrogen, progesteron, antagoniści GnRH'],[8559,'Stadium a ból, typy endometriozy'],[8629,'Ciąża, menopauza, depresja poporodowa'],[8995,'Torbiele, mięśniaki, USG'],[9245,'Ocena płodności; autoimmunologia'],[9471,'Rak piersi: kalkulator ryzyka, badania'],[10187,'Autoimmunologia, mgła mózgowa, inozytol'],[10386,'PMDD, post, dieta niskowęglowodanowa'],[10641,'Wypadanie włosów, perimenopauza'],[10840,'Progesteron, hormony, menopauza'],[11094,'Zakończenie']];
var CD=C.slice().sort(function(a,b){return b[0]-a[0]});
function getCh(t){for(var i=0;i<CD.length;i++)if(t>=CD[i][0])return CD[i][1];return''}
function getIdx(t){for(var i=C.length-1;i>=0;i--)if(t>=C[i][0])return i;return 0}
function fmt(s){s=Math.max(0,s|0);var h=s/3600|0,m=(s%3600)/60|0,x=s%60;return(h?h+':'+(m<10?'0':''):'')+m+':'+(x<10?'0':'')+x}
var box=document.getElementById('yt-box'),drag=document.getElementById('yt-drag'),rz=document.getElementById('yt-rz'),rzl=document.getElementById('yt-rzl'),rztl=document.getElementById('yt-rztl'),rztr=document.getElementById('yt-rztr'),rst=document.getElementById('yt-reset'),fr=document.getElementById('yt-player'),sub=document.getElementById('yt-subs');
var acTitle=document.querySelector('#yt-audio-ctrl .ac-title'),acCur=document.querySelector('#yt-audio-ctrl .ac-cur'),acDur=document.querySelector('#yt-audio-ctrl .ac-dur'),acBar=document.querySelector('#yt-audio-ctrl .ac-bar'),acProg=document.querySelector('#yt-audio-ctrl .ac-prog'),acPlay=document.getElementById('ac-play'),acPrev=document.getElementById('ac-prev'),acNext=document.getElementById('ac-next');
function cmd(fn,a){fr.contentWindow.postMessage(JSON.stringify({event:'command',func:fn,args:a||[]}),'https://www.youtube.com')}
document.addEventListener('click',function(e){var t=e.target.closest('.ts');if(!t)return;e.preventDefault();var sec=parseInt(t.getAttribute('data-t'),10);if(isNaN(sec))return;cmd('seekTo',[sec,!0]);cmd('playVideo');if(window.innerWidth<1100)fr.scrollIntoView({behavior:'smooth',block:'end'})});
var last='',subTimer,curT=0,dur=0,playing=false;
window.addEventListener('message',function(e){if(e.origin.indexOf('youtube.com')===-1)return;var d;try{d=JSON.parse(e.data)}catch(_){return}if(d.event==='infoDelivery'&&d.info){if(typeof d.info.currentTime==='number'){curT=d.info.currentTime;var ch=getCh(curT);if(ch!==last){sub.textContent=ch;if(acTitle)acTitle.textContent=ch;last=ch;sub.classList.remove('fade');clearTimeout(subTimer);subTimer=setTimeout(function(){sub.classList.add('fade')},5000)}if(acCur)acCur.textContent=fmt(curT);if(dur>0&&acBar)acBar.style.width=(curT/dur*100)+'%'}if(typeof d.info.duration==='number'&&d.info.duration>0&&d.info.duration!==dur){dur=d.info.duration;if(acDur)acDur.textContent=fmt(dur)}if(typeof d.info.playerState==='number'){playing=(d.info.playerState===1);if(acPlay)acPlay.textContent=playing?'⏸':'▶'}}if(d.event==='onStateChange'){playing=(d.info===1);if(acPlay)acPlay.textContent=playing?'⏸':'▶'}});
fr.addEventListener('load',function(){fr.contentWindow.postMessage(JSON.stringify({event:'listening'}),'*');cmd('addEventListener',['onStateChange'])});
if(acPlay)acPlay.addEventListener('click',function(e){e.stopPropagation();cmd(playing?'pauseVideo':'playVideo')});
if(acPrev)acPrev.addEventListener('click',function(e){e.stopPropagation();var i=getIdx(curT-2);i=Math.max(0,i-1);cmd('seekTo',[C[i][0],!0]);cmd('playVideo')});
if(acNext)acNext.addEventListener('click',function(e){e.stopPropagation();var i=getIdx(curT);i=Math.min(C.length-1,i+1);cmd('seekTo',[C[i][0],!0]);cmd('playVideo')});
if(acProg)acProg.addEventListener('click',function(e){if(!dur)return;var r=acProg.getBoundingClientRect();var p=(e.clientX-r.left)/r.width;cmd('seekTo',[p*dur,!0])});
function gxy(e){var t=e.touches?e.touches[0]:e;return{x:t.clientX,y:t.clientY}}
function promote(){if(box.classList.contains('dragged'))return;var r=box.getBoundingClientRect();box.classList.add('dragged');box.style.width=r.width+'px';box.style.height=r.height+'px';box.style.left=r.left+'px';box.style.top=r.top+'px'}
var ds=null;
function dstart(e){if(e.target.closest('#yt-reset,#yt-hide,#yt-audio'))return;e.preventDefault();var p=gxy(e),r=box.getBoundingClientRect();ds={ox:p.x-r.left,oy:p.y-r.top};fr.style.pointerEvents='none'}
function dmove(e){if(!ds)return;e.preventDefault();var p=gxy(e);if(!box.classList.contains('dragged')){box.classList.add('dragged');box.style.width=box.offsetWidth+'px'}box.style.left=Math.max(0,Math.min(p.x-ds.ox,innerWidth-80))+'px';box.style.top=Math.max(0,Math.min(p.y-ds.oy,innerHeight-40))+'px'}
function dend(){if(!ds)return;ds=null;fr.style.pointerEvents=''}
var rs=null;
function rstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rs={sw:r.width,sh:r.height,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rmove(e){if(!rs)return;e.preventDefault();var p=gxy(e);box.style.width=Math.max(160,Math.min(rs.sw+(p.x-rs.sx),innerWidth-20))+'px';box.style.height=Math.max(120,Math.min(rs.sh+(p.y-rs.sy),innerHeight-20))+'px'}
function rend(){if(!rs)return;rs=null;fr.style.pointerEvents=''}
var rsl=null;
function rlstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rsl={sw:r.width,sh:r.height,sl:r.left,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rlmove(e){if(!rsl)return;e.preventDefault();var p=gxy(e);var dx=p.x-rsl.sx;var nw=Math.max(160,Math.min(rsl.sw-dx,innerWidth-20));var nh=Math.max(120,Math.min(rsl.sh+(p.y-rsl.sy),innerHeight-20));box.style.width=nw+'px';box.style.height=nh+'px';box.style.left=(rsl.sl+(rsl.sw-nw))+'px'}
function rlend(){if(!rsl)return;rsl=null;fr.style.pointerEvents=''}
var rstr=null;
function rtrstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rstr={sw:r.width,sh:r.height,st:r.top,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rtrmove(e){if(!rstr)return;e.preventDefault();var p=gxy(e);var dy=p.y-rstr.sy;var nw=Math.max(160,Math.min(rstr.sw+(p.x-rstr.sx),innerWidth-20));var nh=Math.max(120,Math.min(rstr.sh-dy,innerHeight-20));box.style.width=nw+'px';box.style.height=nh+'px';box.style.top=(rstr.st+(rstr.sh-nh))+'px'}
function rtrend(){if(!rstr)return;rstr=null;fr.style.pointerEvents=''}
var rstl=null;
function rtlstart(e){e.preventDefault();e.stopPropagation();promote();var r=box.getBoundingClientRect();rstl={sw:r.width,sh:r.height,sl:r.left,st:r.top,sx:gxy(e).x,sy:gxy(e).y};fr.style.pointerEvents='none'}
function rtlmove(e){if(!rstl)return;e.preventDefault();var p=gxy(e);var dx=p.x-rstl.sx;var dy=p.y-rstl.sy;var nw=Math.max(160,Math.min(rstl.sw-dx,innerWidth-20));var nh=Math.max(120,Math.min(rstl.sh-dy,innerHeight-20));box.style.width=nw+'px';box.style.height=nh+'px';box.style.left=(rstl.sl+(rstl.sw-nw))+'px';box.style.top=(rstl.st+(rstl.sh-nh))+'px'}
function rtlend(){if(!rstl)return;rstl=null;fr.style.pointerEvents=''}
function reset(){box.classList.remove('dragged');box.style.left='';box.style.top='';box.style.width='';box.style.height=''}
var hideBtn=document.getElementById('yt-hide'),showBtn=document.getElementById('yt-show');
function hide(){box.classList.add('hidden');showBtn.classList.add('on')}
function show(){box.classList.remove('hidden');showBtn.classList.remove('on')}
hideBtn.addEventListener('click',function(e){e.stopPropagation();hide()});
showBtn.addEventListener('click',show);
var audioBtn=document.getElementById('yt-audio');
audioBtn.addEventListener('click',function(e){e.stopPropagation();box.classList.toggle('audio')});
var idleTimer;function sleep(){box.classList.add('idle')}
function wake(){box.classList.remove('idle');clearTimeout(idleTimer);idleTimer=setTimeout(sleep,5000)}
box.addEventListener('mouseenter',wake);box.addEventListener('mousemove',wake);
box.addEventListener('mouseleave',function(){clearTimeout(idleTimer);idleTimer=setTimeout(sleep,5000)});
box.addEventListener('touchstart',wake,{passive:true});wake();
drag.addEventListener('dblclick',reset);rst.addEventListener('click',reset);
drag.addEventListener('mousedown',dstart);
rz.addEventListener('mousedown',rstart);rzl.addEventListener('mousedown',rlstart);
rztl.addEventListener('mousedown',rtlstart);rztr.addEventListener('mousedown',rtrstart);
document.addEventListener('mousemove',function(e){dmove(e);rmove(e);rlmove(e);rtlmove(e);rtrmove(e)});
document.addEventListener('mouseup',function(){dend();rend();rlend();rtlend();rtrend()});
drag.addEventListener('touchstart',dstart,{passive:false});
rz.addEventListener('touchstart',rstart,{passive:false});rzl.addEventListener('touchstart',rlstart,{passive:false});
rztl.addEventListener('touchstart',rtlstart,{passive:false});rztr.addEventListener('touchstart',rtrstart,{passive:false});
document.addEventListener('touchmove',function(e){dmove(e);rmove(e);rlmove(e);rtlmove(e);rtrmove(e)},{passive:false});
document.addEventListener('touchend',function(){dend();rend();rlend();rtlend();rtrend()})
})();
