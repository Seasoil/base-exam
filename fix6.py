with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,
        correctCount: correctCount,
        totalCount: questions.length,
        duration: duration,
        submitTime: now,
        isTimeout: isTimeout,
        blurCount: blurCount,
        deviceFingerprint: state.deviceInfo.fingerprint,
        deviceModel: state.deviceInfo.deviceModel
      })"""

new = """Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,
        correct_count: correctCount,
        total_count: questions.length,
        duration: duration,
        submit_time: now,
        is_timeout: isTimeout,
        blur_count: blurCount,
        device_fingerprint: state.deviceInfo.fingerprint,
        device_model: state.deviceInfo.deviceModel
      })"""

content = content.replace(old, new)

# 同时修改查询时的字段名
old_query = """var sid = r.studentId;"""
new_query = """var sid = r.student_id;"""
content = content.replace(old_query, new_query)

old_blur = """r.blurCount||0"""
new_blur = """r.blur_count||0"""
content = content.replace(old_blur, new_blur)

old_dev = """r.deviceModel||'未知'"""
new_dev = """r.device_model||'未知'"""
content = content.replace(old_dev, new_dev)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
