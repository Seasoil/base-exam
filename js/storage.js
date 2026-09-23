/**
 * 本地存储封装 + 通用工具函数（H5版）
 */
window.Storage = (function() {
  var PREFIX = 'base_exam_';

  function get(key, defaultValue) {
    try {
      var val = localStorage.getItem(PREFIX + key);
      if (val === null) return defaultValue;
      return JSON.parse(val);
    } catch (e) {
      return defaultValue;
    }
  }

  function set(key, value) {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
      return true;
    } catch (e) {
      return false;
    }
  }

  function remove(key) {
    try {
      localStorage.removeItem(PREFIX + key);
      return true;
    } catch (e) {
      return false;
    }
  }

  function clearAll() {
    try {
      var keys = [];
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (k && k.indexOf(PREFIX) === 0) keys.push(k);
      }
      keys.forEach(function(k) { localStorage.removeItem(k); });
      return true;
    } catch (e) {
      return false;
    }
  }

  return { get: get, set: set, remove: remove, clearAll: clearAll };
})();

window.Util = (function() {
  function formatTime(timestamp, format) {
    format = format || 'YYYY-MM-DD HH:mm:ss';
    var d = new Date(timestamp);
    var pad = function(n) { return String(n).padStart(2, '0'); };
    return format
      .replace('YYYY', d.getFullYear())
      .replace('MM', pad(d.getMonth() + 1))
      .replace('DD', pad(d.getDate()))
      .replace('HH', pad(d.getHours()))
      .replace('mm', pad(d.getMinutes()))
      .replace('ss', pad(d.getSeconds()));
  }

  function formatDuration(seconds) {
    seconds = Math.max(0, Math.floor(seconds));
    var h = Math.floor(seconds / 3600);
    var m = Math.floor((seconds % 3600) / 60);
    var s = seconds % 60;
    var pad = function(n) { return String(n).padStart(2, '0'); };
    if (h > 0) return pad(h) + ':' + pad(m) + ':' + pad(s);
    return pad(m) + ':' + pad(s);
  }

  function showToast(msg, type) {
    type = type || 'info';
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function() { toast.classList.add('show'); }, 10);
    setTimeout(function() {
      toast.classList.remove('show');
      setTimeout(function() { toast.remove(); }, 300);
    }, 2000);
  }

  function showModal(title, content, confirmText) {
    return new Promise(function(resolve) {
      var mask = document.createElement('div');
      mask.className = 'modal-mask';
      mask.innerHTML =
        '<div class="modal-box">' +
          '<div class="modal-title">' + title + '</div>' +
          '<div class="modal-content">' + content.replace(/\n/g, '<br>') + '</div>' +
          '<div class="modal-buttons">' +
            '<button class="modal-btn modal-cancel">取消</button>' +
            '<button class="modal-btn modal-confirm">' + (confirmText || '确定') + '</button>' +
          '</div>' +
        '</div>';
      document.body.appendChild(mask);
      mask.querySelector('.modal-cancel').onclick = function() { mask.remove(); resolve(false); };
      mask.querySelector('.modal-confirm').onclick = function() { mask.remove(); resolve(true); };
    });
  }

  function showPrompt(title, placeholder, confirmText) {
    return new Promise(function(resolve) {
      var mask = document.createElement('div');
      mask.className = 'modal-mask';
      mask.innerHTML =
        '<div class="modal-box">' +
          '<div class="modal-title">' + title + '</div>' +
          '<input class="form-input" id="prompt-input" type="password" placeholder="' + (placeholder || '') + '" style="margin:12px 0;">' +
          '<div class="modal-buttons">' +
            '<button class="modal-btn modal-cancel">取消</button>' +
            '<button class="modal-btn modal-confirm">' + (confirmText || '确定') + '</button>' +
          '</div>' +
        '</div>';
      document.body.appendChild(mask);
      var input = mask.querySelector('#prompt-input');
      if (input) input.focus();
      mask.querySelector('.modal-cancel').onclick = function() { mask.remove(); resolve(null); };
      mask.querySelector('.modal-confirm').onclick = function() { mask.remove(); resolve(input ? input.value : null); };
      mask.onclick = function(e) { if (e.target === mask) { mask.remove(); resolve(null); } };
      mask.querySelector('.modal-box').onclick = function(e) { e.stopPropagation(); };
    });
  }

  function validateStudentId(id) {
    return /^[A-Za-z0-9]{4,20}$/.test(id);
  }

  function validateName(name) {
    return name && name.trim().length >= 2 && name.trim().length <= 20;
  }

  function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  function exportCSV(scores) {
    var headers = ['学号', '姓名', '最高分', '最新分', '考试次数', '答题时长(秒)', '切屏次数', '设备型号', '最新提交时间'];
    var rows = scores.map(function(s) {
      return [
        s.studentId,
        s.name,
        s.maxScore,
        s.latestScore,
        s.examCount,
        s.latestDuration,
        s.maxBlurCount || 0,
        s.deviceModel || '未知',
        formatTime(s.latestSubmitTime)
      ];
    });
    var csv = '\uFEFF' + [headers].concat(rows).map(function(r) { return r.join(','); }).join('\n');
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = '成绩导出_' + formatTime(Date.now(), 'YYYYMMDD_HHmmss') + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return {
    formatTime: formatTime,
    formatDuration: formatDuration,
    showToast: showToast,
    showModal: showModal,
    showPrompt: showPrompt,
    validateStudentId: validateStudentId,
    validateName: validateName,
    generateId: generateId,
    exportCSV: exportCSV
  };
})();
