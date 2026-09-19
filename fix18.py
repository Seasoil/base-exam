with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改解析部分，用详细解析
old = """          '<div class="analysis-item">本题得分：' + (sa.correct ? (100 / paper.questions.length).toFixed(1) : 0) + ' 分</div>' +
          '<div class="analysis-explain">解析：' + q.question + '，从 ' + q.fromBase + ' 进制转换为 ' + q.toBase + ' 进制，结果为 ' + q.answer + '</div>' +"""

new = """          '<div class="analysis-item">本题得分：' + (sa.correct ? (100 / paper.questions.length).toFixed(1) : 0) + ' 分</div>' +
          '<div class="analysis-explain"><pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.7;margin:0;">' + Converter.generateExplanation(q, sa.userAnswer) + '</pre></div>' +"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
