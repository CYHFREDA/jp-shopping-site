// 動態時間戳
const timestamp = Date.now();

document.querySelectorAll('link[data-href]').forEach(link => {
  link.href = link.getAttribute('data-href') + '?v=' + timestamp;
});

document.querySelectorAll('script[data-src]').forEach(script => {
  if (!script.src.includes('cache-busting.js')) {
    script.src = script.getAttribute('data-src') + '?v=' + timestamp;
  }
});