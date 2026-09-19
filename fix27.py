with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. saveExamProgress只存本地，不上传云端
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
        start_time: state.startTime,
        is_final: false
      }).catch(function() {});
    }
  }"""

new_save = """  function saveExamProgress() {
    if (!state.currentPaper) return;
    var progress = {
      paper: state.currentPaper,
      currentIndex: state.currentIndex,
      answers: state.answers,
      submittedAnswers: state.submittedAnswers || [],
      currentScore: state.currentScore || 0,
      startTime: state.startTime,
      endTime: state.endTime,
      savedAt: Date.now()
    };
    Storage.set('exam_progress', progress);
  }

  // 退出时保存中途进度到云端
  function saveMidProgress() {
    if (!state.currentPaper || !Cloud.isConfigured() || !state.userInfo || !state.userInfo.studentId) return;
    var score = state.currentScore || 0;
    var correctCount = (state.submittedAnswers || []).filter(function(a){return a&&a.correct;}).length;
    // 先删掉之前的中途记录，再上传新的
    Cloud.fetchRecordsByStudent(state.userInfo.studentId).then(function(records) {
      records.forEach(function(r) {
        if (!r.is_final) {
          // 删掉旧的
          fetch('https://uazwtblpwayqlpczczai.supabase.co/rest/v1/exam_records?id=eq.' + r.id, {
            method: 'DELETE',
            headers: {
              'apikey': 'sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs',
              'Authorization': 'Bearer sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs'
            }
          });
        }
      });
      // 上传新的
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
        start_time: state.startTime,
        is_final: false
      }).catch(function() {});
    }).catch(function() {});
  }"""

content = content.replace(old_save, new_save)

# 2. 退出保存进度时调用saveMidProgress
old_exit_save = """    // 保存进度下次继续
    mask.querySelector('#exit-save-btn').onclick = function() {
      saveExamProgress();
      mask.remove();
      renderPage('home');
      Util.showToast('进度已保存，考试期间可继续');
    };"""

new_exit_save = """    // 保存进度下次继续
    mask.querySelector('#exit-save-btn').onclick = function() {
      saveExamProgress();
      saveMidProgress();
      mask.remove();
      renderPage('home');
      Util.showToast('进度已保存，考试期间可继续');
    };"""

content = content.replace(old_exit_save, new_exit_save)

# 3. 交卷后清掉本地进度
old_submit_clear = """    // 清除进度
    Storage.remove('exam_progress_' + paper.paperId);"""

new_submit_clear = """    // 清除进度
    Storage.remove('exam_progress');"""

content = content.replace(old_submit_clear, new_submit_clear)

# 4. 检查进度的key改成统一的
old_check = """    var keys = [];
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.indexOf('base_exam_exam_progress_') === 0) keys.push(k);
    }

    if (keys.length > 0) {
      // 有保存的进度，问是否继续
      var lastKey = keys[keys.length - 1];
      var progress = JSON.parse(localStorage.getItem(lastKey));"""

new_check = """    var progress = Storage.get('exam_progress', null);

    if (progress) {
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {"""

content = content.replace(old_check, new_check)

# 5. 时间到了清掉旧进度的代码
old_expire = """      } else {
        // 时间到了，清掉旧进度
        keys.forEach(function(k) { localStorage.removeItem(k); });
      }
    }

    startNewExam();"""

new_expire = """      } else {
        // 时间到了，清掉旧进度
        Storage.remove('exam_progress');
      }
    }

    if (!progress || Math.floor((progress.endTime - Date.now()) / 1000) <= 0) {
      startNewExam();
    }"""

content = content.replace(old_expire, new_expire)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
