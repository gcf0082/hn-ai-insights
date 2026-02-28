/**
 * HN AI Insights - Report Viewer
 * 移动端优先设计
 * 使用 marked.js 渲染 Markdown 报告
 */

// 配置 marked.js 选项
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true,
    mangle: false,
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value;
            } catch (e) {
                console.warn('代码高亮失败:', e);
            }
        }
        return hljs.highlightAuto(code).value;
    },
    langPrefix: 'hljs language-'
});

// 使用 walkTokens 为链接添加 target="_blank"
marked.use({
    walkTokens(token) {
        if (token.type === 'link' && token.href && String(token.href).startsWith('http')) {
            token.target = '_blank';
            token.rel = 'noopener noreferrer';
        }
    }
});

/**
 * 将纯文本 URL 转换为 Markdown 链接
 * 同时处理文章标题，添加 HN 链接
 */
function convertUrlsToLinks(markdown) {
    // 匹配 **标签:** URL 格式
    markdown = markdown.replace(
        /(\*\*[^\*]+\*\*:\s*)(https?:\/\/[^\s\n]+)/g,
        (match, label, url) => {
            return `${label}[${url}](${url})`;
        }
    );
    
    // 匹配 链接：URL 格式（中文冒号）
    markdown = markdown.replace(
        /链接：\s*(https?:\/\/[^\s\n]+)/g,
        (match, url) => `链接：[${url}](${url})`
    );
    
    // 匹配 ### 数字。标题 (英文) 格式，将标题转换为带 HN 链接的格式
    markdown = markdown.replace(
        /###\s*(\d+)\.\s*([^\n]+?)\s*\(([^)]+)\)\s*\n\*\*HN ID:\*\*\s*(\d+)/g,
        (match, num, cnTitle, enTitle, hnId) => {
            const hnUrl = `https://news.ycombinator.com/item?id=${hnId}`;
            return `### ${num}. [${cnTitle} (${enTitle})](${hnUrl})\n**HN ID:** ${hnId}`;
        }
    );
    
    // 匹配没有英文标题的情况：### 数字。中文标题
    markdown = markdown.replace(
        /###\s*(\d+)\.\s*([^\n(]+?)\s*\n\*\*HN ID:\*\*\s*(\d+)/g,
        (match, num, cnTitle, hnId) => {
            const hnUrl = `https://news.ycombinator.com/item?id=${hnId}`;
            return `### ${num}. [${cnTitle.trim()}](${hnUrl})\n**HN ID:** ${hnId}`;
        }
    );
    
    return markdown;
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
    
    const timeMatch = markdown.match(/\*\*抓取时间:\*\*\s*(.+)/i);
    if (timeMatch) {
        items.push({
            icon: '🕐',
            label: '抓取时间',
            value: timeMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
    const countMatch = markdown.match(/\*\*分析文章数:\*\*\s*(.+)/i);
    if (countMatch) {
        items.push({
            icon: '📊',
            label: '文章数',
            value: countMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
    const sourceMatch = markdown.match(/\*\*来源:\*\*\s*(.+)/i);
    if (sourceMatch) {
        items.push({
            icon: '📰',
            label: '来源',
            value: sourceMatch[1].replace(/\*\*/g, '').trim()
        });
    }
    
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
 * 加载并渲染报告
 */
async function loadReport() {
    const container = document.getElementById('report-container');
    const urlParams = new URLSearchParams(window.location.search);
    const reportFile = urlParams.get('file');
    
    if (!reportFile) {
        showError(container, '缺少报告文件参数', '请从首页访问报告详情页');
        return;
    }
    
    showLoading(container);
    
    try {
        const response = await fetch(reportFile);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: 无法加载报告文件`);
        }
        
        let markdown = await response.text();
        markdown = convertUrlsToLinks(markdown);
        
        const metaInfo = extractMetaInfo(markdown);
        const html = marked.parse(markdown);
        const pageTitle = extractTitle(markdown) || '报告详情';
        
        document.title = `${pageTitle} - HN AI Insights`;
        renderReport(container, metaInfo, html);
        postProcess(container);
        
    } catch (error) {
        console.error('加载报告失败:', error);
        showError(container, '加载失败', error.message);
    }
}

/**
 * 显示加载状态
 */
function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div style="font-size: 1rem;">正在加载报告...</div>
            <div style="font-size: 0.85rem; margin-top: 10px; opacity: 0.8;">
                使用 marked.js 渲染
            </div>
        </div>
    `;
}

/**
 * 显示错误信息
 */
function showError(container, title, message) {
    container.innerHTML = `
        <div class="error">
            <h3>⚠️ ${title}</h3>
            <p>${message}</p>
            <a href="index.html" class="view-btn" style="display: inline-block; margin-top: 15px;">← 返回首页</a>
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
        <p class="table-scroll-hint">📱 表格可左右滑动查看</p>
    `;
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
    
    // 为表格添加滚动容器
    container.querySelectorAll('table').forEach(table => {
        if (!table.parentElement.classList.contains('table-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            wrapper.style.overflowX = 'auto';
            wrapper.style.webkitOverflowScrolling = 'touch';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// 页面加载时获取报告
document.addEventListener('DOMContentLoaded', loadReport);
