import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old = """function renderAdminScores() {
    var scores = Storage.get('scores', []);"""

new = """function renderAdminScores() {
    var bodyEl = document.getElementById('admin-scores-content');
    if (bodyEl) bodyEl.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><div>正在从云端加载...</div></div>';
    if (Cloud.isConfigured()) {
      Cloud.fetchAllRecords(1000).then(function(res) {
        var records = res.results || [];
        var scoresMap = {};
        records.forEach(function(r) {
          var sid = r.studentId;
          if (!scoresMap[sid]) {
            scoresMap[sid] = { studentId: sid, name: r.name, maxScore: r.score, latestScore: r.score, examCount: 1, latestBlurCount: r.blurCount||0, maxBlurCount: r.blurCount||0, latestSubmitTime: r.submitTime };
          } else {
            var s = scoresMap[sid];
            s.maxScore = Math.max(s.maxScore, r.score);
            s.latestScore = r.score;
            s.examCount++;
            s.maxBlurCount = Math.max(s.maxBlurCount, r.blurCount||0);
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
  }

  function renderScoresList(scores) {"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
