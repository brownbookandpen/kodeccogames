// Local preview helper. When the site is opened straight from disk (file://),
// folder links like "game/" show a directory listing instead of the page.
// This sends them to "game/index.html". Does nothing on the real website.
if (location.protocol === 'file:') {
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var h = a.getAttribute('href');
    if (/^([a-z]+:|#)/i.test(h)) return;
    var i = h.indexOf('#'), path = i < 0 ? h : h.slice(0, i), hash = i < 0 ? '' : h.slice(i);
    if (!path || path.slice(-1) !== '/') return;
    e.preventDefault();
    location.href = path + 'index.html' + hash;
  });
}
