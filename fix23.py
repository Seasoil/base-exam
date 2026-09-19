with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 改结果页为题号导航模式
old = """  function renderResult() {
    var r = state.examResult;
    if (!r) { renderPage('home'); return; }

    var accuracy = r.totalCount > 0 ? Math.round((r.correctCount / r.totalCount) * 1000) / 10 : 0;

    // 错题列表
    var wrongHtml = '';
    if (r.wrongQuestions.length === 0) {
      wrongHtml = '<div class="empty"><div class="empty-icon">🎉</div><div>全部答对，太棒了！</div></div>';
    } else {
      r.wrongQuestions.forEach(function(wq, idx) {
        wrongHtml +=
          '<div class="wrong-card">' +
            '<div class="wrong-header"><span class="tag tag-red">错题 ' + (idx + 1) + '</span><span class="tag tag-blue">' + wq.typeName + '</span></div>' +
            '<div class="wrong-question">' + wq.question + '</div>' +
            '<div class="wrong-answer-row">' +
              '<div class="wrong-answer-item wrong"><div class="wa-label">你的答案</div><div class="wa-value">' + (wq.userAnswer || '(未作答)') + '</div></div>' +
              '<div class="wrong-answer-item correct"><div class="wa-label">正确答案</div><div class="wa-value">' + wq.answer + '</div></div>' +
            '</div>' +
            '<div class="wrong-explanation"><div class="we-title">📖 解析</div><div class="we-content">' + wq.explanation.replace(/\\n/g, '<br>') + '</div></div>' +
          '</div>';
      });
    }

    document.getElementById('result-content').innerHTML =
      '<div class="result-score-card">' +
        '<div class="result-score-header">考试成绩' + (r.isTimeout ? '<span class="tag tag-orange" style="margin-left:12px;">超时自动提交</span>' : '') + '</div>' +
        '<div class="result-score-num">' + r.score + '<span class="score-unit">分</span></div>' +
        '<div class="result-stats">' +
          '<div class="rs-item"><div class="rs-value text-success">' + r.correctCount + '</div><div class="rs-label">正确</div></div>' +
          '<div class="rs-item"><div class="rs-value text-danger">' + (r.totalCount - r.correctCount) + '</div><div class="rs-label">错误</div></div>' +
          '<div class="rs-item"><div class="rs-value text-primary">' + accuracy + '%</div><div class="rs-label">正确率</div></div>' +
          '<div class="rs-item"><div class="rs-value">' + Util.formatDuration(r.duration) + '</div><div class="rs-label">用时</div></div>' +
        '</div>' +
        '<div class="result-submit-time">提交时间：' + Util.formatTime(r.submitTime) + '</div>' +
      '</div>' +

      '<div class="result-actions">' +
        '<button class="btn btn-primary" data-action="retake-exam">再考一次</button>' +
        '<div class="btn-row mt-16">' +
          '<button class="btn btn-secondary flex-1" data-action="view-history">历史记录</button>' +
          '<button class="btn btn-secondary flex-1" onclick="navigator.clipboard.writeText(window.location.href).then(function(){Util.showToast(\\'链接已复制\\',\\'success\\')})">分享链接</button>' +
        '</div>' +
      '</div>' +

      '<div class="section-title">错题解析（' + r.wrongQuestions.length + '）</div>' +
      wrongHtml +

      '<div class="bottom-actions"><button class="btn btn-primary" data-action="go-home">返回首页</button></div>';
  }"""

new = """  function renderResult() {
    var r = state.examResult;
    if (!r) { renderPage('home'); return; }

    var accuracy = r.totalCount > 0 ? Math.round((r.correctCount / r.totalCount) * 1000) / 10 : 0;

    // 当前题号（默认0）
    if (typeof state.resultIndex !== 'number') state.resultIndex = 0;
    if (typeof state.resultOnlyWrong !== 'boolean') state.resultOnlyWrong = false;

    // 获取题目列表（全部或仅错题）
    var questions = r.questions || [];
    var wrongIdxList = [];
    questions.forEach(function(q, i) {
      if (q.correct === false) wrongIdxList.push(i);
    });

    var displayList = state.resultOnlyWrong ? wrongIdxList.map(function(i){return {q: questions[i], idx: i};}) : questions.map(function(q,i){return {q:q, idx:i};});
    var cur = displayList[state.resultIndex];
    if (!cur) { state.resultIndex = 0; cur = displayList[0]; }

    // 题号导航HTML
    var navHtml = '';
    displayList.forEach(function(item, i) {
      var cls = 'nav-item';
      if (item.q.correct) cls += ' nav-correct';
      else cls += ' nav-wrong';
      if (i === state.resultIndex) cls += ' nav-current';
      var num = state.resultOnlyWrong ? (i+1) : (item.idx+1);
      navHtml += '<div class="' + cls + '" data-action="result-nav" data-index="' + i + '">' + num + '</div>';
    });

    // 当前题解析
    var curHtml = '';
    if (cur) {
      var q = cur.q;
      var correctClass = q.correct ? 'correct' : 'wrong';
      var correctIcon = q.correct ? '✅ 回答正确' : '❌ 回答错误';
      curHtml =
        '<div class="analysis-box ' + correctClass + '">' +
          '<div class="analysis-title">' + correctIcon + ' · 第 ' + (cur.idx+1) + ' 题</div>' +
          '<div class="analysis-item">题型：' + q.typeName + '</div>' +
          '<div class="analysis-item">题目：' + q.question + '</div>' +
          '<div class="analysis-item">原数：' + q.sourceValue + '（' + q.fromBase + '进制）</div>' +
          '<div class="analysis-item">你的答案：<span class="your-answer">' + (q.userAnswer || '空') + '</span></div>' +
          '<div class="analysis-item">正确答案：<span class="right-answer">' + q.answer + '</span></div>' +
          '<div class="analysis-explain"><pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.7;margin:0;">' + Converter.generateExplanation(q, q.userAnswer) + '</pre></div>' +
        '</div>';
    }

    document.getElementById('result-content').innerHTML =
      '<div class="result-score-card">' +
        '<div class="result-score-header">考试成绩' + (r.isTimeout ? '<span class="tag tag-orange" style="margin-left:12px;">超时自动提交</span>' : '') + '</div>' +
        '<div class="result-score-num">' + r.score + '<span class="score-unit">分</span></div>' +
        '<div class="result-stats">' +
          '<div class="rs-item"><div class="rs-value text-success">' + r.correctCount + '</div><div class="rs-label">正确</div></div>' +
          '<div class="rs-item"><div class="rs-value text-danger">' + (r.totalCount - r.correctCount) + '</div><div class="rs-label">错误</div></div>' +
          '<div class="rs-item"><div class="rs-value text-primary">' + accuracy + '%</div><div class="rs-label">正确率</div></div>' +
          '<div class="rs-item"><div class="rs-value">' + Util.formatDuration(r.duration) + '</div><div class="rs-label">用时</div></div>' +
        '</div>' +
        '<div class="result-submit-time">提交时间：' + Util.formatTime(r.submitTime) + '</div>' +
      '</div>' +

      '<div class="result-actions">' +
        '<button class="btn btn-primary" data-action="retake-exam">再考一次</button>' +
        '<div class="btn-row mt-16">' +
          '<button class="btn btn-secondary flex-1" data-action="view-history">历史记录</button>' +
          '<button class="btn btn-secondary flex-1" data-action="go-home">返回首页</button>' +
        '</div>' +
      '</div>' +

      '<div class="card" style="margin-top:16px;">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">' +
          '<div style="font-weight:600;">题目解析</div>' +
          '<button class="btn btn-secondary" data-action="toggle-wrong-only" style="padding:6px 12px;font-size:13px;">' + (state.resultOnlyWrong ? '显示全部题' : '只看错题') + '</button>' +
        '</div>' +
        '<div style="display:flex;gap:8px;align-items:center;margin-bottom:16px;">' +
          '<span>跳转到：</span>' +
          '<input type="number" id="jump-input" min="1" max="' + (state.resultOnlyWrong ? wrongIdxList.length : questions.length) + '" style="width:70px;padding:6px;border:1px solid #e5e7eb;border-radius:6px;text-align:center;">' +
          '<button class="btn btn-secondary" data-action="jump-question" style="padding:6px 12px;font-size:13px;">跳转</button>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:6px;margin-bottom:16px;">' + navHtml + '</div>' +
        curHtml +
      '</div>';

    // 暴露导航事件
    var navBtns = document.querySelectorAll('[data-action="result-nav"]');
    navBtns.forEach(function(btn) {
      btn.onclick = function() {
        state.resultIndex = parseInt(btn.dataset.index);
        renderResult();
      };
    });
  }"""

content = content.replace(old, new)

# 加动作
old_action2 = "case 'submit-current': submitCurrent(); break;"
new_action2 = """case 'submit-current': submitCurrent(); break;
      case 'toggle-wrong-only': state.resultOnlyWrong = !state.resultOnlyWrong; state.resultIndex = 0; renderResult(); break;
      case 'jump-question':
        var val = parseInt(document.getElementById('jump-input').value);
        if (val >= 1 && val <= (state.resultOnlyWrong ? state.examResult.questions.filter(function(q){return !q.correct;}).length : state.examResult.questions.length)) {
          state.resultIndex = val - 1;
          renderResult();
        } else {
          Util.showToast('题号超出范围');
        }
        break;"""
content = content.replace(old_action2, new_action2)

# 加导航CSS
old_css = """.analysis-explain {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 13px;
  color: var(--gray-600);
  line-height: 1.6;
}"""
new_css = """.analysis-explain {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 13px;
  color: var(--gray-600);
  line-height: 1.6;
}

/* 结果页题号导航 */
.nav-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: #f3f4f6;
  color: #6b7280;
}
.nav-item.nav-correct {
  background: #dcfce7;
  color: #16a34a;
}
.nav-item.nav-wrong {
  background: #fee2e2;
  color: #dc2626;
}
.nav-item.nav-current {
  outline: 2px solid #3b82f6;
  outline-offset: 1px;
}"""
content = content.replace(old_css, new_css)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

# 保存CSS到style.css
with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(old_css, new_css)

with open('css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('done')
