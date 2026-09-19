with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 交卷上传时加exam_session（考试开始时间作为场次ID）
old_upload = """      Cloud.uploadRecord({
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
        device_model: state.deviceInfo.deviceModel,
        is_final: true
      })"""

new_upload = """      Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,
        correct_count: correctCount,
        total_count: questions.length,
        duration: duration,
        submit_time: now,
        start_time: state.startTime,
        is_timeout: isTimeout,
        blur_count: blurCount,
        device_fingerprint: state.deviceInfo.fingerprint,
        device_model: state.deviceInfo.deviceModel,
        is_final: true
      })"""

content = content.replace(old_upload, new_upload)

# 2. 中途保存也加start_time
old_save = """        device_model: state.deviceInfo.deviceModel,
        is_final: false"""
new_save = """        device_model: state.deviceInfo.deviceModel,
        start_time: state.startTime,
        is_final: false"""
content = content.replace(old_save, new_save)

# 3. 成绩列表按场次分组
old_render_scores = """    document.getElementById('admin-scores-content').innerHTML =
      '<div class="admin-header">' +
        '<div class="admin-title">成绩管理</div>' +
        '<div class="admin-logout" data-action="go-admin">返回</div>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title-row">' +
          '<div class="card-title" style="margin:0;">学生成绩</div>' +
          '<div class="count-badge">' + scores.length + ' 人</div>' +
        '</div>' +
        '<div class="sort-tabs">' +
          '<div class="sort-tab ' + sortTabClass('maxScore') + '" data-action="sort-scores" data-sort="maxScore">按最高分</div>' +
          '<div class="sort-tab ' + sortTabClass('latestScore') + '" data-action="sort-scores" data-sort="latestScore">按最新分</div>' +
          '<div class="sort-tab ' + sortTabClass('examCount') + '" data-action="sort-scores" data-sort="examCount">按考试次数</div>' +
          '<div class="sort-tab ' + sortTabClass('studentId') + '" data-action="sort-scores" data-sort="studentId">按学号</div>' +
        '</div>' +
        '<input class="form-input search-input mt-16" type="text" data-input="score-search" placeholder="搜索学号或姓名" value="' + (state.adminSearch || '') + '">' +
        scoresHtml +
        (scores.length === 0 ? '<div class="empty"><div class="empty-icon">📊</div><div>暂无成绩记录</div></div>' : '') +
      '</div>' +

      '<div class="card mt-16">' +
        '<div class="card-title-row"><div class="card-title" style="margin:0;">导出</div></div>' +
        '<div class="card-desc">导出Excel格式成绩表，可直接用Excel打开</div>' +
        '<button class="btn btn-primary mt-16" data-action="export-scores">📥 导出成绩表</button>' +
      '</div>';"""

new_render_scores = """    // 按考试场次分组
    var sessions = {};
    var allRecords = state.cloudRecords || [];
    allRecords.forEach(function(r) {
      var st = r.start_time || r.submitTime;
      if (!sessions[st]) sessions[st] = [];
      sessions[st].push(r);
    });
    var sessionKeys = Object.keys(sessions).sort(function(a,b){return b-a;});

    var sessionHtml = '';
    var weekDays = ['周日','周一','周二','周三','周四','周五','周六'];
    sessionKeys.forEach(function(sk) {
      var records = sessions[sk];
      var d = new Date(parseInt(sk));
      var pad = function(n){return n<10?'0'+n:n;};
      var dateStr = d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate());
      var weekStr = weekDays[d.getDay()];
      var timeStr = pad(d.getHours()) + ':' + pad(d.getMinutes());
      // 该场次的最高分
      var maxScore = Math.max.apply(null, records.map(function(r){return r.score;}));
      // 该场次最终人数
      var finalCount = records.filter(function(r){return r.is_final;}).length;

      sessionHtml +=
        '<div style="margin-bottom:16px;">' +
          '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
            '<div style="font-weight:600;font-size:15px;">第 ' + (parseInt(sk)/1000).toString().slice(-6) + ' 场</div>' +
            '<div style="font-size:13px;color:var(--gray-500);">' + dateStr + ' ' + weekStr + ' ' + timeStr + ' 开始</div>' +
          '</div>' +
          '<div style="font-size:13px;color:var(--gray-600);margin-bottom:8px;">最高分：' + maxScore + ' 分 · 交卷人数：' + finalCount + '</div>';

      // 该场次的学生列表
      var sessionStudents = {};
      records.forEach(function(r) {
        var sid = r.studentId;
        if (!sessionStudents[sid] || r.is_final) sessionStudents[sid] = r;
      });
      Object.values(sessionStudents).forEach(function(r) {
        var scoreClass = r.score >= 90 ? 'text-success' : r.score >= 60 ? 'text-warning' : 'text-danger';
        sessionHtml +=
          '<div class="score-row" data-action="view-student-detail" data-studentid="' + r.studentId + '">' +
            '<div class="score-score ' + scoreClass + '">' + r.score + '</div>' +
            '<div class="score-student"><div class="ss-name">' + r.name + '</div><div class="ss-id">' + r.studentId + (r.clazz ? ' · ' + r.clazz : '') + (r.is_final ? '' : ' · <span style="color:#f59e0b;">未交卷</span>') + '</div></div>' +
            '<div class="score-time">' + Util.formatTime(r.submitTime) + '</div>' +
          '</div>';
      });

      sessionHtml += '</div>';
    });

    document.getElementById('admin-scores-content').innerHTML =
      '<div class="admin-header">' +
        '<div class="admin-title">成绩管理</div>' +
        '<div class="admin-logout" data-action="go-admin">返回</div>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title-row">' +
          '<div class="card-title" style="margin:0;">考试场次</div>' +
          '<div class="count-badge">' + sessionKeys.length + ' 场</div>' +
        '</div>' +
        (sessionKeys.length === 0 ? '<div class="empty"><div class="empty-icon">📊</div><div>暂无成绩记录</div></div>' : sessionHtml) +
      '</div>' +

      '<div class="card mt-16">' +
        '<div class="card-title-row"><div class="card-title" style="margin:0;">导出</div></div>' +
        '<div class="card-desc">导出Excel格式成绩表，可直接用Excel打开</div>' +
        '<button class="btn btn-primary mt-16" data-action="export-scores">📥 导出成绩表</button>' +
      '</div>';"""

content = content.replace(old_render_scores, new_render_scores)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
