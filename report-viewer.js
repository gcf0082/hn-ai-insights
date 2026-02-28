// HN AI Insights - 报告查看器
// 使用 marked.js 渲染 Markdown 报告

// 配置 marked 选项
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true,
    mangle: false
});

async function loadReport() {
    const container = document.getElementById('report-container');
    
    // 从 URL 参数获取报告文件路径
    const urlParams = new URLSearchParams(window.location.search);
    const reportFile = urlParams.get('file');
    
    if (!reportFile) {
        container.innerHTML = `
            <div class="error">
                <h3>⚠️ 缺少报告文件参数</h3>
                <p>请从首页访问报告详情页</p>
                <a href="index.html" class="back-btn" style="margin-top: 15px;">返回首页</a>
            </div>
        `;
        return;
    }
    
    try {
        // 加载 Markdown 文件
        const response = await fetch(reportFile);
        if (!response.ok) {
            throw new Error(`无法加载报告文件：${reportFile}`);
        }
        
        const markdown = await response.text();
        
        // 提取报告元信息
        const metaInfo = extractMetaInfo(markdown);
        
        // 渲染 Markdown
        const html = marked.parse(markdown);
        
        // 更新页面标题
        const pageTitle = extractTitle(markdown) || '报告详情';
        document.title = `${pageTitle} - HN AI Insights`;
        
        // 渲染内容
        container.innerHTML = `
            ${metaInfo ? `<div class="meta-info">${metaInfo}</div>` : ''}
            <div class="markdown-body">${html}</div>
        `;
        
        // 为表格添加响应式包装
        container.querySelectorAll('table').forEach(table => {
            const wrapper = document.createElement('div');
            wrapper.style.overflowX = 'auto';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });
        
        // 为外部链接添加 target="_blank"
        container.querySelectorAll('a[href^="http"]').forEach(link => {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        });
        
    } catch (error) {
        console.error('加载报告失败:', error);
        container.innerHTML = `
            <div class="error">
                <h3>⚠️ 加载失败</h3>
                <p>无法加载报告文件</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">错误：${error.message}</p>
                <a href="index.html" class="back-btn" style="margin-top: 15px;">返回首页</a>
            </div>
        `;
    }
}

// 从 Markdown 提取标题
function extractTitle(markdown) {
    const match = markdown.match(/^#\s+(.+)$/m);
    return match ? match[1].replace(/[#*`]/g, '').trim() : null;
}

// 从 Markdown 提取元信息
function extractMetaInfo(markdown) {
    const lines = [];
    
    // 提取抓取时间
    const timeMatch = markdown.match(/\*\*抓取时间:\*\*\s*(.+)/i);
    if (timeMatch) {
        lines.push(`<span>🕐 <strong>抓取时间:</strong> ${timeMatch[1].replace(/\*\*/g, '')}</span>`);
    }
    
    // 提取分析文章数
    const countMatch = markdown.match(/\*\*分析文章数:\*\*\s*(.+)/i);
    if (countMatch) {
        lines.push(`<span>📊 <strong>文章数:</strong> ${countMatch[1].replace(/\*\*/g, '')}</span>`);
    }
    
    // 提取来源
    const sourceMatch = markdown.match(/\*\*来源:\*\*\s*(.+)/i);
    if (sourceMatch) {
        lines.push(`<span>📰 <strong>来源:</strong> ${sourceMatch[1].replace(/\*\*/g, '')}</span>`);
    }
    
    return lines.length > 0 ? lines.join('') : null;
}

// 页面加载时获取报告
document.addEventListener('DOMContentLoaded', loadReport);
