with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 加回clazz字段
old = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        score: score,"""
new = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,"""
content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
