with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改详情页字段名
old = """      recordsHtml +=
        '<div class="detail-record">' +
          '<div class="dr-score ' + scoreClass + '">' + r.score + '</div>' +
          '<div class="dr-content">' +
            '<div>正确 ' + r.correctCount + '/' + r.totalCount + ' · 用时 ' + Util.formatDuration(r.duration) + '</div>' +
            '<div class="dr-time">' + Util.formatTime(r.submitTime) + '</div>' +
          '</div>' +
        '</div>';"""

new = """      recordsHtml +=
        '<div class="detail-record">' +
          '<div class="dr-score ' + scoreClass + '">' + r.score + '</div>' +
          '<div class="dr-content">' +
            '<div>正确 ' + (r.correct_count || r.correctCount) + '/' + (r.total_count || r.totalCount) + ' · 用时 ' + Util.formatDuration(r.duration) + '</div>' +
            '<div class="dr-time">' + Util.formatTime(r.submit_time || r.submitTime) + '</div>' +
          '</div>' +
        '</div>';"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
