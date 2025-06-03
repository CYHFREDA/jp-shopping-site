// 清緩存工具函數
export const clearCache = {
  // 動態時間戳
  timestamp: Date.now(),

  // 清除 localStorage
  clearLocalStorage() {
    localStorage.clear();
  },

  // 清除 sessionStorage
  clearSessionStorage() {
    sessionStorage.clear();
  },

  // 清除所有緩存
  clearAll() {
    this.clearLocalStorage();
    this.clearSessionStorage();
    // 清除瀏覽器緩存
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
        });
      });
    }
  },

  // 清除特定鍵的緩存
  clearItem(key) {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  },

  // 清除過期的緩存
  clearExpired() {
    const now = Date.now();
    // 檢查 localStorage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      try {
        const item = JSON.parse(localStorage.getItem(key));
        if (item && item.expireAt && item.expireAt < now) {
          localStorage.removeItem(key);
        }
      } catch (e) {
        // 如果不是 JSON 格式，跳過
        continue;
      }
    }
  },

  // 更新資源版本
  updateResourceVersion() {
    // 更新 CSS 文件版本
    document.querySelectorAll('link[data-href]').forEach(link => {
      link.href = link.getAttribute('data-href') + '?v=' + this.timestamp;
    });

    // 更新 JS 文件版本
    document.querySelectorAll('script[data-src]').forEach(script => {
      if (!script.src.includes('cache-busting.js')) {
        script.src = script.getAttribute('data-src') + '?v=' + this.timestamp;
      }
    });
  },

  // 初始化緩存清理
  init() {
    // 清除過期緩存
    this.clearExpired();
    // 更新資源版本
    this.updateResourceVersion();
  }
}; 