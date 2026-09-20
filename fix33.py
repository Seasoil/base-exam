with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('?v=2', '?v=3')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
