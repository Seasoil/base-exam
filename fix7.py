with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 去掉上传时的clazz字段
old = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,"""
new = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        score: score,"""
content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
