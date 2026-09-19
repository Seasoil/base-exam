with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改renderAdminScores，统一做字段映射
old = """    if (bodyEl) bodyEl.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><div>正在从云端加载...</div></div>';
    if (Cloud.isConfigured()) {
      Cloud.fetchAllRecords(1000).then(function(res) {
        var records = res.results || [];
        var scoresMap = {};
        records.forEach(function(r) {
          var sid = r.student_id;
          if (!scoresMap[sid]) {
            scoresMap[sid] = { studentId: sid, name: r.name, maxScore: r.score, latestScore: r.score, examCount: 1, latestBlurCount: r.blur_count||0, maxBlurCount: r.blur_count||0, latestSubmitTime: r.submitTime };
          } else {
            var s = scoresMap[sid];
            s.maxScore = Math.max(s.maxScore, r.score);
            s.latestScore = r.score;
            s.examCount++;
            s.maxBlurCount = Math.max(s.maxBlurCount, r.blur_count||0);
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

new = """    if (bodyEl) bodyEl.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><div>正在从云端加载...</div></div>';
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
            deviceModel: r.device_model
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

content = content.replace(old, new)

# 修改viewStudentDetail，从state.cloudRecords找
old_detail = """  function viewStudentDetail(studentId) {
    var records = Storage.get('scores', [])
      .filter(function(r) { return r.studentId === studentId; })
      .sort(function(a, b) { return b.submitTime - a.submitTime; });"""

new_detail = """  function viewStudentDetail(studentId) {
    var allRecords = state.cloudRecords || Storage.get('scores', []);
    var records = allRecords
      .filter(function(r) { return r.studentId === studentId; })
      .sort(function(a, b) { return b.submitTime - a.submitTime; });"""

content = content.replace(old_detail, new_detail)

# 修改监控页的字段映射
old_monitor = """          if (!m[r.studentId]) m[r.studentId] = { studentId:r.studentId, name:r.name, latestScore:r.score, maxBlurCount:r.blur_count||0, deviceModel:r.device_model||'未知' };
          else { m[r.studentId].maxBlurCount = Math.max(m[r.studentId].maxBlurCount, r.blur_count||0); m[r.studentId].latestScore = r.score; }"""
new_monitor = """          var sid = r.student_id || r.studentId;
          var bc = r.blur_count || r.blurCount || 0;
          var dm = r.device_model || r.deviceModel || '未知';
          if (!m[sid]) m[sid] = { studentId: sid, name: r.name, latestScore: r.score, maxBlurCount: bc, deviceModel: dm };
          else { m[sid].maxBlurCount = Math.max(m[sid].maxBlurCount, bc); m[sid].latestScore = r.score; }"""
content = content.replace(old_monitor, new_monitor)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
