with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 班级改成文本输入框，必填
old_class = """        (classOptions.length > 0 ?
          '<div class="form-group">' +
            '<label class="form-label">班级</label>' +
            '<select class="form-input" data-input="student-class">' + classOptsHtml + '</select>' +
          '</div>' : '');"""

new_class = """        '<div class="form-group">' +
          '<label class="form-label">班级</label>' +
          '<input class="form-input" type="text" data-input="student-class" placeholder="请输入班级，如：计科2401" maxlength="30" value="' + (state.userInfo ? state.userInfo.clazz || '' : '') + '" list="class-list">' +
          '<datalist id="class-list">' + classOptsHtml.replace('<option value="">请选择班级</option>', '') + '</datalist>' +
        '</div>';"""

content = content.replace(old_class, new_class)

# 2. 开始考试前校验班级
old_validate = """    if (!Util.validateName(state.userInfo.name)) {
      Util.showToast('姓名格式不正确（2-20个字符）');
      return;
    }"""

new_validate = """    if (!Util.validateName(state.userInfo.name)) {
      Util.showToast('姓名格式不正确（2-20个字符）');
      return;
    }
    if (!state.userInfo.clazz || !state.userInfo.clazz.trim()) {
      Util.showToast('请输入班级');
      return;
    }"""

content = content.replace(old_validate, new_validate)

# 3. 成绩按班级分组显示
old_session = """    var sessionHtml = '';
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
    });"""

new_session = """    var sessionHtml = '';
    var weekDays = ['周日','周一','周二','周三','周四','周五','周六'];
    sessionKeys.forEach(function(sk) {
      var records = sessions[sk];
      var d = new Date(parseInt(sk));
      var pad = function(n){return n<10?'0'+n:n;};
      var dateStr = d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate());
      var weekStr = weekDays[d.getDay()];
      var timeStr = pad(d.getHours()) + ':' + pad(d.getMinutes());
      var maxScore = Math.max.apply(null, records.map(function(r){return r.score;}));
      var finalCount = records.filter(function(r){return r.is_final;}).length;

      // 按班级分组
      var classGroups = {};
      records.forEach(function(r) {
        var c = r.clazz || '未分班';
        if (!classGroups[c]) classGroups[c] = [];
        classGroups[c].push(r);
      });

      sessionHtml +=
        '<div style="margin-bottom:20px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">' +
          '<div style="background:#f8fafc;padding:12px 16px;">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;">' +
              '<div style="font-weight:600;font-size:15px;">第 ' + (parseInt(sk)/1000).toString().slice(-6) + ' 场</div>' +
              '<div style="font-size:13px;color:var(--gray-500);">' + dateStr + ' ' + weekStr + ' ' + timeStr + '</div>' +
            '</div>' +
            '<div style="font-size:13px;color:var(--gray-600);margin-top:4px;">最高分：' + maxScore + ' 分 · 交卷人数：' + finalCount + ' · 班级数：' + Object.keys(classGroups).length + '</div>' +
          '</div>';

      // 每个班级
      Object.keys(classGroups).sort().forEach(function(className) {
        var classRecords = classGroups[className];
        var classStudents = {};
        classRecords.forEach(function(r) {
          var sid = r.studentId;
          if (!classStudents[sid] || r.is_final) classStudents[sid] = r;
        });
        var classMax = Math.max.apply(null, Object.values(classStudents).map(function(r){return r.score;}));
        var classAvg = Math.round(Object.values(classStudents).reduce(function(s,r){return s+r.score;},0) / Object.keys(classStudents).length * 10) / 10;

        sessionHtml +=
          '<div style="padding:12px 16px;border-top:1px solid #f1f5f9;">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
              '<div style="font-weight:600;color:#3b82f6;">' + className + '</div>' +
              '<div style="font-size:12px;color:var(--gray-500);">最高 ' + classMax + ' · 平均 ' + classAvg + ' · ' + Object.keys(classStudents).length + '人</div>' +
            '</div>';

        Object.values(classStudents).forEach(function(r) {
          var scoreClass = r.score >= 90 ? 'text-success' : r.score >= 60 ? 'text-warning' : 'text-danger';
          sessionHtml +=
            '<div class="score-row" data-action="view-student-detail" data-studentid="' + r.studentId + '">' +
              '<div class="score-score ' + scoreClass + '">' + r.score + '</div>' +
              '<div class="score-student"><div class="ss-name">' + r.name + '</div><div class="ss-id">' + r.studentId + (r.is_final ? '' : ' · <span style="color:#f59e0b;">未交卷</span>') + '</div></div>' +
              '<div class="score-time">' + Util.formatTime(r.submitTime) + '</div>' +
            '</div>';
        });

        sessionHtml += '</div>';
      });

      sessionHtml += '</div>';
    });"""

content = content.replace(old_session, new_session)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
