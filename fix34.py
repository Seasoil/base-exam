with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改继续考试弹窗，用自定义弹窗
old = """    if (progress) {
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
        Storage.remove('exam_progress');
      }
    }

    if (!progress || Math.floor((progress.endTime - Date.now()) / 1000) <= 0) {
      startNewExam();
    }
  }"""

new = """    if (progress) {
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {
        // 自定义弹窗：继续 / 重新开始
        var mask = document.createElement('div');
        mask.className = 'modal-mask';
        mask.innerHTML =
          '<div class="modal-box">' +
            '<div class="modal-title">继续考试</div>' +
            '<div class="modal-text">检测到你有未完成的考试进度：</div>' +
            '<div class="modal-text" style="text-align:left;margin:12px 0;">' +
              '已完成 ' + (progress.currentIndex + 1) + '/' + (progress.answers ? progress.answers.length : '?') + ' 题<br>' +
              '剩余时间：' + Math.floor(remainTime / 60) + ' 分钟' +
            '</div>' +
            '<div style="display:flex;flex-direction:column;gap:10px;">' +
              '<button class="modal-btn modal-confirm" id="continue-btn">继续考试</button>' +
              '<button class="modal-btn modal-cancel" id="restart-btn">重新开始</button>' +
            '</div>' +
          '</div>';
        document.body.appendChild(mask);

        mask.querySelector('#continue-btn').onclick = function() {
          mask.remove();
          // 继续考试
          state.currentPaper = progress.paper;
          state.currentIndex = progress.currentIndex;
          state.answers = progress.answers;
          state.submittedAnswers = progress.submittedAnswers || [];
          state.currentScore = progress.currentScore || 0;
          state.startTime = progress.startTime;
          state.endTime = progress.endTime;
          state.blurCount = 0;

          AntiCheat.startMonitoring(function(count) {
            state.blurCount = count;
            Util.showModal('考试警告',
              '考试期间请勿切换应用或页面，切屏行为已被记录。',
              '我知道了');
          });

          renderPage('exam');
        };
        mask.querySelector('#restart-btn').onclick = function() {
          mask.remove();
          Storage.remove('exam_progress');
          startNewExam();
        };
        mask.onclick = function(e) { if (e.target === mask) mask.remove(); };
        return;
      } else {
        Storage.remove('exam_progress');
      }
    }

    startNewExam();
  }"""

content = content.replace(old, new)

# 修复保存进度退出后回到首页
old_exit = """    mask.querySelector('#exit-save-btn').onclick = function() {
      saveExamProgress();
      saveMidProgress();
      mask.remove();
      renderPage('home');
      Util.showToast('进度已保存，考试期间可继续');
    };"""

new_exit = """    mask.querySelector('#exit-save-btn').onclick = function() {
      saveExamProgress();
      saveMidProgress();
      mask.remove();
      state.currentPaper = null;
      renderPage('home');
      Util.showToast('进度已保存，考试期间可继续');
    };"""

content = content.replace(old_exit, new_exit)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
