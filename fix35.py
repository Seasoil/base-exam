with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到renderAdminScores函数并替换
old_start = "  function renderAdminScores() {"
old_end = "  function renderScoresList(scores) {"

# 找到这两个函数之间的内容，替换renderAdminScores
import re

# 先加is_final和start_time到字段映射
old_map = """            deviceModel: r.device_model
          };
        });"""
new_map = """            deviceModel: r.device_model,
            isFinal: r.is_final !== false,
            startTime: r.start_time
          };
        });"""
content = content.replace(old_map, new_map)

# 替换renderAdminScores函数体，改成场次+班级分组
old_func = """  function renderAdminScores() {
    var bodyEl = document.getElementById('admin-scores-content');
    if (bodyEl) bodyEl.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><div>正在从云端加载...</div></div>';
    if (Cloud.isConfigured()) {
      Cloud.fetchAllRecords(1000).then(function(records) {
        // 统一字段映射：蛇形 -> 驼峰
        records = records.map(function(r) {
          return {
            id: r.id,
            studentId: r.student_id,
            name: r.name,
            clazz: r.clazz || '',
            score: r.score,
            correctCount: r.correct_count,
            totalCount: r.total_count,
            duration: r.duration,
            submitTime: r.submit_time,
            isTimeout: r.is_timeout,
            blurCount: r.blur_count,
            deviceFingerprint: r.device_fingerprint,
            deviceModel: r.device_model,
            isFinal: r.is_final !== false,
            startTime: r.start_time
          };
        });
        // 存到全局，供详情页使用
        state.cloudRecords = records;
        var scoresMap = {};
        records.forEach(function(r) {
          var sid = r.studentId;
          if (!scoresMap[sid]) {
            scoresMap[sid] = { studentId: sid, name: r.name, clazz: r.clazz, maxScore: r.score, latestScore: r.score, examCount: 1, latestBlurCount: r.blurCount, maxBlurCount: r.blurCount, latestSubmitTime: r.submitTime };
          } else {
            var s = scoresMap[sid];
            s.maxScore = Math.max(s.maxScore, r.score);
            s.latestScore = r.score;
            s.examCount++;
            s.maxBlurCount = Math.max(s.maxBlurCount, r.blurCount);
            s.latestSubmitTime = r.submitTime;
          }
        });
        renderScoresList(Object.values(scoresMap));
      }).catch(function() {
        renderScoresList(Storage.get('scores', []));
      });
    } else {
      renderScoresList(Storage.get('scores', []));
    }
  }"""

new_func = """  function renderAdminScores() {
    var bodyEl = document.getElementById('admin-scores-content');
    if (bodyEl) bodyEl.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><div>正在从云端加载...</div></div>';
    if (Cloud.isConfigured()) {
      Cloud.fetchAllRecords(1000).then(function(records) {
        // 统一字段映射
        records = records.map(function(r) {
          return {
            id: r.id,
            studentId: r.student_id,
            name: r.name,
            clazz: r.clazz || '未分班',
            score: r.score,
            correctCount: r.correct_count,
            totalCount: r.total_count,
            duration: r.duration,
            submitTime: r.submit_time,
            isTimeout: r.is_timeout,
            blurCount: r.blur_count,
            deviceModel: r.device_model,
            isFinal: r.is_final !== false,
            startTime: r.start_time
          };
        });
        state.cloudRecords = records;
        renderSessions(records);
      }).catch(function() {
        renderSessions([]);
      });
    } else {
      renderSessions([]);
    }
  }

  function renderSessions(records) {
    var weekDays = ['周日','周一','周二','周三','周四','周五','周六'];
    var pad = function(n){return n<10?'0'+n:n;};

    // 按场次分组（用startTime区分）
    var sessions = {};
    records.forEach(function(r) {
      var key = r.startTime || r.submitTime;
      if (!sessions[key]) sessions[key] = [];
      sessions[key].push(r);
    });
    var sessionKeys = Object.keys(sessions).sort(function(a,b){return b-a;});

    var html = '';
    if (sessionKeys.length === 0) {
      html = '<div class="empty"><div class="empty-icon">📊</div><div>暂无成绩记录</div></div>';
    } else {
      sessionKeys.forEach(function(sk) {
        var recs = sessions[sk];
        var d = new Date(parseInt(sk));
        var dateStr = d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate());
        var weekStr = weekDays[d.getDay()];
        var timeStr = pad(d.getHours()) + ':' + pad(d.getMinutes());
        var finalRecs = recs.filter(function(r){return r.isFinal;});
        var maxScore = recs.length > 0 ? Math.max.apply(null, recs.map(function(r){return r.score;})) : 0;

        // 按班级分组
        var classGroups = {};
        recs.forEach(function(r) {
          var c = r.clazz || '未分班';
          if (!classGroups[c]) classGroups[c] = [];
          classGroups[c].push(r);
        });

        html +=
          '<div style="margin-bottom:20px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">' +
            '<div style="background:#f8fafc;padding:12px 16px;">' +
              '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                '<div style="font-weight:600;font-size:15px;">' + dateStr + ' ' + weekStr + ' ' + timeStr + '</div>' +
                '<div style="font-size:13px;color:var(--gray-500);">最高分 ' + maxScore + ' · 交卷 ' + finalRecs.length + ' 人 · ' + Object.keys(classGroups).length + ' 个班</div>' +
              '</div>' +
            '</div>';

        Object.keys(classGroups).sort().forEach(function(className) {
          var classRecs = classGroups[className];
          // 每个学生取最终成绩（没有最终的取最新的）
          var studentMap = {};
          classRecs.forEach(function(r) {
            var sid = r.studentId;
            if (!studentMap[sid] || r.isFinal) studentMap[sid] = r;
          });
          var students = Object.values(studentMap);
          students.sort(function(a,b){return b.score - a.score;});
          var classMax = students.length > 0 ? Math.max.apply(null, students.map(function(r){return r.score;})) : 0;
          var classAvg = students.length > 0 ? Math.round(students.reduce(function(s,r){return s+r.score;},0) / students.length * 10) / 10 : 0;

          html +=
            '<div style="padding:12px 16px;border-top:1px solid #f1f5f9;">' +
              '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                '<div style="font-weight:600;color:#3b82f6;">' + className + '</div>' +
                '<div style="font-size:12px;color:var(--gray-500);">最高 ' + classMax + ' · 平均 ' + classAvg + ' · ' + students.length + '人</div>' +
              '</div>';

          students.forEach(function(r, idx) {
            var scoreClass = r.score >= 90 ? 'text-success' : r.score >= 60 ? 'text-warning' : 'text-danger';
            html +=
              '<div class="score-row" data-action="view-student-detail" data-studentid="' + r.studentId + '">' +
                '<div class="score-rank rank-normal">' + (idx+1) + '</div>' +
                '<div class="score-student"><div class="ss-name">' + r.name + '</div><div class="ss-id">' + r.studentId + (r.isFinal ? '' : ' · <span style="color:#f59e0b;">未交卷</span>') + '</div></div>' +
                '<div class="score-info-text"><div class="si-score ' + scoreClass + '">' + r.score + '<span class="si-unit">分</span></div></div>' +
                '<div class="score-arrow">›</div>' +
              '</div>';
          });

          html += '</div>';
        });

        html += '</div>';
      });
    }

    document.getElementById('admin-scores-content').innerHTML =
      '<div class="admin-header">' +
        '<div class="admin-title">成绩管理</div>' +
        '<div class="admin-logout" data-action="go-admin">返回</div>' +
      '</div>' +
      '<div class="card"><div class="card-title-row"><div class="card-title" style="margin:0;">考试场次</div><div class="count-badge">' + sessionKeys.length + ' 场</div></div>' +
      html +
      '</div>';
  }"""

content = content.replace(old_func, new_func)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
