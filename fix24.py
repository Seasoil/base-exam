with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old = """        Util.showModal('考试警告',
          '检测到您已切换到其他应用 ' + count + ' 次。\\n\\n' +
          '为防止作弊，切屏行为已被记录，将在成绩中标注。\\n' +
          '请勿再次切换，否则成绩可能无效。',
          '我知道了');"""

new = """        Util.showModal('考试警告',
          '考试期间请勿切换应用或页面，切屏行为已被记录。',
          '我知道了');"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
