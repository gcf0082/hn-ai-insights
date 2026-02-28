/**
 * HN AI Insights - Report Viewer
 * 使用 marked.js 渲染 Markdown 报告
 * 集成 highlight.js 代码高亮
 */

// 配置 marked.js 选项
marked.setOptions({
    breaks: true,           // 启用换行
    gfm: true,              // GitHub Flavored Markdown
    headerIds: true,        // 标题 ID
    mangle: false,          // 不转义 HTML
    highlight: function(code, lang) {
        // 代码高亮
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value;
            } catch (e) {
                console.warn('代码高亮失败:', e);
            }
        }
        return hljs.highlightAuto(code).value;
    },
    langPrefix: 'hljs language-'  // highlight.js 类名前缀
});

// 自定义 Markdown 渲染器
const renderer = new marked.Renderer();

// 自定义链接渲染（添加 target="_blank"）
renderer.link = function(href, title, text) {
    const target = href.startsWith('http') ? ' target="_blank" rel="noopener noreferrer"' : '';
    return `<a href="${href}"${target}${title ? ` title="${title}"` : ''}>${text}</a>`;
};

// 自定义表格渲染（添加响应式包装）
renderer.table = function(header, body) {
    return `
        <div style="overflow-x: auto; margin: 20px 0;">
            <table>
                <thead>${header}</thead>
                <tbody>${body}</tbody>
            </table>
        </div>
    `;
};

// 应用自定义渲染器
marked.use({ renderer });

/**
 * 加载并渲染报告
 */
async function loadReport() {
    const container = document.getElementById('report-container');
    
    // 从 URL 参数获取报告文件路径
    const urlParams = new URLSearchParams(window.location.search);
    const reportFile = urlParams.get('file');
    
    if (!reportFile) {
        showError('缺少报告文件参数', '请从首页访问报告详情页');
        return;
    }
    
    // 显示加载状态
    showLoading('正在加载报告...');
    
    try {
        // 加载 Markdown 文件
        const response = await fetch(reportFile);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: 无法加载报告文件`);
        }
        
        const markdown = await response.text();
        
        // 提取元信息
        const metaInfo = extractMetaInfo(markdown);
        
        // 使用 marked.js 渲染 Markdown
        const html = marked.parse(markdown);
        
        // 更新页面标题
        const pageTitle = extractTitle(markdown) || '报告详情';
        document.title = `${pageTitle} - HN AI Insights`;
        
        // 渲染内容
        renderReport(container, metaInfo, html);
        
        // 后处理：优化链接和样式
        postProcess(container);
        
    } catch (error) {
        console.error('加载报告失败:', error);
        showError('加载失败', error.message);
    }
}

/**
 * 显示加载状态
 */
function showLoading(message) {
    document.getElementById('report-container').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div style="font-size: 1.1rem; color: #667eea;">${message}</div>
            <div style="font-size: 0.9rem; color: #888; margin-top: 10px;">
                使用 marked.js + highlight.js 渲染
            </div>
        </div>
    `;
}

/**
 * 显示错误信息
 */
function showError(title, message) {
    document.getElementById('report-container').innerHTML = `
        <div class="error-box">
            <h3 style="margin-bottom: 10px;">⚠️ ${title}</h3>
            <p style="margin-bottom: 20px;">${message}</p>
            <a href="index.html" class="back-btn">返回首页</a>
        </div>
    `;
}

/**
 * 渲染报告内容
 */
function renderReport(container, metaInfo, html) {
    container.innerHTML = `
        ${metaInfo ? `<div class="meta-card">${metaInfo}</div>` : ''}
        <div class="markdown-body">
            ${html}
        </div>
    `;
}

/**
 * 从 Markdown 提取标题
 */
function extractTitle(markdown) {
    const match = markdown.match(/^#\s+(.+)$/m);
    if (match) {
        return match[1].replace(/[#*`_\[\]]/g, '').trim();
    }
    return null;
}

/**
 * 从 Markdown 提取元信息
 */
function extractMetaInfo(markdown) {
    const items = [];
    
    // 提取抓取时间
    const timeMatch = markdown.match(/\*\*抓取时间:\*\*\s*(.+)/i);
    if (timeMatch) {
        items.push({
            icon: '🕐',
            label: '抓取时间',
            value: timeMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
    // 提取分析文章数
    const countMatch = markdown.match(/\*\*分析文章数:\*\*\s*(.+)/i);
    if (countMatch) {
        items.push({
            icon: '📊',
            label: '文章数',
            value: countMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
    // 提取来源
    const sourceMatch = markdown.match(/\*\*来源:\*\*\s*(.+)/i);
    if (sourceMatch) {
        items.push({
            icon: '📰',
            label: '来源',
            value: sourceMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
    // 提取报告生成时间
    const genMatch = markdown.match(/\*\*报告生成时间:\*\*\s*(.+)/i);
    if (genMatch) {
        items.push({
            icon: '⏰',
            label: '生成时间',
            value: genMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
    if (items.length === 0) return null;
    
    return items.map(item => `
        <div class="meta-item">
            <span class="meta-icon">${item.icon}</span>
            <div>
                <div class="meta-label">${item.label}</div>
                <div class="meta-value">${item.value}</div>
            </div>
        </div>
    `).join('');
}

/**
 * 后处理：优化渲染后的 HTML
 */
function postProcess(container) {
    // 为外部链接添加安全属性
    container.querySelectorAll('a[href^="http"]').forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });
    
    // 为表格添加额外样式类
    container.querySelectorAll('table').forEach(table => {
        table.classList.add('table');
    });
    
    // 为代码块添加复制按钮（可选）
    container.querySelectorAll('pre code').forEach(block => {
        // 可以在这里添加复制按钮功能
    });
}

// 页面加载时获取报告
document.addEventListener('DOMContentLoaded', loadReport);
