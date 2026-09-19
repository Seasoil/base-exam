with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改配置页，加时间选择和状态
old_config = """    document.getElementById('admin-config-content').innerHTML =
      '<div class="card"><div class="card-title">基础配置</div>' +
        '<div class="form-group"><label class="form-label">考试名称</label><input class="form-input" type="text" data-input="config-exam-name" value="' + config.examName + '"></div>' +
        '<div class="form-row">' +
          '<div class="form-group flex-1"><label class="form-label">题目数量</label><input class="form-input" type="number" data-input="config-total-questions" value="' + config.totalQuestions + '"></div>' +
          '<div class="form-group flex-1"><label class="form-label">考试时长(分钟)</label><input class="form-input" type="number" data-input="config-duration" value="' + config.duration + '"></div>' +
        '</div>' +
        '<div class="form-group switch-item"><label class="form-label">允许多次考试（刷分）</label><label class="switch"><input type="checkbox" ' + (config.allowRetake ? 'checked' : '') + ' onchange="window.App.toggleAllowRetake(this)"><span class="slider"></span></label></div>' +
      '</div>'"""

new_config = """    var statusText = config.status === 1 ? '进行中' : (config.status === 2 ? '已结束' : '未开启');
    var statusColor = config.status === 1 ? '#22c55e' : (config.status === 2 ? '#64748b' : '#ef4444');
    // 格式化时间
    function fmtTs(ts) {
      if (!ts) return '';
      var d = new Date(ts);
      var pad = function(n) { return n < 10 ? '0' + n : n; };
      return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + 'T' + pad(d.getHours()) + ':' + pad(d.getMinutes());
    }

    document.getElementById('admin-config-content').innerHTML =
      '<div class="card"><div class="card-title">考试状态</div>' +
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">' +
          '<div style="width:10px;height:10px;border-radius:50%;background:' + statusColor + ';"></div>' +
          '<div style="font-size:18px;font-weight:600;color:' + statusColor + ';">当前状态：' + statusText + '</div>' +
        '</div>' +
        '<button class="btn btn-primary" style="width:100%;" data-action="toggle-exam-status">' + (config.status === 1 ? '关闭考试' : '开启考试') + '</button>' +
      '</div>' +

      '<div class="card"><div class="card-title">定时设置</div>' +
        '<div class="form-group"><label class="form-label">开始时间</label><input class="form-input" type="datetime-local" data-input="config-start-time" value="' + fmtTs(config.startTime) + '"></div>' +
        '<div class="form-group"><label class="form-label">结束时间</label><input class="form-input" type="datetime-local" data-input="config-end-time" value="' + fmtTs(config.endTime) + '"></div>' +
        '<div class="card-desc" style="margin-top:8px;">设置后，在时间段内学生可以进入考试，超时自动结束。留空则手动控制开关。</div>' +
      '</div>' +

      '<div class="card"><div class="card-title">基础配置</div>' +
        '<div class="form-group"><label class="form-label">考试名称</label><input class="form-input" type="text" data-input="config-exam-name" value="' + config.examName + '"></div>' +
        '<div class="form-row">' +
          '<div class="form-group flex-1"><label class="form-label">题目数量</label><input class="form-input" type="number" data-input="config-total-questions" value="' + config.totalQuestions + '"></div>' +
          '<div class="form-group flex-1"><label class="form-label">考试时长(分钟)</label><input class="form-input" type="number" data-input="config-duration" value="' + config.duration + '"></div>' +
        '</div>' +
        '<div class="form-group switch-item"><label class="form-label">允许多次考试（刷分）</label><label class="switch"><input type="checkbox" ' + (config.allowRetake ? 'checked' : '') + ' onchange="window.App.toggleAllowRetake(this)"><span class="slider"></span></label></div>' +
      '</div>'"""

content = content.replace(old_config, new_config)

# 加toggle-exam-status动作
old_action = "case 'toggle-admin':"
new_action = """case 'toggle-exam-status': toggleExamStatus(); break;
      case 'toggle-admin':"""
content = content.replace(old_action, new_action)

# 加保存时间输入的处理
old_input = "case 'config-exam-name':"
new_input = """case 'config-start-time':
        state.examConfig.startTime = value ? new Date(value).getTime() : null;
        break;
      case 'config-end-time':
        state.examConfig.endTime = value ? new Date(value).getTime() : null;
        break;
      case 'config-exam-name':"""
content = content.replace(old_input, new_input)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
