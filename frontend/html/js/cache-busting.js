// 動態時間戳
const timestamp = Date.now();
document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
  link.href = link.href + '?v=' + timestamp;
});
document.querySelectorAll('script[src]').forEach(script => {
  if (!script.src.includes('cache-busting.js')) {
    script.src = script.src + '?v=' + timestamp;
  }
});