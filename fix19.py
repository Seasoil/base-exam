with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 顶部加退出按钮
old_topbar = """      '<div class="exam-topbar">' +
        '<div class="exam-topbar-left">第 ' + (state.currentIndex + 1) + ' / ' + paper.questions.length + ' 题</div>' +
        '<div class="exam-topbar-center ' + (remaining <= 60 ? 'time-warning' : '') + '">⏱ ' + Util.formatDuration(remaining) + '</div>' +
        '<div class="exam-topbar-right">累计 <span style="color:#22c55e;font-weight:600;">' + totalScore.toFixed(1) + '</span> 分</div>' +
      '</div>'"""

new_topbar = """      '<div class="exam-topbar">' +
        '<div class="exam-topbar-left" data-action="exit-exam" style="cursor:pointer;color:#ef4444;">← 退出</div>' +
        '<div class="exam-topbar-center ' + (remaining <= 60 ? 'time-warning' : '') + '">⏱ ' + Util.formatDuration(remaining) + '</div>' +
        '<div class="exam-topbar-right">累计 <span style="color:#22c55e;font-weight:600;">' + totalScore.toFixed(1) + '</span> 分</div>' +
      '</div>'"""

content = content.replace(old_topbar, new_topbar)

# 2. 加exit-exam动作
old_action = "case 'submit-current': submitCurrent(); break;"
new_action = """case 'submit-current': submitCurrent(); break;
      case 'exit-exam': exitExam(); break;"""
content = content.replace(old_action, new_action)

# 3. 加exitExam函数
old_submit_current = """  // 提交当前题，即时判题
  function submitCurrent() {"""

new_submit_current = """  // 退出考试弹窗
  function exitExam() {
    var mask = document.createElement('div');
    mask.className = 'modal-mask';
    mask.innerHTML =
      '<div class="modal-box">' +
        '<div class="modal-title">退出考试</div>' +
        '<div class="modal-text">你确定要退出考试吗？</div>' +
        '<div class="modal-text" style="font-size:13px;color:var(--gray-500);margin-top:8px;">退出后进度会自动保存，下次考试期间可以继续。</div>' +
        '<div class="modal-buttons">' +
          '<button class="modal-btn modal-cancel" onclick="this.closest(\\'.modal-mask\\').remove()">继续考试</button>' +
          '<button class="modal-btn modal-danger" id="exit-confirm-btn">直接交卷</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(mask);
    mask.querySelector('#exit-confirm-btn').onclick = function() {
      mask.remove();
      doSubmit();
    };
    mask.onclick = function(e) { if (e.target === mask) mask.remove(); };
  }

  // 提交当前题，即时判题
  function submitCurrent() {"""

content = content.replace(old_submit_current, new_submit_current)

# 4. 保存进度到云端（中途保存）
old_save = """  function saveExamProgress() {
    if (!state.currentPaper) return;
    var progress = {
      paperId: state.currentPaper.paperId,
      currentIndex: state.currentIndex,
      answers: state.answers,
      submittedAnswers: state.submittedAnswers || [],
      currentScore: state.currentScore || 0,
      startTime: state.startTime,
      endTime: state.endTime,
      savedAt: Date.now()
    };
    Storage.set('exam_progress_' + state.currentPaper.paperId, progress);
  }"""

new_save = """  function saveExamProgress() {
    if (!state.currentPaper) return;
    var progress = {
      paperId: state.currentPaper.paperId,
      currentIndex: state.currentIndex,
      answers: state.answers,
      submittedAnswers: state.submittedAnswers || [],
      currentScore: state.currentScore || 0,
      startTime: state.startTime,
      endTime: state.endTime,
      savedAt: Date.now()
    };
    Storage.set('exam_progress_' + state.currentPaper.paperId, progress);
    // 云端保存中途进度
    if (Cloud.isConfigured() && state.userInfo && state.userInfo.studentId) {
      var score = state.currentScore || 0;
      var correctCount = (state.submittedAnswers || []).filter(function(a){return a&&a.correct;}).length;
      Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,
        correct_count: correctCount,
        total_count: state.currentPaper.questions.length,
        duration: Math.floor((Date.now() - state.startTime) / 1000),
        submit_time: Date.now(),
        is_timeout: false,
        blur_count: state.blurCount || 0,
        device_fingerprint: state.deviceInfo.fingerprint,
        device_model: state.deviceInfo.deviceModel,
        is_final: false
      }).catch(function() {});
    }
  }"""

content = content.replace(old_save, new_save)

# 5. 交卷时标记为最终
old_do_submit = """    // 云端同步：上传考试记录
    if (Cloud.isConfigured()) {
      Cloud.uploadRecord({
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
      }).then(function() {
        console.log('成绩已同步到云端');
      }).catch(function(err) {
        console.warn('云端同步失败：', err.message);
      });
    }"""

new_do_submit = """    // 云端同步：上传考试记录
    if (Cloud.isConfigured()) {
      Cloud.uploadRecord({
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
      }).then(function() {
        console.log('成绩已同步到云端');
      }).catch(function(err) {
        console.warn('云端同步失败：', err.message);
      });
    }"""

content = content.replace(old_do_submit, new_do_submit)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
