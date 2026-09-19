with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复字段名
content = content.replace('q.correctAnswer', 'q.answer')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
