// HN AI Insights - 前端应用
// 加载并显示分析报告列表

const REPORTS_DIR = 'reports/';

async function loadReports() {
    const container = document.getElementById('reports-container');
    
    try {
        // 加载 reports.json 索引文件
        const response = await fetch('reports.json');
        if (!response.ok) throw new Error('无法加载报告索引');
        
        const reports = await response.json();
        
        // 更新最后更新时间
        const lastUpdate = document.getElementById('last-update');
        if (reports.length > 0) {
            const latest = reports[0];
            lastUpdate.textContent = `最后更新：${latest.date} ${latest.time}`;
        }
        
        // 渲染报告列表
        if (reports.length === 0) {
            container.innerHTML = '<div class="loading">暂无报告，等待首次分析...</div>';
            return;
        }
        
        container.innerHTML = reports.map(report => `
            <article class="report-card">
                <div class="report-header">
                    <h2 class="report-date">📅 ${report.date}</h2>
                    <span class="report-time">⏰ ${report.time}</span>
                </div>
                <p class="report-summary">
                    ${report.summary || '查看完整分析报告'}
                </p>
                <ul class="article-list">
                    ${report.articles.slice(0, 5).map(article => `
                        <li class="article-item">
                            <a href="${article.url}" target="_blank" class="article-title">
                                ${article.title}
                            </a>
                            <span class="article-meta">
                                🔥 ${article.points} pts · 💬 ${article.comments} 评论
                            </span>
                        </li>
                    `).join('')}
                </ul>
                <a href="${report.file}" class="view-btn" target="_blank">
                    📄 查看完整报告
                </a>
            </article>
        `).join('');
        
    } catch (error) {
        console.error('加载报告失败:', error);
        container.innerHTML = `
            <div class="error">
                <h3>⚠️ 加载失败</h3>
                <p>无法加载报告列表，请稍后重试。</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">错误：${error.message}</p>
            </div>
        `;
    }
}

// 页面加载时获取报告
document.addEventListener('DOMContentLoaded', loadReports);
