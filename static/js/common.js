// 克孜尔石窟壁画智慧修复全生命周期管理系统 - 公共JavaScript文件

// 全局配置
const API_BASE_URL = '/api';
let currentUser = null;
let authToken = null;

// 工具函数
const utils = {
    // 格式化日期
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // 格式化文件大小
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // 生成状态标签
    getStatusBadge: function(status) {
        const statusMap = {
            'draft': { text: '草稿', class: 'status-draft' },
            'running': { text: '进行中', class: 'status-running' },
            'finished': { text: '已完成', class: 'status-finished' },
            'paused': { text: '已暂停', class: 'status-paused' },
            'revoked': { text: '已撤销', class: 'status-revoked' },
            'pending': { text: '待审批', class: 'badge-warning' },
            'approved': { text: '已批准', class: 'badge-success' },
            'rejected': { text: '已拒绝', class: 'badge-danger' }
        };
        
        const statusInfo = statusMap[status] || { text: status, class: 'badge-secondary' };
        return `<span class="badge ${statusInfo.class}">${statusInfo.text}</span>`;
    },

    // 显示toast消息
    showToast: function(message, type = 'info') {
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close">&times;</button>
            </div>
        `;

        // 添加toast样式（如果不存在）
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    min-width: 300px;
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transform: translateX(400px);
                    transition: transform 0.3s ease;
                }
                .toast.show { transform: translateX(0); }
                .toast-success { background: #28a745; }
                .toast-error { background: #dc3545; }
                .toast-warning { background: #ffc107; color: #212529; }
                .toast-info { background: #17a2b8; }
                .toast-content { display: flex; justify-content: space-between; align-items: center; }
                .toast-close { background: none; border: none; color: inherit; font-size: 18px; cursor: pointer; }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);

        // 显示toast
        setTimeout(() => toast.classList.add('show'), 100);

        // 关闭按钮事件
        toast.querySelector('.toast-close').onclick = () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        };

        // 自动关闭
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    },

    // 获取当前用户信息
    getCurrentUser: function() {
        return currentUser;
    },

    // 创建模态框
    createModal: function(title, content, onConfirm, onCancel) {
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="close" onclick="this.closest('.modal').remove()">
                        <span>&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                    <button class="btn btn-secondary cancel-btn">取消</button>
                    <button class="btn btn-primary confirm-btn">确认</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        if (onConfirm) {
            modal.querySelector('.confirm-btn').onclick = () => {
                modal.remove();
                onConfirm();
            };
        }

        if (onCancel) {
            modal.querySelector('.cancel-btn').onclick = () => {
                modal.remove();
                onCancel();
            };
        }

        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
                if (onCancel) onCancel();
            }
        };

        return modal;
    },

    // 显示确认对话框
    confirm: function(message, onConfirm, onCancel) {
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 400px;">
                <div class="modal-header">
                    <h5 class="modal-title">确认操作</h5>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                    <button class="btn btn-secondary cancel-btn">取消</button>
                    <button class="btn btn-primary confirm-btn">确认</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.confirm-btn').onclick = () => {
            modal.remove();
            if (onConfirm) onConfirm();
        };

        modal.querySelector('.cancel-btn').onclick = () => {
            modal.remove();
            if (onCancel) onCancel();
        };

        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
                if (onCancel) onCancel();
            }
        };
    }
};

// HTTP请求封装
const http = {
    // 通用请求方法
    request: async function(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // 添加认证头
        if (authToken) {
            config.headers['Authorization'] = `Bearer ${authToken}`;
        }

        try {
            const response = await fetch(API_BASE_URL + url, config);
            
            if (response.status === 401) {
                // Token过期，跳转到登录页
                this.logout();
                return null;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            utils.showToast(error.message, 'error');
            throw error;
        }
    },

    // GET请求
    get: function(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl);
    },

    // POST请求
    post: function(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT请求
    put: function(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE请求
    delete: function(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    },

    // 文件上传
    uploadFile: async function(file) {
        const formData = new FormData();
        formData.append('file', file);

        const config = {
            method: 'POST',
            body: formData,
            headers: {}
        };

        // 添加认证头
        if (authToken) {
            config.headers['Authorization'] = `Bearer ${authToken}`;
        }

        try {
            const response = await fetch(API_BASE_URL + '/upload', config);
            
            if (response.status === 401) {
                this.logout();
                return null;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            utils.showToast(error.message, 'error');
            throw error;
        }
    },

    // 登录
    login: async function(username, password) {
        try {
            const data = await this.post('/login', { username, password });
            authToken = data.access_token;
            currentUser = data.user;
            
            // 保存到localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            return data;
        } catch (error) {
            throw error;
        }
    },

    // 登出
    logout: function() {
        authToken = null;
        currentUser = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        window.location.href = '/';
    },

    // 检查登录状态
    checkAuth: function() {
        const token = localStorage.getItem('authToken');
        const user = localStorage.getItem('currentUser');
        
        if (token && user) {
            authToken = token;
            currentUser = JSON.parse(user);
            return true;
        }
        
        return false;
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    if (window.location.pathname !== '/' && !http.checkAuth()) {
        window.location.href = '/';
        return;
    }

    // 如果已登录且在登录页，跳转到主页
    if (window.location.pathname === '/' && http.checkAuth()) {
        window.location.href = '/static/index.html';
        return;
    }
});

// 文件拖拽上传功能
function initFileUpload(dropAreaId, fileInputId, onFileSelect) {
    const dropArea = document.getElementById(dropAreaId);
    const fileInput = document.getElementById(fileInputId);

    if (!dropArea || !fileInput) return;

    // 点击上传区域打开文件选择
    dropArea.addEventListener('click', () => fileInput.click());

    // 文件选择事件
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            onFileSelect(e.target.files[0]);
        }
    });

    // 拖拽事件
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'));
    });

    dropArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            onFileSelect(files[0]);
        }
    });
}

// 表格分页功能
function initPagination(data, itemsPerPage, renderFunction) {
    let currentPage = 1;
    const totalPages = Math.ceil(data.length / itemsPerPage);

    function render() {
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = data.slice(start, end);
        renderFunction(pageData);
        updatePaginationControls();
    }

    function updatePaginationControls() {
        const paginationContainer = document.querySelector('.pagination');
        if (!paginationContainer) return;

        let html = '';
        
        // 上一页
        html += `<button class="btn btn-secondary" ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">上一页</button>`;
        
        // 页码
        for (let i = 1; i <= totalPages; i++) {
            if (i === currentPage || i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                html += `<button class="btn ${i === currentPage ? 'btn-primary' : 'btn-secondary'}" onclick="changePage(${i})">${i}</button>`;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                html += '<span>...</span>';
            }
        }
        
        // 下一页
        html += `<button class="btn btn-secondary" ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">下一页</button>`;
        
        paginationContainer.innerHTML = html;
    }

    window.changePage = function(page) {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
            render();
        }
    };

    render();
    return { render, changePage: window.changePage };
}




