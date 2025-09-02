/**
 * Service Worker - 克孜尔石窟壁画智慧修复全生命周期管理系统
 * 提供离线支持和资源缓存
 */

const CACHE_NAME = 'kizil-restoration-v2.0.0';
const CACHE_URLS = [
  // 核心页面
  '/static/index-new.html',
  '/static/login-new.html',
  
  // CSS资源
  '/static/assets/css/variables.css',
  '/static/assets/css/base.css',
  '/static/assets/css/components.css',
  '/static/assets/css/layout.css',
  '/static/assets/css/animations.css',
  
  // JavaScript模块
  '/static/assets/js/modules/ui.js',
  '/static/assets/js/modules/api.js',
  '/static/assets/js/modules/app.js',
  
  // 图标和字体（如果存在）
  '/static/assets/images/favicon.svg',
  '/static/assets/images/favicon.png'
];

// 安装事件 - 缓存资源
self.addEventListener('install', (event) => {
  console.log('[SW] 安装中...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] 缓存资源...');
        return cache.addAll(CACHE_URLS);
      })
      .then(() => {
        console.log('[SW] 安装完成');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] 安装失败:', error);
      })
  );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
  console.log('[SW] 激活中...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('[SW] 删除旧缓存:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] 激活完成');
        return self.clients.claim();
      })
  );
});

// 拦截请求 - 缓存策略
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // 只处理同源请求
  if (url.origin !== location.origin) {
    return;
  }
  
  // API请求使用网络优先策略
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
  }
  // 静态资源使用缓存优先策略
  else if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(request));
  }
  // 页面请求使用网络优先策略
  else {
    event.respondWith(networkFirst(request));
  }
});

/**
 * 缓存优先策略 - 适用于静态资源
 */
async function cacheFirst(request) {
  try {
    // 先从缓存中查找
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 缓存中没有，从网络获取
    const networkResponse = await fetch(request);
    
    // 缓存成功的响应
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] 缓存优先策略失败:', error);
    
    // 返回离线页面或默认响应
    if (request.destination === 'document') {
      return caches.match('/static/offline.html') || 
             new Response('离线模式，请检查网络连接', { 
               status: 503, 
               statusText: 'Service Unavailable' 
             });
    }
    
    throw error;
  }
}

/**
 * 网络优先策略 - 适用于API和页面请求
 */
async function networkFirst(request) {
  try {
    // 先尝试网络请求
    const networkResponse = await fetch(request);
    
    // 缓存成功的响应
    if (networkResponse.ok && request.method === 'GET') {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] 网络请求失败:', error);
    
    // 网络失败，尝试从缓存获取
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 缓存中也没有，返回错误响应
    if (request.destination === 'document') {
      return caches.match('/static/offline.html') || 
             new Response('网络连接失败，请稍后重试', { 
               status: 503, 
               statusText: 'Service Unavailable' 
             });
    }
    
    throw error;
  }
}

// 消息处理 - 与主线程通信
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_NAME });
      break;
      
    case 'CLEAR_CACHE':
      caches.delete(CACHE_NAME).then(() => {
        event.ports[0].postMessage({ success: true });
      });
      break;
      
    default:
      console.log('[SW] 未知消息类型:', type);
  }
});

// 后台同步 - 离线时的数据同步
self.addEventListener('sync', (event) => {
  console.log('[SW] 后台同步:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

/**
 * 执行后台同步
 */
async function doBackgroundSync() {
  try {
    // 这里可以实现离线数据的同步逻辑
    console.log('[SW] 执行后台同步...');
    
    // 示例：同步离线时保存的表单数据
    const offlineData = await getOfflineData();
    if (offlineData.length > 0) {
      for (const data of offlineData) {
        await syncData(data);
      }
      await clearOfflineData();
    }
    
    console.log('[SW] 后台同步完成');
  } catch (error) {
    console.error('[SW] 后台同步失败:', error);
  }
}

/**
 * 获取离线数据
 */
async function getOfflineData() {
  // 这里应该从IndexedDB或其他存储中获取离线数据
  return [];
}

/**
 * 同步数据到服务器
 */
async function syncData(data) {
  try {
    const response = await fetch('/api/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error('同步失败');
    }
    
    return response.json();
  } catch (error) {
    console.error('[SW] 数据同步失败:', error);
    throw error;
  }
}

/**
 * 清理离线数据
 */
async function clearOfflineData() {
  // 这里应该清理已同步的离线数据
  console.log('[SW] 清理离线数据');
}

// 推送通知处理
self.addEventListener('push', (event) => {
  console.log('[SW] 收到推送通知:', event);
  
  const options = {
    body: '您有新的工作流需要处理',
    icon: '/static/assets/images/icon-192.png',
    badge: '/static/assets/images/badge-72.png',
    tag: 'workflow-notification',
    data: {
      url: '/static/index-new.html'
    },
    actions: [
      {
        action: 'view',
        title: '查看详情',
        icon: '/static/assets/images/view-icon.png'
      },
      {
        action: 'dismiss',
        title: '忽略',
        icon: '/static/assets/images/dismiss-icon.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('克孜尔修复系统', options)
  );
});

// 通知点击处理
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] 通知点击:', event);
  
  event.notification.close();
  
  const { action, data } = event;
  
  if (action === 'view' || !action) {
    event.waitUntil(
      clients.openWindow(data?.url || '/static/index-new.html')
    );
  }
});

// 错误处理
self.addEventListener('error', (event) => {
  console.error('[SW] Service Worker错误:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('[SW] 未处理的Promise拒绝:', event.reason);
});

console.log('[SW] Service Worker已加载');
