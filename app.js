/**
 * HN AI Insights - 首页应用
 * 移动端优先设计 + 分页支持
 */

const REPORTS_PER_PAGE = 10; // 每页显示 10 篇报告
let currentPage = 1;
let totalPages = 1;
let allReports = [];

async function loadReports() {
    const container = document.getElementById('reports-container');
    
    try {
        const response = await fetch('reports.json');
        if (!response.ok) throw new Error('无法加载报告索引');
        
        allReports = await response.json();
        totalPages = Math.ceil(allReports.length / REPORTS_PER_PAGE);
        
        // 更新最后更新时间
        const lastUpdate = document.getElementById('last-update');
        if (allReports.length > 0) {
            const latest = allReports[0];
            lastUpdate.textContent = `📅 最后更新：${latest.date} ${latest.time}`;
        }
        
        // 渲染报告列表
        if (allReports.length === 0) {
            container.innerHTML = `
                <div class="loading">
                    <div>📭 暂无报告</div>
                    <div style="font-size: 0.9rem; margin-top: 10px; opacity: 0.8;">等待首次分析...</div>
                </div>
            `;
            return;
        }
        
        renderPage(1);
        
    } catch (error) {
        console.error('加载报告失败:', error);
        container.innerHTML = `
            <div class="error">
                <h3>⚠️ 加载失败</h3>
                <p>无法加载报告列表，请稍后重试</p>
                <p style="font-size: 0.85rem; margin-top: 10px; opacity: 0.8;">${error.message}</p>
                <button onclick="location.reload()" class="view-btn" style="margin-top: 15px;">🔄 刷新页面</button>
            </div>
        `;
    }
}

/**
 * 渲染指定页
 */
function renderPage(page) {
    currentPage = page;
    const container = document.getElementById('reports-container');
    
    // 计算当前页的报告
    const startIndex = (page - 1) * REPORTS_PER_PAGE;
    const endIndex = startIndex + REPORTS_PER_PAGE;
    const pageReports = allReports.slice(startIndex, endIndex);
    
    // 渲染报告卡片
    const reportsHTML = pageReports.map(report => `
        <article class="report-card">
            <div class="report-header">
                <h2 class="report-date">📅 ${formatDate(report.date)}</h2>
                <span class="report-time">⏰ ${report.time}</span>
            </div>
            <p class="report-summary">
                ${report.summary || '查看完整分析报告'}
            </p>
            ${renderArticles(report.articles)}
            <a href="report.html?file=${encodeURIComponent(report.file)}" class="view-btn">
                📄 查看完整报告
            </a>
        </article>
    `).join('');
    
    // 渲染分页控件
    const paginationHTML = renderPagination();
    
    container.innerHTML = reportsHTML + paginationHTML;
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 渲染分页控件
 */
function renderPagination() {
    if (totalPages <= 1) return '';
    
    const pages = [];
    const maxVisible = 5; // 最多显示 5 个页码
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    // 调整起始页，确保始终显示 maxVisible 个页码
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    // 上一页
    if (currentPage > 1) {
        pages.push(`<button onclick="renderPage(${currentPage - 1})" class="page-btn">← 上一页</button>`);
    }
    
    // 第一页（如果不在可见范围内）
    if (startPage > 1) {
        pages.push(`<button onclick="renderPage(1)" class="page-btn ${currentPage === 1 ? 'active' : ''}">1</button>`);
        if (startPage > 2) {
            pages.push(`<span class="page-ellipsis">...</span>`);
        }
    }
    
    // 可见页码
    for (let i = startPage; i <= endPage; i++) {
        pages.push(`<button onclick="renderPage(${i})" class="page-btn ${currentPage === i ? 'active' : ''}">${i}</button>`);
    }
    
    // 最后一页（如果不在可见范围内）
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            pages.push(`<span class="page-ellipsis">...</span>`);
        }
        pages.push(`<button onclick="renderPage(${totalPages})" class="page-btn ${currentPage === totalPages ? 'active' : ''}">${totalPages}</button>`);
    }
    
    // 下一页
    if (currentPage < totalPages) {
        pages.push(`<button onclick="renderPage(${currentPage + 1})" class="page-btn">下一页 →</button>`);
    }
    
    // 页码信息
    const infoHTML = `<div class="page-info">第 ${currentPage} / ${totalPages} 页 · 共 ${allReports.length} 篇报告</div>`;
    
    return `
        <div class="pagination">
            ${infoHTML}
            <div class="page-buttons">
                ${pages.join('')}
            </div>
        </div>
    `;
}

/**
 * 渲染文章列表（移动端优化）
 */
function renderArticles(articles) {
    if (!articles || articles.length === 0) return '';
    
    // 移动端只显示前 3 篇
    const displayArticles = articles.slice(0, 3);
    const remaining = articles.length - 3;
    
    return `
        <ul class="article-list">
            ${displayArticles.map(article => `
                <li class="article-item">
                    <a href="${article.url || article.hnUrl || '#'}" target="_blank" rel="noopener" class="article-title">
                        ${truncateTitle(article.title)}
                    </a>
                    <span class="article-meta">
                        <span class="hot-score">🔥 ${formatPoints(article.points)}</span>
                        <span>💬 ${article.comments || 0}</span>
                    </span>
                </li>
            `).join('')}
        </ul>
        ${remaining > 0 ? `<p style="font-size: 0.85rem; color: #888; text-align: center; margin-bottom: 12px;">还有 ${remaining} 篇文章 →</p>` : ''}
    `;
}

/**
 * 格式化日期显示
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
        return '今天';
    } else if (date.toDateString() === yesterday.toDateString()) {
        return '昨天';
    } else {
        return `${date.getMonth() + 1}/${date.getDate()}`;
    }
}

/**
 * 格式化热度显示
 */
function formatPoints(points) {
    if (points >= 1000) {
        return (points / 1000).toFixed(1) + 'k';
    }
    return points;
}

/**
 * 截断长标题（移动端）
 */
function truncateTitle(title, maxLength = 50) {
    if (!title) return '';
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength - 3) + '...';
}

// 暴露 renderPage 到全局作用域
window.renderPage = renderPage;

// 页面加载时获取报告
document.addEventListener('DOMContentLoaded', loadReports);
