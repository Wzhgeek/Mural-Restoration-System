// 主应用JavaScript文件
// 作者：王梓涵 (wangzh011031@163.com)
// 创建时间：2025年

let dashboardData = null;
let currentWorkflows = [];

// 主题管理
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme-mode') || 'light';
        this.init();
    }

    init() {
        // 应用保存的主题
        this.applyTheme(this.currentTheme);
        
        // 创建主题切换按钮
        this.createThemeToggle();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('theme-mode', theme);
        localStorage.setItem('theme-mode', theme);
        this.currentTheme = theme;
        
        // 更新主题切换按钮图标
        this.updateToggleIcon();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    createThemeToggle() {
        // 在导航栏用户信息区域添加主题切换按钮
        const userInfo = document.querySelector('.navbar-user');
        if (userInfo) {
            const themeToggle = document.createElement('button');
            themeToggle.id = 'theme-toggle';
            themeToggle.className = 'btn btn-secondary';
            themeToggle.style.cssText = `
                padding: 8px 12px;
                border: none;
                border-radius: var(--td-radius-medium);
                background: var(--td-bg-color-component);
                color: var(--td-text-color-primary);
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 14px;
            `;
            
            themeToggle.addEventListener('click', () => this.toggleTheme());
            themeToggle.addEventListener('mouseenter', () => {
                themeToggle.style.background = 'var(--td-bg-color-component-hover)';
            });
            themeToggle.addEventListener('mouseleave', () => {
                themeToggle.style.background = 'var(--td-bg-color-component)';
            });
            
            // 插入到用户信息前面
            userInfo.insertBefore(themeToggle, userInfo.firstChild);
            
            this.toggleButton = themeToggle;
            this.updateToggleIcon();
        }
    }

    updateToggleIcon() {
        if (this.toggleButton) {
            const icon = this.currentTheme === 'light' ? '🌙' : '☀️';
            const text = this.currentTheme === 'light' ? '暗色' : '亮色';
            this.toggleButton.innerHTML = `${icon} ${text}`;
        }
    }
}

// 初始化主题管理器
let themeManager;

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化主题管理器
    themeManager = new ThemeManager();
    
    // 检查登录状态
    if (!http.checkAuth()) {
        window.location.href = '/';
        return;
    }

    initUserInterface();
    loadDashboard();
});

// 在页面加载前就应用主题，避免闪烁
(function() {
    const savedTheme = localStorage.getItem('theme-mode') || 'light';
    document.documentElement.setAttribute('theme-mode', savedTheme);
})();

// 初始化用户界面
function initUserInterface() {
    // 获取当前用户信息
    const user = utils.getCurrentUser();
    if (!user) {
        console.error('用户信息未加载，currentUser为空');
        return;
    }

    console.log('当前用户信息:', user);
    console.log('用户角色键:', user.role_key);

    // 设置用户信息
    document.getElementById('userName').textContent = user.full_name;
    document.getElementById('userRole').textContent = user.role_name;
    document.getElementById('userAvatar').textContent = user.full_name.charAt(0);

    // 根据角色显示/隐藏菜单
    const role = user.role_key;
    
    if (role === 'admin') {
        // 管理员可以看到所有菜单
        document.getElementById('nav-restoration').classList.remove('hidden');
        document.getElementById('nav-evaluation').classList.remove('hidden');
        document.getElementById('nav-management').classList.remove('hidden');
        document.getElementById('nav-rollback-history').classList.remove('hidden');
        document.getElementById('nav-evaluation-history').classList.remove('hidden');
        // 显示管理员控制按钮
        showAdminControls();
    } else if (role === 'restorer') {
        // 修复专家只能看到修复菜单和回溯历史
        document.getElementById('nav-restoration').classList.remove('hidden');
        document.getElementById('nav-rollback-history').classList.remove('hidden');
    } else if (role === 'evaluator') {
        // 评估专家只能看到评估菜单和评估历史
        document.getElementById('nav-evaluation').classList.remove('hidden');
        document.getElementById('nav-evaluation-history').classList.remove('hidden');
    }
}

// 页面切换
function showPage(pageId) {
    // 隐藏所有页面
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.add('hidden');
    });

    // 移除所有导航活动状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // 显示目标页面
    const targetPage = document.getElementById(`page-${pageId}`);
    if (!targetPage) {
        console.error(`页面元素不存在: page-${pageId}`);
        utils.showToast(`页面不存在: ${pageId}`, 'error');
        return;
    }
    targetPage.classList.remove('hidden');
    
    // 设置导航活动状态
    const navLink = document.querySelector(`[data-page="${pageId}"]`);
    if (navLink) {
        navLink.classList.add('active');
    }

    // 加载页面数据
    switch(pageId) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'restoration':
            loadWorkflows();
            break;
        case 'evaluation':
            loadEvaluationList();
            break;
        case 'management':
            // 显示管理员控制按钮
            console.log('切换到管理页面，准备显示管理员控制按钮');
            showAdminControls();
            loadAllWorkflows();
            loadRollbackRequests();
            break;
        case 'profile':
            loadProfile();
            break;
        case 'rollback-history':
            loadRollbackHistory();
            break;
        case 'evaluation-history':
            loadEvaluationHistory();
            break;
    }
}

// 加载仪表板数据
async function loadDashboard() {
    try {
        dashboardData = await http.get('/dashboard');
        renderDashboardStats();
        renderRecentActivities();
    } catch (error) {
        console.error('加载仪表板数据失败:', error);
    }
}

// 渲染仪表板统计
function renderDashboardStats() {
    if (!dashboardData) return;

    const statsContainer = document.getElementById('statsContainer');
    const userRole = utils.getCurrentUser()?.role_key;
    
    // 基础统计数据
    let stats = [];
    
    if (userRole === 'admin') {
        // 管理员看到全局统计
        stats = [
            { label: '总工作流', value: dashboardData.total_workflows, icon: '📊', trend: dashboardData.workflow_trend || 0 },
            { label: '进行中', value: dashboardData.running_workflows, icon: '🔄', color: 'primary' },
            { label: '已完成', value: dashboardData.finished_workflows, icon: '✅', color: 'success' },
            { label: '待评估', value: dashboardData.pending_evaluations, icon: '📋', color: 'warning' },
            { label: '待审批回溯', value: dashboardData.pending_rollbacks || 0, icon: '⏮️', color: 'info' },
            { label: '完成率', value: `${dashboardData.completion_rate || 0}%`, icon: '📈', color: 'success' }
        ];
    } else if (userRole === 'restorer') {
        // 修复专家看到个人相关统计
        stats = [
            { label: '我的工作流', value: dashboardData.my_workflows || 0, icon: '👤', color: 'primary' },
            { label: '进行中', value: dashboardData.my_running_workflows || 0, icon: '🔄', color: 'warning' },
            { label: '已完成', value: dashboardData.my_finished_workflows || 0, icon: '✅', color: 'success' },
            { label: '我的回溯申请', value: dashboardData.my_rollback_requests || 0, icon: '⏮️', color: 'info' },
            { label: '本月提交', value: dashboardData.monthly_submissions || 0, icon: '📅', color: 'secondary' },
            { label: '平均评分', value: `${dashboardData.average_score || 0}分`, icon: '⭐', color: 'warning' }
        ];
    } else if (userRole === 'evaluator') {
        // 评估专家看到评估相关统计
        stats = [
            { label: '待评估', value: dashboardData.pending_evaluations || 0, icon: '📋', color: 'warning' },
            { label: '已评估', value: dashboardData.completed_evaluations || 0, icon: '✅', color: 'success' },
            { label: '本月评估', value: dashboardData.monthly_evaluations || 0, icon: '📅', color: 'primary' },
            { label: '平均给分', value: `${dashboardData.average_given_score || 0}分`, icon: '⭐', color: 'info' },
            { label: '高分率', value: `${dashboardData.high_score_rate || 0}%`, icon: '🎯', color: 'success' },
            { label: '评估效率', value: `${dashboardData.evaluation_efficiency || 0}/天`, icon: '⚡', color: 'secondary' }
        ];
    }

    statsContainer.innerHTML = stats.map(stat => {
        const trendHtml = stat.trend !== undefined ? 
            `<div class="stat-trend ${stat.trend >= 0 ? 'positive' : 'negative'}">
                ${stat.trend >= 0 ? '↗' : '↘'} ${Math.abs(stat.trend)}%
            </div>` : '';
        
        return `
            <div class="stat-card ${stat.color ? 'stat-card-' + stat.color : ''}">
                <div class="stat-header">
                    <div class="stat-icon">${stat.icon}</div>
                    ${trendHtml}
                </div>
                <div class="stat-number">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            </div>
        `;
    }).join('');
    
    // 渲染图表（如果有数据）
    renderDashboardCharts();
}

// 渲染最近活动
function renderRecentActivities() {
    if (!dashboardData || !dashboardData.recent_activities) return;

    const activitiesContainer = document.getElementById('recentActivities');
    
    if (dashboardData.recent_activities.length === 0) {
        activitiesContainer.innerHTML = '<p class="text-center text-muted">暂无活动记录</p>';
        return;
    }

    const actionMap = {
        'submit': { text: '提交表单', icon: '📝', color: 'primary' },
        'rollback': { text: '回溯操作', icon: '⏮️', color: 'warning' },
        'finalize': { text: '设为最终方案', icon: '🎯', color: 'success' },
        'revoke': { text: '撤销操作', icon: '❌', color: 'danger' },
        'evaluate': { text: '评估完成', icon: '⭐', color: 'info' },
        'approve': { text: '审批通过', icon: '✅', color: 'success' },
        'reject': { text: '审批拒绝', icon: '❌', color: 'danger' }
    };

    activitiesContainer.innerHTML = `
        <div class="activity-list">
            ${dashboardData.recent_activities.map(activity => {
                const actionInfo = actionMap[activity.action] || { text: activity.action, icon: '📋', color: 'secondary' };
                return `
                    <div class="activity-item">
                        <div class="activity-icon activity-icon-${actionInfo.color}">
                            ${actionInfo.icon}
                        </div>
                        <div class="activity-content">
                            <div class="activity-main">
                                <strong>${activity.operator}</strong> 
                                <span class="activity-action">${actionInfo.text}</span>
                                ${activity.workflow_title ? `<span class="activity-target">「${activity.workflow_title}」</span>` : ''}
                            </div>
                            <div class="activity-time">${activity.time}</div>
                            ${activity.comment ? `<div class="activity-comment">${activity.comment}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// 从评估管理删除工作流（仅管理员）
async function deleteWorkflowFromEvaluation(workflowId) {
    try {
        if (!confirm('确定要删除这个工作流吗？此操作不可撤销！')) {
            return;
        }
        
        await http.delete(`/api/admin/workflows/${workflowId}`);
        utils.showToast('工作流删除成功', 'success');
        loadEvaluationList(); // 刷新列表
    } catch (error) {
        utils.showToast('删除失败: ' + error.message, 'error');
    }
}

// 渲染仪表盘图表
function renderDashboardCharts() {
    const userRole = utils.getCurrentUser()?.role_key;
    
    // 隐藏所有图表容器
    document.getElementById('trendChartCard').style.display = 'none';
    document.getElementById('scoreChartCard').style.display = 'none';
    document.getElementById('progressChartCard').style.display = 'none';
    
    // 渲染工作流趋势图
    if (dashboardData.workflow_trend_data && userRole === 'admin') {
        document.getElementById('trendChartCard').style.display = 'block';
        renderWorkflowTrendChart();
    }
    
    // 渲染评分分布图
    if (dashboardData.score_distribution && (userRole === 'admin' || userRole === 'evaluator')) {
        document.getElementById('scoreChartCard').style.display = 'block';
        renderScoreDistributionChart();
    }
    
    // 渲染个人进度图
    if (dashboardData.personal_progress && userRole === 'restorer') {
        document.getElementById('progressChartCard').style.display = 'block';
        renderPersonalProgressChart();
    }
}

// 渲染工作流趋势图（简化版）
function renderWorkflowTrendChart() {
    const chartContainer = document.getElementById('trendChart');
    if (!chartContainer || !dashboardData.workflow_trend_data) return;
    
    const data = dashboardData.workflow_trend_data;
    const maxValue = Math.max(...data.values);
    
    chartContainer.innerHTML = `
        <div class="chart-title">工作流趋势（最近7天）</div>
        <div class="simple-chart">
            ${data.labels.map((label, index) => {
                const height = (data.values[index] / maxValue) * 100;
                return `
                    <div class="chart-bar">
                        <div class="bar" style="height: ${height}%" title="${label}: ${data.values[index]}"></div>
                        <div class="bar-label">${label}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// 渲染评分分布图
function renderScoreDistributionChart() {
    const chartContainer = document.getElementById('scoreChart');
    if (!chartContainer || !dashboardData.score_distribution) return;
    
    const distribution = dashboardData.score_distribution;
    const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
    
    chartContainer.innerHTML = `
        <div class="chart-title">评分分布</div>
        <div class="score-distribution">
            ${Object.entries(distribution).map(([range, count]) => {
                const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;
                return `
                    <div class="score-range">
                        <div class="score-label">${range}分</div>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div class="score-count">${count} (${percentage}%)</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// 渲染个人进度图
function renderPersonalProgressChart() {
    const chartContainer = document.getElementById('progressChart');
    if (!chartContainer || !dashboardData.personal_progress) return;
    
    const progress = dashboardData.personal_progress;
    
    chartContainer.innerHTML = `
        <div class="chart-title">个人进度</div>
        <div class="progress-stats">
            <div class="progress-item">
                <div class="progress-label">本月目标完成率</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress.monthly_completion}%"></div>
                </div>
                <div class="progress-text">${progress.monthly_completion}%</div>
            </div>
            <div class="progress-item">
                <div class="progress-label">质量评分</div>
                <div class="progress-bar">
                    <div class="progress-fill score-bar" style="width: ${progress.quality_score}%"></div>
                </div>
                <div class="progress-text">${progress.quality_score}分</div>
            </div>
        </div>
    `;
}

// 加载工作流列表
async function loadWorkflows() {
    try {
        currentWorkflows = await http.get('/workflows');
        renderWorkflowsList('workflowsList', currentWorkflows);
    } catch (error) {
        console.error('加载工作流失败:', error);
        document.getElementById('workflowsList').innerHTML = '<p class="text-center text-danger">加载失败</p>';
    }
}

// 渲染工作流列表
function renderWorkflowsList(containerId, workflows) {
    const container = document.getElementById(containerId);
    const currentUser = utils.getCurrentUser();
    const isAdmin = currentUser?.role === 'admin';
    
    // 显示或隐藏删除按钮（仅在所有工作流页面）
    if (containerId === 'allWorkflowsList') {
        const deleteBtn = document.getElementById('deleteSelectedWorkflowBtn');
        if (deleteBtn) {
            deleteBtn.style.display = isAdmin ? 'inline-block' : 'none';
        }
    }
    
    if (workflows.length === 0) {
        container.innerHTML = '<p class="text-center">暂无工作流</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        ${isAdmin && containerId === 'allWorkflowsList' ? '<th><input type="checkbox" id="selectAllWorkflows" onchange="toggleAllWorkflows(this)"></th>' : ''}
                        <th>标题</th>
                        <th>发起人</th>
                        <th>当前步骤</th>
                        <th>状态</th>
                        <th>创建时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${workflows.map(workflow => `
                        <tr>
                            ${isAdmin && containerId === 'allWorkflowsList' ? `<td><input type="checkbox" name="allWorkflowSelect" value="${workflow.workflow_id}"></td>` : ''}
                            <td>${workflow.title}</td>
                            <td>${workflow.initiator_name}</td>
                            <td>第 ${workflow.current_step} 步</td>
                            <td>${utils.getStatusBadge(workflow.status)}</td>
                            <td>${utils.formatDate(workflow.created_at)}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="viewWorkflowDetails('${workflow.workflow_id}')">
                                    查看详情
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// 显示创建工作流模态框
function showCreateWorkflowModal() {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">创建新工作流</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <form id="createWorkflowForm">
                <div class="modal-body">
                    <div class="form-group">
                        <label for="workflowTitle">工作流标题</label>
                        <input type="text" class="form-control" id="workflowTitle" required>
                    </div>
                    <div class="form-group">
                        <label for="workflowDesc">描述</label>
                        <textarea class="form-control textarea" id="workflowDesc" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">取消</button>
                    <button type="submit" class="btn btn-primary">创建</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('createWorkflowForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const title = document.getElementById('workflowTitle').value.trim();
        const description = document.getElementById('workflowDesc').value.trim();

        if (!title) {
            utils.showToast('请输入工作流标题', 'warning');
            return;
        }

        try {
            await http.post('/workflows', { title, description });
            utils.showToast('工作流创建成功', 'success');
            modal.remove();
            loadWorkflows();
        } catch (error) {
            utils.showToast('创建失败: ' + error.message, 'error');
        }
    });
}

// 显示创建表单模态框
async function showCreateFormModal(workflowId) {
    // 首先显示保密协议
    const shouldProceed = await showPrivacyAgreement();
    if (!shouldProceed) return;

    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h5 class="modal-title">提交修复表单</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <form id="createFormForm" enctype="multipart/form-data">
                <div class="modal-body">
                    <div class="form-row">
                        <div class="form-col">
                            <div class="form-group">
                                <label>壁画图片</label>
                                <div class="file-upload" id="imageUpload">
                                    <p>点击或拖拽上传图片</p>
                                    <input type="file" id="imageFile" accept="image/*" style="display: none;">
                                </div>
                                <div id="imagePreview" class="hidden" style="margin-top: 10px;">
                                    <img id="previewImg" style="max-width: 100%; height: auto; border-radius: 4px;">
                                </div>
                            </div>
                        </div>
                        <div class="form-col">
                            <div class="form-group">
                                <label for="imageDesc">图片描述</label>
                                <textarea class="form-control textarea" id="imageDesc" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label>图片描述附件</label>
                                <input type="file" class="form-control" id="imageDescFile" accept=".pdf,.doc,.docx,.txt">
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-col">
                            <div class="form-group">
                                <label for="restorationOpinion">修复意见</label>
                                <textarea class="form-control textarea" id="restorationOpinion" rows="4"></textarea>
                            </div>
                        </div>
                        <div class="form-col">
                            <div class="form-group">
                                <label for="opinionTags">修复标签 (用逗号分隔)</label>
                                <input type="text" class="form-control" id="opinionTags" placeholder="如：浮灰清理,内容修补,颜料补充">
                            </div>
                            <div class="form-group">
                                <label>修复意见附件</label>
                                <input type="file" class="form-control" id="opinionFile" accept=".pdf,.doc,.docx,.txt">
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-col">
                            <div class="form-group">
                                <label for="remark">备注</label>
                                <textarea class="form-control textarea" id="remark" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="form-col">
                            <div class="form-group">
                                <label>其他附件</label>
                                <input type="file" class="form-control" id="attachmentFile">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">取消</button>
                    <button type="submit" class="btn btn-primary">提交表单</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // 初始化图片上传
    initFileUpload('imageUpload', 'imageFile', function(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('previewImg').src = e.target.result;
                document.getElementById('imagePreview').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // 表单提交
    document.getElementById('createFormForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append('workflow_id', workflowId);
        formData.append('image_desc', document.getElementById('imageDesc').value);
        formData.append('restoration_opinion', document.getElementById('restorationOpinion').value);
        formData.append('opinion_tags', document.getElementById('opinionTags').value);
        formData.append('remark', document.getElementById('remark').value);

        // 添加文件
        const fileInputs = ['imageFile', 'imageDescFile', 'opinionFile', 'attachmentFile'];
        const fileParams = ['image_file', 'image_desc_file', 'opinion_file', 'attachment_file'];
        
        fileInputs.forEach((inputId, index) => {
            const fileInput = document.getElementById(inputId);
            if (fileInput.files[0]) {
                formData.append(fileParams[index], fileInput.files[0]);
            }
        });

        try {
            const response = await fetch('/api/forms', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                body: formData
            });

            if (response.ok) {
                utils.showToast('表单提交成功', 'success');
                modal.remove();
                loadWorkflows();
            } else {
                const error = await response.json();
                throw new Error(error.detail || '提交失败');
            }
        } catch (error) {
            utils.showToast('提交失败: ' + error.message, 'error');
        }
    });
}

// 显示保密协议
async function showPrivacyAgreement() {
    return new Promise(async (resolve) => {
        try {
            const response = await http.get('/privacy-agreement');
            const agreement = response.data.content;

            const modal = document.createElement('div');
            modal.className = 'modal show';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 600px;">
                    <div class="modal-header">
                        <h5 class="modal-title">保密协议</h5>
                    </div>
                    <div class="modal-body">
                        <div style="max-height: 400px; overflow-y: auto; padding: 20px; background: #f8f9fa; border-radius: 4px; white-space: pre-wrap;">
                            ${agreement}
                        </div>
                        <div style="margin-top: 20px; text-align: center;">
                            <p style="color: #dc3545; font-weight: 500;">请仔细阅读上述协议内容，滚动到底部后才能同意</p>
                        </div>
                    </div>
                    <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                        <button type="button" class="btn btn-secondary" onclick="rejectAgreement()">不同意</button>
                        <button type="button" class="btn btn-primary" id="agreeBtn" disabled onclick="acceptAgreement()">同意并继续</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            const agreementContent = modal.querySelector('.modal-body > div');
            const agreeBtn = document.getElementById('agreeBtn');

            // 检测是否滚动到底部
            agreementContent.addEventListener('scroll', function() {
                if (this.scrollTop + this.clientHeight >= this.scrollHeight - 10) {
                    agreeBtn.disabled = false;
                    agreeBtn.textContent = '同意并继续';
                }
            });

            window.acceptAgreement = function() {
                modal.remove();
                resolve(true);
            };

            window.rejectAgreement = function() {
                modal.remove();
                resolve(false);
            };

        } catch (error) {
            utils.showToast('加载保密协议失败', 'error');
            resolve(false);
        }
    });
}

// 查看工作流详情
async function viewWorkflowDetails(workflowId) {
    try {
        console.log('查看工作流详情:', workflowId);
        const forms = await http.get(`/workflows/${workflowId}/forms`);
        const evaluations = await http.get(`/workflows/${workflowId}/evaluations`);
        
        // 确保使用模态框显示详情，而不是页面跳转
        showWorkflowDetailsModal(workflowId, forms, evaluations);
    } catch (error) {
        console.error('加载工作流详情失败:', error);
        utils.showToast('加载工作流详情失败', 'error');
    }
}

// 显示工作流详情模态框
function showWorkflowDetailsModal(workflowId, forms, evaluations) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 1000px;">
            <div class="modal-header">
                <h5 class="modal-title">工作流详情</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="display: flex; gap: 20px;">
                    <!-- 表单列表 -->
                    <div style="flex: 2;">
                        <h6>修复表单历史</h6>
                        <div style="max-height: 400px; overflow-y: auto;">
                            ${forms.length === 0 ? '<p>暂无表单</p>' : forms.map((form, index) => `
                                <div class="card" style="margin-bottom: 15px;">
                                    <div class="card-header" style="padding: 10px 15px;">
                                        <strong>第 ${form.step_no} 步 - ${form.submitter_name}</strong>
                                        <span style="float: right; font-size: 12px; color: #6c757d;">
                                            ${utils.formatDate(form.created_at)}
                                        </span>
                                    </div>
                                    <div class="card-body" style="padding: 15px;">
                                        ${form.image_url ? `
                                            <div style="margin-bottom: 10px;">
                                                <img src="${form.image_url}" 
                                                     style="max-width: 200px; height: auto; border-radius: 4px;" 
                                                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                                                     onload="this.nextElementSibling.style.display='none';">
                                                <div style="display: none; padding: 10px; background-color: #f8f9fa; border: 1px dashed #dee2e6; border-radius: 4px; text-align: center; color: #6c757d; font-size: 12px;">
                                                    <i class="fas fa-image" style="margin-right: 5px;"></i>
                                                    图片加载失败
                                                </div>
                                            </div>
                                        ` : ''}
                                        ${form.image_desc ? `<p><strong>图片描述：</strong>${form.image_desc}</p>` : ''}
                                        ${form.restoration_opinion ? `<p><strong>修复意见：</strong>${form.restoration_opinion}</p>` : ''}
                                        ${form.opinion_tags && form.opinion_tags.length > 0 ? `
                                            <p><strong>标签：</strong>
                                                ${form.opinion_tags.map(tag => `<span class="badge badge-secondary">${tag}</span>`).join(' ')}
                                            </p>
                                        ` : ''}
                                        ${form.remark ? `<p><strong>备注：</strong>${form.remark}</p>` : ''}
                                        <div style="margin-top: 10px;">
                                            <!-- 调试信息 -->
                                            <div style="font-size: 12px; color: #6c757d; margin-bottom: 10px;">
                                                调试: 用户角色=${utils.getCurrentUser() ? utils.getCurrentUser().role_key : '未登录'}, 表单数量=${forms.length}
                                            </div>
                                            ${utils.getCurrentUser() && utils.getCurrentUser().role_key === 'restorer' && forms.length > 1 ? `
                                                <button class="btn btn-warning" onclick="requestRollback('${workflowId}', '${form.form_id}')">
                                                    申请回溯到此步骤
                                                </button>
                                            ` : utils.getCurrentUser() && utils.getCurrentUser().role_key === 'restorer' && forms.length <= 1 ? `
                                                <div class="alert alert-info" style="font-size: 12px; padding: 8px;">
                                                    提示：需要至少2个表单才能申请回溯
                                                </div>
                                            ` : utils.getCurrentUser() && utils.getCurrentUser().role_key !== 'restorer' ? `
                                                <div class="alert alert-info" style="font-size: 12px; padding: 8px;">
                                                    提示：只有修复师可以申请回溯
                                                </div>
                                            ` : `
                                                <div class="alert alert-warning" style="font-size: 12px; padding: 8px;">
                                                    提示：用户信息未加载，无法显示回溯申请按钮
                                                </div>
                                            `}
                                            ${utils.getCurrentUser() && utils.getCurrentUser().role_key !== 'evaluator' ? `
                                                <button class="btn btn-success" onclick="finalizeWorkflow('${workflowId}', '${form.form_id}')">
                                                    设为最终方案
                                                </button>
                                            ` : ''}
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- 评估意见 -->
                    <div style="flex: 1;">
                        <h6>评估意见</h6>
                        <div style="max-height: 400px; overflow-y: auto;">
                            ${evaluations.length === 0 ? '<p>暂无评估</p>' : evaluations.map(evaluation => `
                                <div class="card" style="margin-bottom: 15px;">
                                    <div class="card-body" style="padding: 15px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                            <strong>${evaluation.evaluator_name}</strong>
                                            <span class="badge badge-primary">评分: ${evaluation.score}</span>
                                        </div>
                                        ${evaluation.comment ? `<p>${evaluation.comment}</p>` : ''}
                                        ${evaluation.support_file_url ? `
                                            <p style="margin: 10px 0;">
                                                <strong>支撑文件：</strong>
                                                <a href="${evaluation.support_file_url}" target="_blank" class="btn btn-sm btn-outline-primary" style="margin-left: 5px;">
                                                    <i class="fas fa-download"></i> 查看文件
                                                </a>
                                            </p>
                                        ` : ''}
                                        <small class="text-muted">${utils.formatDate(evaluation.created_at)}</small>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        ${utils.getCurrentUser()?.role_key === 'evaluator' || utils.getCurrentUser()?.role_key === 'admin' ? `
                            <div style="margin-top: 15px;">
                                <button class="btn btn-primary" onclick="showEvaluationModal('${workflowId}')">
                                    添加评估
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

// 申请回溯
function requestRollback(workflowId, targetFormId) {
    showRollbackModal(workflowId, targetFormId);
}

// 显示回溯申请模态框
function showRollbackModal(workflowId, targetFormId) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h5 class="modal-title">申请回溯</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="rollbackForm">
                    <div class="form-group">
                        <label for="rollbackReason">回溯原因 <span style="color: red;">*</span></label>
                        <textarea class="form-control" id="rollbackReason" rows="4" 
                                  placeholder="请详细说明申请回溯的原因..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>支撑材料（可选）</label>
                        <div class="file-upload" id="rollbackFileUpload">
                            <p>点击或拖拽上传支撑文件</p>
                            <input type="file" id="rollbackFile" accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png" style="display: none;">
                        </div>
                        <div id="rollbackFilePreview" class="hidden" style="margin-top: 10px;">
                            <div class="alert alert-info" style="padding: 8px; font-size: 12px;">
                                <i class="fas fa-file" style="margin-right: 5px;"></i>
                                <span id="rollbackFileName"></span>
                                <button type="button" class="btn btn-sm btn-outline-danger" 
                                        style="float: right; padding: 2px 6px;" 
                                        onclick="clearRollbackFile()">删除</button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">取消</button>
                <button class="btn btn-primary" onclick="submitRollbackRequest('${workflowId}', '${targetFormId}')">提交申请</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 初始化文件上传
    initFileUpload('rollbackFileUpload', 'rollbackFile', function(file) {
        if (file) {
            document.getElementById('rollbackFileName').textContent = file.name;
            document.getElementById('rollbackFilePreview').classList.remove('hidden');
        }
    });
}

// 清除回溯申请文件
function clearRollbackFile() {
    document.getElementById('rollbackFile').value = '';
    document.getElementById('rollbackFilePreview').classList.add('hidden');
}

// 提交回溯申请
async function submitRollbackRequest(workflowId, targetFormId) {
    const reason = document.getElementById('rollbackReason').value.trim();
    if (!reason) {
        utils.showToast('请输入回溯原因', 'error');
        return;
    }
    
    const fileInput = document.getElementById('rollbackFile');
    const formData = new FormData();
    formData.append('workflow_id', workflowId);
    formData.append('target_form_id', targetFormId);
    formData.append('reason', reason);
    
    if (fileInput.files[0]) {
        formData.append('support_file', fileInput.files[0]);
    }
    
    try {
        const response = await fetch('/api/rollback-requests', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('申请提交失败');
        }
        
        utils.showToast('回溯申请已提交', 'success');
        document.querySelector('.modal').remove();
        
        // 刷新相关数据
        if (typeof loadRollbackRequests === 'function') {
            loadRollbackRequests();
        }
    } catch (error) {
        utils.showToast('申请失败: ' + error.message, 'error');
    }
}

// 设为最终方案
function finalizeWorkflow(workflowId, formId) {
    utils.confirm('确认将此步骤设为最终方案吗？这将结束整个工作流。', async () => {
        try {
            const formData = new FormData();
            formData.append('final_form_id', formId);
            
            const response = await fetch(`/api/workflows/${workflowId}/finalize`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                body: formData
            });

            if (response.ok) {
                utils.showToast('已设为最终方案', 'success');
                document.querySelector('.modal').remove();
                loadWorkflows();
            } else {
                const error = await response.json();
                throw new Error(error.detail || '操作失败');
            }
        } catch (error) {
            utils.showToast('操作失败: ' + error.message, 'error');
        }
    });
}

// 显示评估模态框
function showEvaluationModal(workflowId) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">添加评估意见</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <form id="evaluationForm">
                <div class="modal-body">
                    <div class="form-group">
                        <label for="score">评分 (0-100分)</label>
                        <input type="number" class="form-control" id="score" min="0" max="100" required>
                    </div>
                    <div class="form-group">
                        <label for="comment">评估意见</label>
                        <textarea class="form-control textarea" id="comment" rows="4"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="evaluationFile">支撑文件 (可选)</label>
                        <div class="file-upload-area" style="border: 2px dashed #ddd; padding: 20px; text-align: center; cursor: pointer;" onclick="document.getElementById('evaluationFile').click()">
                            <i class="fas fa-cloud-upload-alt" style="font-size: 24px; color: #666;"></i>
                            <p style="margin: 10px 0 0 0; color: #666;">点击上传文件或拖拽文件到此处</p>
                            <small style="color: #999;">支持 PDF、DOC、DOCX、图片等格式</small>
                        </div>
                        <input type="file" id="evaluationFile" style="display: none;" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif">
                        <div id="evaluationFilePreview" class="file-preview hidden" style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span id="evaluationFileName"></span>
                                <button type="button" class="btn btn-sm btn-danger" onclick="removeEvaluationFile()">删除</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">取消</button>
                    <button type="submit" class="btn btn-primary">提交评估</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // 文件选择事件
    document.getElementById('evaluationFile').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            document.getElementById('evaluationFileName').textContent = file.name;
            document.getElementById('evaluationFilePreview').classList.remove('hidden');
        }
    });

    document.getElementById('evaluationForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const score = parseInt(document.getElementById('score').value);
        const comment = document.getElementById('comment').value.trim();
        const fileInput = document.getElementById('evaluationFile');
        
        const formData = new FormData();
        formData.append('workflow_id', workflowId);
        formData.append('score', score);
        if (comment) {
            formData.append('comment', comment);
        }
        if (fileInput.files[0]) {
            formData.append('support_file', fileInput.files[0]);
        }

        try {
            const response = await fetch('/api/evaluations', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '提交失败');
            }
            
            utils.showToast('评估提交成功', 'success');
            modal.remove();
            
            // 关闭详情窗口并刷新
            const detailModal = document.querySelector('.modal');
            if (detailModal) detailModal.remove();
            
            if (currentPage === 'evaluation') {
                loadEvaluationList();
            }
        } catch (error) {
            utils.showToast('提交失败: ' + error.message, 'error');
        }
    });
}

// 删除评估文件
function removeEvaluationFile() {
    document.getElementById('evaluationFile').value = '';
    document.getElementById('evaluationFilePreview').classList.add('hidden');
    document.getElementById('evaluationFileName').textContent = '';
}

// 加载评估列表
async function loadEvaluationList() {
    try {
        const workflows = await http.get('/workflows', { status: 'finished' });
        window.evaluationWorkflowsData = workflows; // 保存原始数据用于筛选
        renderEvaluationWorkflows(workflows);
    } catch (error) {
        console.error('加载评估列表失败:', error);
        document.getElementById('evaluationList').innerHTML = '<p class="text-center text-danger">加载失败</p>';
    }
}

// 筛选评估工作流
// 搜索和筛选评估工作流（按钮触发）
function searchAndFilterEvaluationWorkflows() {
    const searchTerm = document.getElementById('evaluationSearchInput').value.toLowerCase().trim();
    const filterValue = document.getElementById('evaluationWorkflowFilter').value;
    
    if (!window.evaluationWorkflowsData) {
        return;
    }
    
    let filteredWorkflows = window.evaluationWorkflowsData;
    
    // 先应用状态筛选
    if (filterValue === 'finished') {
        filteredWorkflows = filteredWorkflows.filter(workflow => workflow.status === 'finished');
    } else if (filterValue === 'evaluated') {
        filteredWorkflows = filteredWorkflows.filter(workflow => workflow.has_evaluation);
    } else if (filterValue === 'unevaluated') {
        filteredWorkflows = filteredWorkflows.filter(workflow => !workflow.has_evaluation);
    }
    
    // 再应用搜索筛选
    if (searchTerm) {
        filteredWorkflows = filteredWorkflows.filter(workflow => 
            workflow.title.toLowerCase().includes(searchTerm) ||
            workflow.initiator_name.toLowerCase().includes(searchTerm)
        );
    }
    
    renderEvaluationWorkflows(filteredWorkflows);
}

// 兼容性函数：筛选评估工作流
function filterEvaluationWorkflows() {
    searchAndFilterEvaluationWorkflows();
}

// 兼容性函数：搜索评估工作流
function searchEvaluationWorkflows() {
    searchAndFilterEvaluationWorkflows();
}

// 批量删除选中的评估工作流（仅管理员）
async function deleteSelectedEvaluationWorkflows() {
    const checkboxes = document.querySelectorAll('input[name="evaluationWorkflowSelect"]:checked');
    
    if (checkboxes.length === 0) {
        utils.showToast('请先选择要删除的工作流', 'warning');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 个工作流吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const deletePromises = Array.from(checkboxes).map(checkbox => 
            http.delete(`/api/admin/workflows/${checkbox.value}`)
        );
        
        await Promise.all(deletePromises);
        utils.showToast(`成功删除 ${checkboxes.length} 个工作流`, 'success');
        loadEvaluationList(); // 刷新列表
    } catch (error) {
        utils.showToast('批量删除失败: ' + error.message, 'error');
    }
}

// 渲染待评估工作流
function renderEvaluationWorkflows(workflows) {
    const container = document.getElementById('evaluationList');
    const currentUser = utils.getCurrentUser();
    const isAdmin = currentUser?.role === 'admin';
    
    if (workflows.length === 0) {
        container.innerHTML = '<p class="text-center">暂无待评估的工作流</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        ${isAdmin ? '<th><input type="checkbox" id="selectAllEvaluationWorkflows" onchange="toggleAllEvaluationWorkflows(this)"></th>' : ''}
                        <th>标题</th>
                        <th>发起人</th>
                        <th>完成时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${workflows.map(workflow => `
                        <tr>
                            ${isAdmin ? `<td><input type="checkbox" name="evaluationWorkflowSelect" value="${workflow.workflow_id}"></td>` : ''}
                            <td>${workflow.title}</td>
                            <td>${workflow.initiator_name}</td>
                            <td>${utils.formatDate(workflow.updated_at)}</td>
                            <td>
                                <button class="btn btn-primary" onclick="viewWorkflowDetails('${workflow.workflow_id}')">
                                    查看并评估
                                </button>
                                ${isAdmin ? `<button class="btn btn-sm btn-danger ml-1" onclick="deleteWorkflowFromEvaluation('${workflow.workflow_id}')">删除</button>` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// 切换所有评估工作流的选择状态
function toggleAllEvaluationWorkflows(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="evaluationWorkflowSelect"]');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

// 加载所有工作流（管理员）
async function loadAllWorkflows() {
    try {
        const workflows = await http.get('/workflows');
        window.allWorkflowsData = workflows; // 保存原始数据用于筛选
        renderWorkflowsList('allWorkflowsList', workflows);
    } catch (error) {
        console.error('加载所有工作流失败:', error);
        document.getElementById('allWorkflowsList').innerHTML = '<p class="text-center text-danger">加载失败</p>';
    }
}

// 管理页面搜索和筛选功能（按钮触发）
function searchAndFilterManagement() {
    const searchTerm = document.getElementById('managementSearchInput').value.toLowerCase().trim();
    const statusFilter = document.getElementById('managementStatusFilter').value;
    
    if (!window.allWorkflowsData) {
        return;
    }
    
    let filteredWorkflows = window.allWorkflowsData;
    
    // 先应用状态筛选
    if (statusFilter) {
        filteredWorkflows = filteredWorkflows.filter(workflow => workflow.status === statusFilter);
    }
    
    // 再应用搜索筛选
    if (searchTerm) {
        filteredWorkflows = filteredWorkflows.filter(workflow => 
            workflow.title.toLowerCase().includes(searchTerm) ||
            workflow.initiator_name.toLowerCase().includes(searchTerm)
        );
    }
    
    renderWorkflowsList('allWorkflowsList', filteredWorkflows);
}

// 搜索所有工作流（按钮触发）
function searchAllWorkflows() {
    const searchTerm = document.getElementById('workflowSearchInput').value.toLowerCase().trim();
    
    if (!window.allWorkflowsData) {
        return;
    }
    
    let filteredWorkflows = window.allWorkflowsData;
    
    // 应用搜索筛选
    if (searchTerm) {
        filteredWorkflows = filteredWorkflows.filter(workflow => 
            workflow.title.toLowerCase().includes(searchTerm) ||
            workflow.initiator_name.toLowerCase().includes(searchTerm)
        );
    }
    
    renderWorkflowsList('allWorkflowsList', filteredWorkflows);
}

// 批量删除选中的工作流（仅管理员）
async function deleteSelectedAllWorkflows() {
    const checkboxes = document.querySelectorAll('input[name="allWorkflowSelect"]:checked');
    
    if (checkboxes.length === 0) {
        utils.showToast('请先选择要删除的工作流', 'warning');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 个工作流吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const deletePromises = Array.from(checkboxes).map(checkbox => 
            http.delete(`/api/admin/workflows/${checkbox.value}`)
        );
        
        await Promise.all(deletePromises);
        utils.showToast(`成功删除 ${checkboxes.length} 个工作流`, 'success');
        loadAllWorkflows(); // 刷新列表
    } catch (error) {
        utils.showToast('批量删除失败: ' + error.message, 'error');
    }
}

// 切换所有工作流的选择状态
function toggleAllWorkflows(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="allWorkflowSelect"]');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

// 加载回溯申请列表
async function loadRollbackRequests() {
    try {
        console.log('正在加载回溯申请列表...');
        const requests = await http.get('/rollback-requests');
        console.log('回溯申请数据:', requests);
        window.rollbackRequestsData = requests; // 保存原始数据用于筛选
        renderRollbackRequests(requests);
    } catch (error) {
        console.error('加载回溯申请失败:', error);
        document.getElementById('rollbackRequestsList').innerHTML = `
            <div class="alert alert-danger">
                <p>加载失败: ${error.message}</p>
                <small>请检查网络连接或联系管理员</small>
            </div>
        `;
    }
}

// 筛选回溯申请
function filterRollbackRequests() {
    const statusFilter = document.getElementById('rollbackStatusFilter').value;
    if (!window.rollbackRequestsData) return;
    
    let filteredRequests = window.rollbackRequestsData;
    if (statusFilter) {
        filteredRequests = window.rollbackRequestsData.filter(request => request.status === statusFilter);
    }
    
    renderRollbackRequests(filteredRequests);
}

// 搜索回溯申请
function searchRollbackRequests() {
    const searchTerm = document.getElementById('rollbackRequestsSearchInput').value.toLowerCase().trim();
    const statusFilter = document.getElementById('rollbackStatusFilter').value;
    
    if (!window.rollbackRequestsData) {
        return;
    }
    
    let filteredRequests = window.rollbackRequestsData;
    
    // 先应用状态筛选
    if (statusFilter) {
        filteredRequests = filteredRequests.filter(request => request.status === statusFilter);
    }
    
    // 再应用搜索筛选
    if (searchTerm) {
        filteredRequests = filteredRequests.filter(request => 
            request.reason.toLowerCase().includes(searchTerm) ||
            request.workflow_id.toString().includes(searchTerm) ||
            request.rollback_id.toString().includes(searchTerm)
        );
    }
    
    renderRollbackRequests(filteredRequests);
}

// 批量删除选中的回溯申请（仅管理员）
async function deleteSelectedRollbackRequests() {
    const checkboxes = document.querySelectorAll('input[name="rollbackRequestSelect"]:checked');
    
    if (checkboxes.length === 0) {
        utils.showToast('请先选择要删除的回溯申请', 'warning');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 个回溯申请吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const deletePromises = Array.from(checkboxes).map(checkbox => 
            http.delete(`/api/admin/rollback-requests/${checkbox.value}`)
        );
        
        await Promise.all(deletePromises);
        utils.showToast(`成功删除 ${checkboxes.length} 个回溯申请`, 'success');
        loadRollbackRequests(); // 刷新列表
    } catch (error) {
        utils.showToast('批量删除失败: ' + error.message, 'error');
    }
}

// 切换所有回溯申请的选择状态
function toggleAllRollbackRequests(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="rollbackRequestSelect"]');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

// 渲染回溯申请列表
function renderRollbackRequests(requests) {
    const container = document.getElementById('rollbackRequestsList');
    
    console.log('渲染回溯申请列表，总数:', requests.length);
    
    const pendingRequests = requests.filter(req => req.status === 'pending');
    const approvedRequests = requests.filter(req => req.status === 'approved');
    const rejectedRequests = requests.filter(req => req.status === 'rejected');
    
    console.log('待审批申请数:', pendingRequests.length);
    
    if (requests.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <p>暂无回溯申请</p>
                <small>当修复师需要回溯到之前的步骤时，申请会显示在这里</small>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <!-- 回溯申请列表 -->
        <div style="max-height: 400px; overflow-y: auto;">
            ${requests.map(request => renderRollbackRequestCard(request, request.status === 'pending')).join('')}
        </div>
    `;
    

}

// 渲染单个回溯申请卡片
function renderRollbackRequestCard(request, showActions = false) {
    return `
        <div class="card" style="margin-bottom: 15px;">
            <div class="card-body" style="padding: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                            <h6 style="margin: 0;">${request.requester_name}</h6>
                            <span class="badge ${
                                request.status === 'pending' ? 'badge-warning' :
                                request.status === 'approved' ? 'badge-success' : 'badge-danger'
                            }">${
                                request.status === 'pending' ? '待审批' :
                                request.status === 'approved' ? '已批准' : '已拒绝'
                            }</span>
                        </div>
                        <p style="margin: 5px 0;"><strong>工作流ID：</strong>${request.workflow_id}</p>
                        <p style="margin: 5px 0;"><strong>目标表单ID：</strong>${request.target_form_id}</p>
                        <p style="margin: 5px 0;"><strong>原因：</strong>${request.reason}</p>
                        ${request.support_file_url ? `
                            <p style="margin: 5px 0;">
                                <strong>支撑文件：</strong>
                                <a href="${request.support_file_url}" target="_blank" class="btn btn-sm btn-outline-primary" style="margin-left: 5px;">
                                    <i class="fas fa-download"></i> 查看文件
                                </a>
                            </p>
                        ` : ''}
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <small class="text-muted">${utils.formatDate(request.created_at)}</small>
                            ${request.approved_at ? `<small class="text-muted">审批时间: ${utils.formatDate(request.approved_at)}</small>` : ''}
                        </div>
                    </div>
                    ${showActions && request.status === 'pending' && utils.getCurrentUser() && utils.getCurrentUser().role_key === 'admin' ? `
                        <div style="display: flex; gap: 5px;">
                            <button class="btn btn-success" onclick="approveRollback(${request.rollback_id}, true)">
                                批准
                            </button>
                            <button class="btn btn-danger" onclick="approveRollback(${request.rollback_id}, false)">
                                拒绝
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// 渲染最近审批


// 初始化回溯申请标签页


// 审批回溯申请
function approveRollback(rollbackId, approve) {
    const action = approve ? '批准' : '拒绝';
    utils.confirm(`确认${action}此回溯申请吗？`, async () => {
        try {
            const formData = new FormData();
            formData.append('approve', approve);
            
            const response = await fetch(`/api/rollback-requests/${rollbackId}/approve`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                body: formData
            });

            if (response.ok) {
                utils.showToast(`已${action}回溯申请`, 'success');
                loadRollbackRequests();
                loadDashboard(); // 刷新仪表板
                loadWorkflows(); // 刷新工作流列表状态
            } else {
                const error = await response.json();
                throw new Error(error.detail || '操作失败');
            }
        } catch (error) {
            utils.showToast('操作失败: ' + error.message, 'error');
        }
    });
}

// ==================== 管理员功能 ====================

// 显示管理员控制按钮
function showAdminControls() {
    const user = utils.getCurrentUser();
    console.log('showAdminControls调用，currentUser:', user);
    if (user && user.role_key === 'admin') {
        console.log('显示管理员控制按钮');
        const adminControls = document.getElementById('adminControls');
        if (adminControls) {
            adminControls.classList.remove('hidden');
            // 确保显示样式正确应用
            adminControls.style.display = 'flex';
            console.log('管理员按钮已显示，当前样式:', adminControls.style.display, '类列表:', adminControls.className);
        } else {
            console.error('找不到adminControls元素');
        }
    } else {
        console.log('用户不是管理员或用户信息未加载');
    }
}

// 显示管理员工作流管理模态框


















// 编辑工作流（快捷方式）




// ==================== 个人信息功能 ====================

// 加载个人信息
async function loadProfile() {
    try {
        const user = await http.get('/user/me');
        renderProfile(user);
    } catch (error) {
        console.error('加载个人信息失败:', error);
        document.getElementById('profileInfo').innerHTML = `<p class="text-danger">加载失败: ${error.message}</p>`;
    }
}

// 渲染个人信息
function renderProfile(user) {
    const container = document.getElementById('profileInfo');
    
    container.innerHTML = `
        <form id="profileForm" class="profile-form">
            <div class="form-row">
                <div class="form-group">
                    <label for="profileUsername">用户名</label>
                    <input type="text" id="profileUsername" class="form-control" value="${user.username}" readonly>
                </div>
                <div class="form-group">
                    <label for="profileFullName">姓名</label>
                    <input type="text" id="profileFullName" class="form-control" value="${user.full_name}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="profileEmail">邮箱</label>
                    <input type="email" id="profileEmail" class="form-control" value="${user.email || ''}">
                </div>
                <div class="form-group">
                    <label for="profileRole">角色</label>
                    <input type="text" id="profileRole" class="form-control" value="${user.role_name}" readonly>
                </div>
            </div>
            <div class="form-group">
                <label for="profilePhone">联系电话</label>
                <input type="tel" id="profilePhone" class="form-control" value="${user.phone || ''}">
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-primary" onclick="updateProfile()">保存修改</button>
                <button type="button" class="btn btn-secondary" onclick="showChangePasswordModal()">修改密码</button>
            </div>
        </form>
    `;
}

// 更新个人信息
async function updateProfile() {
    try {
        const fullName = document.getElementById('profileFullName').value.trim();
        const email = document.getElementById('profileEmail').value.trim();
        const phone = document.getElementById('profilePhone').value.trim();
        
        if (!fullName) {
            utils.showToast('姓名不能为空', 'error');
            return;
        }
        
        const updateData = {
            full_name: fullName,
            email: email || null,
            phone: phone || null
        };
        
        await http.put('/user/profile', updateData);
        utils.showToast('个人信息更新成功', 'success');
        
        // 更新顶部用户信息显示
        document.getElementById('userName').textContent = fullName;
        
        // 重新加载个人信息
        loadProfile();
    } catch (error) {
        utils.showToast('更新失败: ' + error.message, 'error');
    }
}

// 显示修改密码模态框
function showChangePasswordModal() {
    const modal = utils.createModal('修改密码', `
        <form id="changePasswordForm">
            <div class="form-group">
                <label for="currentPassword">当前密码</label>
                <input type="password" id="currentPassword" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="newPassword">新密码</label>
                <input type="password" id="newPassword" class="form-control" required minlength="6">
            </div>
            <div class="form-group">
                <label for="confirmPassword">确认新密码</label>
                <input type="password" id="confirmPassword" class="form-control" required>
            </div>
        </form>
    `, [
        {
            text: '取消',
            class: 'btn-secondary',
            onclick: 'utils.closeModal()'
        },
        {
            text: '确认修改',
            class: 'btn-primary',
            onclick: 'changePassword()'
        }
    ]);
}

// 修改密码
async function changePassword() {
    try {
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (!currentPassword || !newPassword || !confirmPassword) {
            utils.showToast('请填写所有字段', 'error');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            utils.showToast('新密码和确认密码不匹配', 'error');
            return;
        }
        
        if (newPassword.length < 6) {
            utils.showToast('新密码长度至少6位', 'error');
            return;
        }
        
        await http.put('/user/password', {
            current_password: currentPassword,
            new_password: newPassword
        });
        
        utils.showToast('密码修改成功，请重新登录', 'success');
        utils.closeModal();
        
        // 延迟1秒后自动退出登录
        setTimeout(() => {
            // 清除本地存储的认证信息
            localStorage.removeItem('authToken');
            localStorage.removeItem('currentUser');
            
            // 跳转到登录页面
            window.location.href = '/login';
        }, 1000);
    } catch (error) {
        utils.showToast('修改失败: ' + error.message, 'error');
    }
}

// ==================== 回溯历史功能 ====================

// 加载回溯历史
async function loadRollbackHistory() {
    try {
        const response = await http.get('/rollback-requests');
        const rollbackRequests = response.data || response;
        window.rollbackHistoryData = rollbackRequests; // 保存原始数据用于筛选
        renderRollbackHistory(rollbackRequests);
    } catch (error) {
        console.error('加载回溯历史失败:', error);
        document.getElementById('rollbackHistoryList').innerHTML = `<p class="text-danger">加载失败: ${error.message}</p>`;
    }
}

// 搜索和筛选回溯历史（按钮触发）
function searchAndFilterRollbackHistory() {
    const searchTerm = document.getElementById('rollbackHistorySearchInput').value.toLowerCase().trim();
    const statusFilter = document.getElementById('rollbackHistoryStatusFilter').value;
    
    if (!window.rollbackHistoryData) {
        return;
    }
    
    let filteredHistory = window.rollbackHistoryData;
    
    // 应用状态筛选
    if (statusFilter) {
        filteredHistory = filteredHistory.filter(request => request.status === statusFilter);
    }
    
    // 应用搜索筛选
    if (searchTerm) {
        filteredHistory = filteredHistory.filter(request => 
            request.reason.toLowerCase().includes(searchTerm) ||
            request.workflow_id.toString().includes(searchTerm) ||
            request.rollback_id.toString().includes(searchTerm) ||
            (request.requester_name && request.requester_name.toLowerCase().includes(searchTerm))
        );
    }
    
    renderRollbackHistory(filteredHistory);
}

// 保持向后兼容的搜索函数
function searchRollbackHistory() {
    searchAndFilterRollbackHistory();
}

// 批量删除选中的回溯历史（仅管理员）
async function deleteSelectedRollbackHistory() {
    const checkboxes = document.querySelectorAll('input[name="rollbackHistorySelect"]:checked');
    
    if (checkboxes.length === 0) {
        utils.showToast('请先选择要删除的回溯记录', 'warning');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 个回溯记录吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const deletePromises = Array.from(checkboxes).map(checkbox => 
            http.delete(`/api/admin/rollback-requests/${checkbox.value}`)
        );
        
        await Promise.all(deletePromises);
        utils.showToast(`成功删除 ${checkboxes.length} 个回溯记录`, 'success');
        loadRollbackHistory(); // 刷新列表
    } catch (error) {
        utils.showToast('批量删除失败: ' + error.message, 'error');
    }
}

// 切换所有回溯历史的选择状态
function toggleAllRollbackHistory(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="rollbackHistorySelect"]');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

// 渲染回溯历史
function renderRollbackHistory(rollbackRequests) {
    const container = document.getElementById('rollbackHistoryList');
    const currentUser = utils.getCurrentUser();
    const isAdmin = currentUser?.role === 'admin';
    
    // 显示或隐藏删除按钮
    const deleteBtn = document.getElementById('deleteSelectedRollbackHistoryBtn');
    if (deleteBtn) {
        deleteBtn.style.display = isAdmin ? 'inline-block' : 'none';
    }
    
    if (!rollbackRequests || rollbackRequests.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">暂无回溯申请记录</p>';
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        ${isAdmin ? '<th><input type="checkbox" onchange="toggleAllRollbackHistory(this)"> 全选</th>' : ''}
                        <th>申请ID</th>
                        <th>工作流ID</th>
                        <th>目标表单</th>
                        <th>申请原因</th>
                        <th>状态</th>
                        <th>申请时间</th>
                        <th>审批时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    rollbackRequests.forEach(request => {
        const statusBadge = getStatusBadgeClass(request.status);
        const statusText = getStatusText(request.status);
        
        html += `
            <tr>
                ${isAdmin ? `<td><input type="checkbox" name="rollbackHistorySelect" value="${request.rollback_id}"></td>` : ''}
                <td>${request.rollback_id}</td>
                <td>${request.workflow_id}</td>
                <td>${request.target_form_id}</td>
                <td title="${request.reason}">${request.reason.length > 30 ? request.reason.substring(0, 30) + '...' : request.reason}</td>
                <td><span class="badge ${statusBadge}">${statusText}</span></td>
                <td>${new Date(request.created_at).toLocaleString()}</td>
                <td>${request.approved_at ? new Date(request.approved_at).toLocaleString() : '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewRollbackDetails(${request.rollback_id})">查看详情</button>
                    ${isAdmin ? `<button class="btn btn-sm btn-danger ml-1" onclick="deleteRollbackRequest(${request.rollback_id})">删除</button>` : ''}
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// 删除评估记录（仅管理员）
async function deleteEvaluation(evaluationId) {
    try {
        if (!confirm('确定要删除这个评估记录吗？此操作不可撤销！')) {
            return;
        }
        
        await http.delete(`/api/admin/evaluations/${evaluationId}`);
        utils.showToast('评估记录删除成功', 'success');
        loadEvaluationHistory(); // 刷新列表
    } catch (error) {
        utils.showToast('删除失败: ' + error.message, 'error');
    }
}

// 删除回溯申请（仅管理员）
async function deleteRollbackRequest(rollbackId) {
    try {
        if (!confirm('确定要删除这个回溯申请吗？此操作不可撤销！')) {
            return;
        }
        
        await http.delete(`/api/admin/rollback-requests/${rollbackId}`);
        utils.showToast('回溯申请删除成功', 'success');
        loadRollbackHistory(); // 刷新列表
    } catch (error) {
        utils.showToast('删除失败: ' + error.message, 'error');
    }
}

// 查看回溯申请详情
async function viewRollbackDetails(rollbackId) {
    try {
        const response = await http.get(`/rollback-requests/${rollbackId}`);
        const rollback = response.data || response;
        showRollbackDetailsModal(rollback);
    } catch (error) {
        console.error('获取回溯申请详情失败:', error);
        utils.showToast('获取详情失败: ' + error.message, 'error');
    }
}

// 显示回溯申请详情模态框
function showRollbackDetailsModal(rollback) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    
    const statusBadge = getStatusBadgeClass(rollback.status);
    const statusText = getStatusText(rollback.status);
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h5 class="modal-title">回溯申请详情</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label><strong>申请ID:</strong></label>
                            <p>${rollback.rollback_id}</p>
                        </div>
                        <div class="form-group">
                            <label><strong>工作流ID:</strong></label>
                            <p>${rollback.workflow_id}</p>
                        </div>
                        <div class="form-group">
                            <label><strong>目标表单ID:</strong></label>
                            <p>${rollback.target_form_id}</p>
                        </div>
                        <div class="form-group">
                            <label><strong>申请人:</strong></label>
                            <p>${rollback.requester_name}</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label><strong>申请状态:</strong></label>
                            <p><span class="badge ${statusBadge}">${statusText}</span></p>
                        </div>
                        <div class="form-group">
                            <label><strong>申请时间:</strong></label>
                            <p>${new Date(rollback.created_at).toLocaleString()}</p>
                        </div>
                        ${rollback.approved_at ? `
                        <div class="form-group">
                            <label><strong>审批时间:</strong></label>
                            <p>${new Date(rollback.approved_at).toLocaleString()}</p>
                        </div>
                        ` : ''}
                        ${rollback.approver_name ? `
                        <div class="form-group">
                            <label><strong>审批人:</strong></label>
                            <p>${rollback.approver_name}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="form-group">
                    <label><strong>申请原因:</strong></label>
                    <div class="card">
                        <div class="card-body">
                            <p style="white-space: pre-wrap; margin: 0;">${rollback.reason}</p>
                        </div>
                    </div>
                </div>
                
                ${rollback.support_file_url ? `
                <div class="form-group">
                    <label><strong>支撑材料:</strong></label>
                    <div class="card">
                        <div class="card-body">
                            <a href="${rollback.support_file_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                                📎 查看支撑文件
                            </a>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">关闭</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// ==================== 评估历史功能 ====================

// 加载评估历史
async function loadEvaluationHistory() {
    try {
        const response = await http.get('/evaluations');
        const evaluations = response.data || response;
        window.evaluationHistoryData = evaluations; // 保存原始数据用于筛选
        renderEvaluationHistory(evaluations);
    } catch (error) {
        console.error('加载评估历史失败:', error);
        document.getElementById('evaluationHistoryList').innerHTML = `<p class="text-danger">加载失败: ${error.message}</p>`;
    }
}

// 搜索和筛选评估历史（按钮触发）
function searchAndFilterEvaluationHistory() {
    const searchTerm = document.getElementById('evaluationHistorySearchInput').value.toLowerCase().trim();
    const scoreFilter = document.getElementById('evaluationScoreFilter').value;
    
    if (!window.evaluationHistoryData) {
        return;
    }
    
    let filteredEvaluations = window.evaluationHistoryData;
    
    // 先应用评分筛选
    if (scoreFilter) {
        filteredEvaluations = filteredEvaluations.filter(evaluation => {
            const score = evaluation.score;
            switch (scoreFilter) {
                case 'excellent':
                    return score >= 80;
                case 'good':
                    return score >= 60 && score < 80;
                case 'poor':
                    return score < 60;
                default:
                    return true;
            }
        });
    }
    
    // 再应用搜索筛选
    if (searchTerm) {
        filteredEvaluations = filteredEvaluations.filter(evaluation => 
            evaluation.evaluate_id.toString().includes(searchTerm) ||
            evaluation.workflow_id.toString().toLowerCase().includes(searchTerm) ||
            (evaluation.comment && evaluation.comment.toLowerCase().includes(searchTerm)) ||
            evaluation.evaluator_name.toLowerCase().includes(searchTerm)
        );
    }
    
    renderEvaluationHistory(filteredEvaluations);
}

// 兼容性函数：筛选评估历史
function filterEvaluationHistory() {
    searchAndFilterEvaluationHistory();
}

// 兼容性函数：搜索评估历史
function searchEvaluationHistory() {
    searchAndFilterEvaluationHistory();
}

// 删除选中的评估历史记录（仅管理员）
async function deleteSelectedEvaluationHistory() {
    const checkboxes = document.querySelectorAll('input[name="evaluationHistorySelect"]:checked');
    
    if (checkboxes.length === 0) {
        utils.showToast('请选择要删除的评估记录', 'warning');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 条评估记录吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const deletePromises = Array.from(checkboxes).map(checkbox => {
            const evaluationId = checkbox.value;
            return http.delete(`/api/admin/evaluations/${evaluationId}`);
        });
        
        await Promise.all(deletePromises);
        utils.showToast('评估记录删除成功', 'success');
        loadEvaluationHistory(); // 刷新列表
    } catch (error) {
        utils.showToast('删除失败: ' + error.message, 'error');
    }
}

// 切换所有评估历史记录的选择状态
function toggleAllEvaluationHistory(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="evaluationHistorySelect"]');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

// 渲染评估历史
function renderEvaluationHistory(evaluations) {
    const container = document.getElementById('evaluationHistoryList');
    const currentUser = utils.getCurrentUser();
    const isAdmin = currentUser?.role === 'admin';
    
    // 显示或隐藏删除按钮
    const deleteBtn = document.getElementById('deleteSelectedEvaluationHistoryBtn');
    if (deleteBtn) {
        deleteBtn.style.display = isAdmin ? 'inline-block' : 'none';
    }
    
    if (!evaluations || evaluations.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">暂无评估记录</p>';
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        ${isAdmin ? '<th><input type="checkbox" onchange="toggleAllEvaluationHistory(this)"> 全选</th>' : ''}
                        <th>评估ID</th>
                        <th>工作流ID</th>
                        <th>评分</th>
                        <th>评估意见</th>
                        <th>评估时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    evaluations.forEach(evaluation => {
        const scoreClass = evaluation.score >= 80 ? 'text-success' : evaluation.score >= 60 ? 'text-warning' : 'text-danger';
        
        html += `
            <tr>
                ${isAdmin ? `<td><input type="checkbox" name="evaluationHistorySelect" value="${evaluation.evaluate_id}"></td>` : ''}
                <td>${evaluation.evaluate_id}</td>
                <td>${evaluation.workflow_id}</td>
                <td><span class="${scoreClass} font-weight-bold">${evaluation.score}分</span></td>
                <td title="${evaluation.comment}">${evaluation.comment ? (evaluation.comment.length > 50 ? evaluation.comment.substring(0, 50) + '...' : evaluation.comment) : '-'}</td>
                <td>${new Date(evaluation.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewEvaluationDetails(${evaluation.evaluate_id})">查看详情</button>
                    ${isAdmin ? `<button class="btn btn-sm btn-danger ml-1" onclick="deleteEvaluation(${evaluation.evaluate_id})">删除</button>` : ''}
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// 查看评估详情
async function viewEvaluationDetails(evaluationId) {
    try {
        const response = await http.get(`/evaluations/${evaluationId}`);
        const evaluation = response.data || response;
        showEvaluationDetailsModal(evaluation);
    } catch (error) {
        console.error('获取评估详情失败:', error);
        utils.showToast('获取详情失败: ' + error.message, 'error');
    }
}

// 显示评估详情模态框
function showEvaluationDetailsModal(evaluation) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    
    // 根据评分显示不同颜色
    let scoreClass = 'text-secondary';
    if (evaluation.score >= 90) scoreClass = 'text-success';
    else if (evaluation.score >= 80) scoreClass = 'text-info';
    else if (evaluation.score >= 70) scoreClass = 'text-warning';
    else if (evaluation.score >= 60) scoreClass = 'text-orange';
    else scoreClass = 'text-danger';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h5 class="modal-title">评估详情</h5>
                <button class="close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label><strong>评估ID:</strong></label>
                            <p>${evaluation.evaluate_id}</p>
                        </div>
                        <div class="form-group">
                            <label><strong>工作流ID:</strong></label>
                            <p>${evaluation.workflow_id}</p>
                        </div>
                        <div class="form-group">
                            <label><strong>评估专家:</strong></label>
                            <p>${evaluation.evaluator_name}</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label><strong>评估分数:</strong></label>
                            <p><span class="${scoreClass}" style="font-size: 1.5em; font-weight: bold;">${evaluation.score}分</span></p>
                        </div>
                        <div class="form-group">
                            <label><strong>评估时间:</strong></label>
                            <p>${new Date(evaluation.created_at).toLocaleString()}</p>
                        </div>
                        ${evaluation.updated_at && evaluation.updated_at !== evaluation.created_at ? `
                        <div class="form-group">
                            <label><strong>更新时间:</strong></label>
                            <p>${new Date(evaluation.updated_at).toLocaleString()}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="form-group">
                    <label><strong>评估意见:</strong></label>
                    <div class="card">
                        <div class="card-body">
                            <p style="white-space: pre-wrap; margin: 0;">${evaluation.comment || '暂无评估意见'}</p>
                        </div>
                    </div>
                </div>
                
                ${evaluation.evaluation_file ? `
                <div class="form-group">
                    <label><strong>评估文件:</strong></label>
                    <div class="card">
                        <div class="card-body">
                            <a href="${evaluation.evaluation_file}" target="_blank" class="btn btn-outline-primary btn-sm">
                                📄 查看评估文件
                            </a>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">关闭</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// ==================== 辅助函数 ====================

// 获取状态徽章样式
function getStatusBadgeClass(status) {
    switch(status) {
        case 'pending': return 'badge-warning';
        case 'approved': return 'badge-success';
        case 'rejected': return 'badge-danger';
        case 'active': return 'badge-primary';
        case 'completed': return 'badge-success';
        case 'cancelled': return 'badge-secondary';
        default: return 'badge-secondary';
    }
}

// 获取状态文本
function getStatusText(status) {
    switch(status) {
        case 'pending': return '待审批';
        case 'approved': return '已批准';
        case 'rejected': return '已拒绝';
        case 'active': return '进行中';
        case 'completed': return '已完成';
        case 'cancelled': return '已取消';
        default: return status;
    }
}




