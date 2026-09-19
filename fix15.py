with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改renderExam函数，改成逐题提交模式
old_render = """  function renderExam() {
    var paper = state.currentPaper;
    if (!paper) { renderPage('home'); return; }

    var q = paper.questions[state.currentIndex];
    var remaining = Math.max(0, Math.floor((state.endTime - Date.now()) / 1000));
    var answeredCount = state.answers.filter(function(a) { return a && a.trim() !== ''; }).length;

    // 构建答题卡
    var sheetHtml = '';
    for (var i = 0; i < paper.questions.length; i++) {
      var cls = 'sheet-item';
      if (state.answers[i] && state.answers[i].trim() !== '') cls += ' answered';
      else cls += ' unanswered';
      if (state.marked[i]) cls += ' marked';
      if (i === state.currentIndex) cls += ' current';
      sheetHtml += '<div class="' + cls + '" data-action="jump-question" data-index="' + i + '">' + (i + 1) + '</div>';
    }

    var isLast = state.currentIndex === paper.questions.length - 1;
    var nextBtnText = isLast ? '交卷' : '下一题';
    var nextBtnAction = isLast ? 'submit-exam' : 'next-question';

    document.getElementById('exam-content').innerHTML =
      '<div class="exam-topbar">' +
        '<div class="exam-topbar-left">第 ' + (state.currentIndex + 1) + ' / ' + paper.questions.length + ' 题</div>' +
        '<div class="exam-topbar-center ' + (remaining <= 60 ? 'time-warning' : '') + '">⏱ ' + Util.formatDuration(remaining) + '</div>' +
        '<div class="exam-topbar-right" data-action="toggle-sheet">答题卡 <span class="sheet-count">' + answeredCount + '/' + paper.questions.length + '</span></div>' +
      '</div>' +

      '<div class="exam-question-area">' +
        '<div class="question-card">' +
          '<div class="question-type-tags">' +
            '<span class="tag tag-blue">' + q.typeName + '</span>' +
            (state.marked[state.currentIndex] ? '<span class="tag tag-orange">已标记</span>' : '') +
          '</div>' +
          '<div class="question-text">' + q.question + '</div>' +
          '<div class="source-value-box">' +
            '<span class="source-label">原数：</span>' +
            '<span class="source-num">' + q.sourceValue + '</span>' +
            '<span class="source-base">(' + q.fromBase + '进制)</span>' +
          '</div>' +
          '<div class="answer-input-area">' +
            '<label class="answer-label">请输入答案（' + q.toBase + '进制）</label>' +
            '<input class="answer-input" type="text" data-input="exam-answer" placeholder="在此输入答案" value="' + (state.answers[state.currentIndex] || '') + '" autofocus>' +
            (q.padLength > 0 ? '<div class="answer-hint">提示：结果需为 ' + q.padLength + ' 位，不足请补前导零</div>' : '') +
            (q.toBase === 16 ? '<div class="answer-hint">提示：十六进制字母请使用大写（A-F）</div>' : '') +
          '</div>' +
        '</div>' +
      '</div>' +

      '<div class="exam-bottombar">' +
        '<button class="btn btn-footer ' + (state.currentIndex === 0 ? 'disabled' : '') + '" data-action="prev-question">上一题</button>' +
        '<button class="btn btn-footer btn-mark" data-action="toggle-mark">' + (state.marked[state.currentIndex] ? '取消标记' : '标记此题') + '</button>' +
        '<button class="btn btn-footer btn-next" data-action="' + nextBtnAction + '">' + nextBtnText + '</button>' +
      '</div>' +

      '<div class="sheet-mask" id="sheet-mask" style="display:none;">' +
        '<div class="sheet-panel">' +
          '<div class="sheet-header"><span>答题卡</span><span class="sheet-close" data-action="toggle-sheet">✕</span></div>' +
          '<div class="sheet-stats">' +
            '<span><span class="dot dot-answered"></span>已答 ' + answeredCount + '</span>' +
            '<span><span class="dot dot-unanswered"></span>未答 ' + (paper.questions.length - answeredCount) + '</span>' +
            '<span><span class="dot dot-marked"></span>标记 ' + state.marked.filter(function(m) { return m; }).length + '</span>' +
          '</div>' +
          '<div class="sheet-grid">' + sheetHtml + '</div>' +
          '<div class="sheet-footer"><button class="btn btn-primary" data-action="submit-exam">交卷</button></div>' +
        '</div>' +
      '</div>';

    // 聚焦输入框
    setTimeout(function() {
      var input = document.querySelector('.answer-input');
      if (input) input.focus();
    }, 100);

    // 启动计时
    if (state._examTimer) clearInterval(state._examTimer);
    state._examTimer = setInterval(function() {
      if (state.currentPage !== 'exam') return;
      var rem = Math.max(0, Math.floor((state.endTime - Date.now()) / 1000));
      var timeEl = document.querySelector('.exam-topbar-center');
      if (timeEl) {
        timeEl.textContent = '⏱ ' + Util.formatDuration(rem);
        if (rem <= 60) timeEl.classList.add('time-warning');
      }
      if (rem <= 0) {
        clearInterval(state._examTimer);
        autoSubmit();
      }
    }, 1000);
  }"""

new_render = """  function renderExam() {
    var paper = state.currentPaper;
    if (!paper) { renderPage('home'); return; }

    var q = paper.questions[state.currentIndex];
    var remaining = Math.max(0, Math.floor((state.endTime - Date.now()) / 1000));
    var answeredCount = state.submittedCount || 0;
    var isSubmitted = state.submittedAnswers && state.submittedAnswers[state.currentIndex];

    // 累计得分
    var totalScore = state.currentScore || 0;

    // 构建答题卡（只能看不能点）
    var sheetHtml = '';
    for (var i = 0; i < paper.questions.length; i++) {
      var cls = 'sheet-item';
      if (state.submittedAnswers && state.submittedAnswers[i]) {
        cls += state.submittedAnswers[i].correct ? ' answered' : ' wrong';
      } else {
        cls += ' unanswered';
      }
      if (i === state.currentIndex) cls += ' current';
      sheetHtml += '<div class="' + cls + '">' + (i + 1) + '</div>';
    }

    var isLast = state.currentIndex === paper.questions.length - 1;

    // 解析内容
    var analysisHtml = '';
    if (isSubmitted) {
      var sa = state.submittedAnswers[state.currentIndex];
      var correctClass = sa.correct ? 'correct' : 'wrong';
      var correctIcon = sa.correct ? '✅ 回答正确' : '❌ 回答错误';
      analysisHtml =
        '<div class="analysis-box ' + correctClass + '">' +
          '<div class="analysis-title">' + correctIcon + '</div>' +
          '<div class="analysis-item">你的答案：<span class="your-answer">' + (sa.userAnswer || '空') + '</span></div>' +
          '<div class="analysis-item">正确答案：<span class="right-answer">' + q.correctAnswer + '</span></div>' +
          '<div class="analysis-item">本题得分：' + (sa.correct ? (100 / paper.questions.length).toFixed(1) : 0) + ' 分</div>' +
          '<div class="analysis-explain">解析：' + q.question + '，从 ' + q.fromBase + ' 进制转换为 ' + q.toBase + ' 进制，结果为 ' + q.correctAnswer + '</div>' +
        '</div>';
    }

    document.getElementById('exam-content').innerHTML =
      '<div class="exam-topbar">' +
        '<div class="exam-topbar-left">第 ' + (state.currentIndex + 1) + ' / ' + paper.questions.length + ' 题</div>' +
        '<div class="exam-topbar-center ' + (remaining <= 60 ? 'time-warning' : '') + '">⏱ ' + Util.formatDuration(remaining) + '</div>' +
        '<div class="exam-topbar-right">累计 <span style="color:#22c55e;font-weight:600;">' + totalScore.toFixed(1) + '</span> 分</div>' +
      '</div>' +

      '<div class="exam-question-area">' +
        '<div class="question-card">' +
          '<div class="question-type-tags">' +
            '<span class="tag tag-blue">' + q.typeName + '</span>' +
          '</div>' +
          '<div class="question-text">' + q.question + '</div>' +
          '<div class="source-value-box">' +
            '<span class="source-label">原数：</span>' +
            '<span class="source-num">' + q.sourceValue + '</span>' +
            '<span class="source-base">(' + q.fromBase + '进制)</span>' +
          '</div>' +
          (isSubmitted ? '' :
          '<div class="answer-input-area">' +
            '<label class="answer-label">请输入答案（' + q.toBase + '进制）</label>' +
            '<input class="answer-input" type="text" data-input="exam-answer" placeholder="在此输入答案" value="' + (state.answers[state.currentIndex] || '') + '" autofocus>' +
            (q.padLength > 0 ? '<div class="answer-hint">提示：结果需为 ' + q.padLength + ' 位，不足请补前导零</div>' : '') +
            (q.toBase === 16 ? '<div class="answer-hint">提示：十六进制字母请使用大写（A-F）</div>' : '') +
          '</div>') +
          analysisHtml +
        '</div>' +
      '</div>' +

      '<div class="exam-bottombar">' +
        (isSubmitted ?
          '<button class="btn btn-footer btn-next" data-action="' + (isLast ? 'submit-exam' : 'next-question') + '">' + (isLast ? '交卷' : '下一题') + '</button>'
          :
          '<button class="btn btn-footer btn-next btn-primary" data-action="submit-current">提交本题</button>'
        ) +
      '</div>' +

      '<div class="sheet-mask" id="sheet-mask" style="display:none;">' +
        '<div class="sheet-panel">' +
          '<div class="sheet-header"><span>答题卡</span><span class="sheet-close" data-action="toggle-sheet">✕</span></div>' +
          '<div class="sheet-stats">' +
            '<span><span class="dot dot-answered"></span>正确 ' + (state.submittedAnswers ? state.submittedAnswers.filter(function(a){return a&&a.correct;}).length : 0) + '</span>' +
            '<span><span class="dot dot-unanswered"></span>错误 ' + (state.submittedAnswers ? state.submittedAnswers.filter(function(a){return a&&!a.correct;}).length : 0) + '</span>' +
            '<span><span class="dot dot-marked"></span>未做 ' + (paper.questions.length - answeredCount) + '</span>' +
          '</div>' +
          '<div class="sheet-grid">' + sheetHtml + '</div>' +
        '</div>' +
      '</div>';

    // 聚焦输入框
    if (!isSubmitted) {
      setTimeout(function() {
        var input = document.querySelector('.answer-input');
        if (input) input.focus();
      }, 100);
    }

    // 启动计时
    if (state._examTimer) clearInterval(state._examTimer);
    state._examTimer = setInterval(function() {
      if (state.currentPage !== 'exam') return;
      var rem = Math.max(0, Math.floor((state.endTime - Date.now()) / 1000));
      var timeEl = document.querySelector('.exam-topbar-center');
      if (timeEl) {
        timeEl.textContent = '⏱ ' + Util.formatDuration(rem);
        if (rem <= 60) timeEl.classList.add('time-warning');
      }
      if (rem <= 0) {
        clearInterval(state._examTimer);
        autoSubmit();
      }
    }, 1000);
  }"""

content = content.replace(old_render, new_render)

# 加submitCurrent函数
old_next = """  function nextQuestion() {
    if (state.currentIndex < state.currentPaper.questions.length - 1) {
      state.currentIndex++;
      saveExamProgress();
      renderExam();
    }
  }"""

new_next = """  function nextQuestion() {
    if (state.currentIndex < state.currentPaper.questions.length - 1) {
      state.currentIndex++;
      saveExamProgress();
      renderExam();
    }
  }

  // 提交当前题，即时判题
  function submitCurrent() {
    var paper = state.currentPaper;
    var q = paper.questions[state.currentIndex];
    var userAnswer = (state.answers[state.currentIndex] || '').trim().toUpperCase();
    var correctAnswer = q.correctAnswer.toUpperCase();
    var correct = userAnswer === correctAnswer;

    // 初始化数组
    if (!state.submittedAnswers) state.submittedAnswers = [];
    if (typeof state.currentScore !== 'number') state.currentScore = 0;

    // 记录本题结果
    state.submittedAnswers[state.currentIndex] = {
      userAnswer: userAnswer,
      correct: correct
    };

    // 累计得分
    if (correct) state.currentScore += 100 / paper.questions.length;

    // 更新已提交计数
    state.submittedCount = state.submittedAnswers.filter(function(a) { return a; }).length;

    saveExamProgress();
    renderExam();
  }"""

content = content.replace(old_next, new_next)

# 加submit-current动作
old_action = "case 'next-question': nextQuestion(); break;"
new_action = """case 'next-question': nextQuestion(); break;
      case 'submit-current': submitCurrent(); break;"""
content = content.replace(old_action, new_action)

# 删除prevQuestion动作
old_prev = "case 'prev-question': prevQuestion(); break;"
new_prev = ""
content = content.replace(old_prev, new_prev)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
