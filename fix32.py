with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换saveExamProgress函数，加saveMidProgress
old = """  function saveExamProgress() {
    if (!state.currentPaper) return;
    Storage.set('exam_progress_' + state.currentPaper.paperId, {
      answers: state.answers,
      marked: state.marked,
      currentIndex: state.currentIndex,
      endTime: state.endTime,
      saveTime: Date.now()
    });
  }"""

new = """  function saveExamProgress() {
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
      var delPromises = [];
      records.forEach(function(r) {
        if (!r.is_final) {
          delPromises.push(fetch('https://uazwtblpwayqlpczczai.supabase.co/rest/v1/exam_records?id=eq.' + r.id, {
            method: 'DELETE',
            headers: {
              'apikey': 'sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs',
              'Authorization': 'Bearer sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs'
            }
          }));
        }
      });
      Promise.all(delPromises).then(function() {
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
      });
    }).catch(function() {});
  }"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
