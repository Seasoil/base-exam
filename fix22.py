with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改退出弹窗，三个按钮
old = """  // 退出考试弹窗
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
  }"""

new = """  // 退出考试弹窗
  function exitExam() {
    var mask = document.createElement('div');
    mask.className = 'modal-mask';
    mask.innerHTML =
      '<div class="modal-box">' +
        '<div class="modal-title">退出考试</div>' +
        '<div class="modal-text" style="margin-bottom:16px;">你确定要退出考试吗？</div>' +
        '<div style="display:flex;flex-direction:column;gap:10px;">' +
          '<button class="modal-btn modal-cancel" id="exit-back-btn">继续考试（返回）</button>' +
          '<button class="modal-btn modal-secondary" id="exit-save-btn">保存进度下次继续（有事情）</button>' +
          '<button class="modal-btn modal-danger" id="exit-confirm-btn">直接交卷</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(mask);
    // 继续考试
    mask.querySelector('#exit-back-btn').onclick = function() {
      mask.remove();
    };
    // 保存进度下次继续
    mask.querySelector('#exit-save-btn').onclick = function() {
      saveExamProgress();
      mask.remove();
      renderPage('home');
      Util.showToast('进度已保存，考试期间可继续');
    };
    // 直接交卷
    mask.querySelector('#exit-confirm-btn').onclick = function() {
      mask.remove();
      doSubmit();
    };
    mask.onclick = function(e) { if (e.target === mask) mask.remove(); };
  }"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
