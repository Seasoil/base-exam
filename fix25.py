with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改startExam，加继续进度检查
old = """    Util.showModal('开始考试',
      '本次考试共 ' + config.totalQuestions + ' 题，时长 ' + config.duration + ' 分钟。\\n\\n' +
      '⚠️ 考试期间请不要切换到其他应用或页面，切屏将被记录。\\n\\n确定要开始吗？',
      '开始考试').then(function(confirmed) {
      if (!confirmed) return;

      // 生成试卷
      var paper = Converter.generatePaper(config.totalQuestions, {
        basicMax: config.basicMax,
        advancedMax: config.advancedMax,
        advancedRatio: config.advancedRatio,
        typeWeights: config.typeWeights
      });

      state.currentPaper = paper;
      state.currentIndex = 0;
      state.answers = new Array(paper.questions.length).fill('');
      state.marked = new Array(paper.questions.length).fill(false);
      state.endTime = Date.now() + config.duration * 60 * 1000;
      state.blurCount = 0;

      // 启动切屏监控
      AntiCheat.startMonitoring(function(count) {
        // 切屏回来警告
        state.blurCount = count;
        Util.showModal('考试警告',
          '考试期间请勿切换应用或页面，切屏行为已被记录。',
          '我知道了');
      });

      // 保存进度
      saveExamProgress();

      renderPage('exam');
    });
  }"""

new = """    // 检查是否有未完成的进度
    var keys = [];
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.indexOf('base_exam_exam_progress_') === 0) keys.push(k);
    }

    if (keys.length > 0) {
      // 有保存的进度，问是否继续
      var lastKey = keys[keys.length - 1];
      var progress = JSON.parse(localStorage.getItem(lastKey));
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {
        // 时间还有剩余，问是否继续
        Util.showModal('继续考试',
          '检测到你有未完成的考试进度：\\n' +
          '已完成 ' + (progress.currentIndex + 1) + '/' + (progress.answers ? progress.answers.length : '?') + ' 题\\n' +
          '剩余时间：' + Math.floor(remainTime / 60) + ' 分钟\\n\\n' +
          '要继续考试吗？',
          '继续考试', '重新开始').then(function(choice) {
          if (choice === 'confirm') {
            // 继续考试
            state.currentPaper = progress.paper;
            state.currentIndex = progress.currentIndex;
            state.answers = progress.answers;
            state.submittedAnswers = progress.submittedAnswers || [];
            state.currentScore = progress.currentScore || 0;
            state.startTime = progress.startTime;
            state.endTime = progress.endTime;
            state.blurCount = 0;

            // 启动切屏监控
            AntiCheat.startMonitoring(function(count) {
              state.blurCount = count;
              Util.showModal('考试警告',
                '考试期间请勿切换应用或页面，切屏行为已被记录。',
                '我知道了');
            });

            renderPage('exam');
          } else {
            // 重新开始
            startNewExam();
          }
        });
        return;
      } else {
        // 时间到了，清掉旧进度
        keys.forEach(function(k) { localStorage.removeItem(k); });
      }
    }

    startNewExam();
  }

  function startNewExam() {
    var config = state.examConfig;
    Util.showModal('开始考试',
      '本次考试共 ' + config.totalQuestions + ' 题，时长 ' + config.duration + ' 分钟。\\n\\n' +
      '⚠️ 考试期间请不要切换到其他应用或页面，切屏将被记录。\\n\\n确定要开始吗？',
      '开始考试').then(function(confirmed) {
      if (!confirmed) return;

      // 生成试卷
      var paper = Converter.generatePaper(config.totalQuestions, {
        basicMax: config.basicMax,
        advancedMax: config.advancedMax,
        advancedRatio: config.advancedRatio,
        typeWeights: config.typeWeights
      });

      state.currentPaper = paper;
      state.currentIndex = 0;
      state.answers = new Array(paper.questions.length).fill('');
      state.submittedAnswers = [];
      state.currentScore = 0;
      state.startTime = Date.now();
      state.endTime = Date.now() + config.duration * 60 * 1000;
      state.blurCount = 0;

      // 启动切屏监控
      AntiCheat.startMonitoring(function(count) {
        state.blurCount = count;
        Util.showModal('考试警告',
          '考试期间请勿切换应用或页面，切屏行为已被记录。',
          '我知道了');
      });

      // 保存进度
      saveExamProgress();

      renderPage('exam');
    });
  }"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
