with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改交卷上传，加班级
old_upload = """Cloud.uploadRecord({
        studentId: state.userInfo.studentId,
        name: state.userInfo.name,
        score: score,"""
new_upload = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,"""
content = content.replace(old_upload, new_upload)

# 修改成绩列表显示班级
old_score_row = """'<div class="score-student"><div class="ss-name">' + s.name + '</div><div class="ss-id">' + s.studentId + '</div></div>'"""
new_score_row = """'<div class="score-student"><div class="ss-name">' + s.name + '</div><div class="ss-id">' + s.studentId + (s.clazz ? ' · ' + s.clazz : '') + '</div></div>'"""
content = content.replace(old_score_row, new_score_row)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
