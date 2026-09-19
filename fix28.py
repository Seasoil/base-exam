with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复重复的代码
old = """    if (progress) {
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {
        // 时间还有剩余，问是否继续"""

new = """    if (progress) {
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {
        // 时间还有剩余，问是否继续"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
