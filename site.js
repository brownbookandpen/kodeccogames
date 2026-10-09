// Shared behaviour for the hub and the Unity pages.
(function(){
  var h = document.querySelector('.site-header');
  if (h) { var on = function(){ h.classList.toggle('scrolled', window.scrollY > 8); }; on(); addEventListener('scroll', on, {passive:true}); }
  var els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) { els.forEach(function(e){ e.classList.add('in'); }); return; }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {rootMargin:'0px 0px -8% 0px'});
  els.forEach(function(e){ io.observe(e); });
})();
