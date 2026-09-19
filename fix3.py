with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改renderAdminStudents，加手动添加和班级
old_admin = """  function renderAdminStudents() {
    var list = state.studentList;
    var listHtml = '';

    if (list.length === 0) {
      listHtml = '<div class="empty"><div class="empty-icon">👥</div><div>暂无学生名单</div><div style="font-size:12px;margin-top:8px;">导入名单后，学生需通过学号+姓名校验才能进入考试</div></div>';
    } else {
      list.forEach(function(s, idx) {
        listHtml +=
          '<div class="student-row">' +
            '<div class="student-idx">' + (idx + 1) + '</div>' +
            '<div class="student-info"><div class="student-sid">' + s.studentId + '</div><div class="student-sname">' + s.name + '</div></div>' +
          '</div>';
      });
    }

    document.getElementById('admin-students-content').innerHTML =
      '<div class="admin-header">' +
        '<div class="admin-title">学生名单管理</div>' +
        '<div class="admin-logout" data-action="go-admin">返回</div>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">名单导入</div>' +
        '<div class="card-desc">导入CSV格式名单，第一列学号，第二列姓名。导入后学生必须在名单中且姓名匹配才能考试。</div>' +
        '<input type="file" id="student-file-input" accept=".csv,.txt" style="display:none;" onchange="window.App.handleStudentFile(this)">' +
        '<button class="btn btn-primary mt-16" onclick="document.getElementById(\'student-file-input\').click()">📁 选择CSV文件导入</button>' +
        '<button class="btn btn-secondary mt-16" data-action="download-template">下载CSV模板</button>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title-row"><div class="card-title" style="margin:0;">学生名单</div><div class="count-badge">' + list.length + ' 人</div></div>' +
        listHtml +
      '</div>' +

      (list.length > 0 ?
        '<button class="btn btn-danger" data-action="clear-student-list">清空学生名单</button>' : '') +

      '<div class="warning-card" style="margin-top:16px;">' +
        '<div class="warning-title">💡 使用说明</div>' +
        '<div class="warning-item">1. 名单为空时，不校验学生身份，任何人都可以考试。</div>' +
        '<div class="warning-item">2. 导入名单后，学生输入学号会自动匹配姓名，不在名单中无法考试。</div>' +
        '<div class="warning-item">3. 防替考功能自动启用：一台设备绑定一名考生，换设备需联系老师。</div>' +
      '</div>';
  }"""

new_admin = """  function renderAdminStudents() {
    var list = state.studentList;
    // 获取所有班级
    var classSet = {};
    list.forEach(function(s) { if (s.clazz) classSet[s.clazz] = true; });
    var classOptions = Object.keys(classSet);

    var listHtml = '';
    if (list.length === 0) {
      listHtml = '<div class="empty"><div class="empty-icon">👥</div><div>暂无学生名单</div></div>';
    } else {
      list.forEach(function(s, idx) {
        listHtml +=
          '<div class="student-row">' +
            '<div class="student-idx">' + (idx + 1) + '</div>' +
            '<div class="student-info">' +
              '<div class="student-sid">' + s.studentId + '</div>' +
              '<div class="student-sname">' + s.name + (s.clazz ? ' · ' + s.clazz : '') + '</div>' +
            '</div>' +
          '</div>';
      });
    }

    var classOptsHtml = classOptions.map(function(c) {
      return '<option value="' + c + '">' + c + '</option>';
    }).join('');

    document.getElementById('admin-students-content').innerHTML =
      '<div class="admin-header">' +
        '<div class="admin-title">学生名单管理</div>' +
        '<div class="admin-logout" data-action="go-admin">返回</div>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">手动添加学生</div>' +
        '<div class="form-group"><label class="form-label">学号</label><input class="form-input" type="text" id="add-sid" placeholder="请输入学号"></div>' +
        '<div class="form-group"><label class="form-label">姓名</label><input class="form-input" type="text" id="add-sname" placeholder="请输入姓名"></div>' +
        '<div class="form-group"><label class="form-label">班级</label><input class="form-input" type="text" id="add-sclass" placeholder="请输入班级名，如：计科2401"></div>' +
        '<button class="btn btn-primary mt-16" data-action="add-student">➕ 添加学生</button>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">批量导入</div>' +
        '<div class="card-desc">CSV格式：学号,姓名,班级</div>' +
        '<input type="file" id="student-file-input" accept=".csv,.txt" style="display:none;" onchange="window.App.handleStudentFile(this)">' +
        '<button class="btn btn-primary mt-16" onclick="document.getElementById(\'student-file-input\').click()">📁 选择CSV文件导入</button>' +
        '<button class="btn btn-secondary mt-16" data-action="download-template">下载CSV模板</button>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title-row"><div class="card-title" style="margin:0;">学生名单</div><div class="count-badge">' + list.length + ' 人</div></div>' +
        listHtml +
      '</div>' +

      (list.length > 0 ?
        '<button class="btn btn-danger" data-action="clear-student-list">清空学生名单</button>' : '') +

      '<div class="warning-card" style="margin-top:16px;">' +
        '<div class="warning-title">💡 使用说明</div>' +
        '<div class="warning-item">1. 名单为空时，不校验学生身份，任何人都可以考试。</div>' +
        '<div class="warning-item">2. 学生输入学号会自动匹配姓名和班级，不在名单中无法考试。</div>' +
        '<div class="warning-item">3. 防替考功能自动启用：一台设备绑定一名考生。</div>' +
      '</div>';
  }"""

content = content.replace(old_admin, new_admin)

# 2. 加add-student动作
old_action = "case 'show-qrcode': showQRCode(); break;"
new_action = """case 'show-qrcode': showQRCode(); break;
      case 'add-student': addStudent(); break;"""
content = content.replace(old_action, new_action)

# 3. 加addStudent函数
old_clear = "function clearStudentList() {"
new_add = """function addStudent() {
    var sid = document.getElementById('add-sid').value.trim();
    var name = document.getElementById('add-sname').value.trim();
    var clazz = document.getElementById('add-sclass').value.trim();
    if (!sid || !name) {
      Util.showToast('请填写学号和姓名');
      return;
    }
    // 检查是否已存在
    var exists = state.studentList.find(function(s) { return s.studentId === sid; });
    if (exists) {
      Util.showToast('该学号已存在');
      return;
    }
    state.studentList.push({ studentId: sid, name: name, clazz: clazz });
    Storage.set('student_list', state.studentList);
    Util.showToast('添加成功', 'success');
    renderAdminStudents();
  }

  function clearStudentList() {"""
content = content.replace(old_clear, new_add)

# 4. 修改CSV模板，加班级列
old_template = "var csv = '\\uFEFF' + '学号,姓名\\n2024001,张三\\n2024002,李四\\n2024003,王五';"
new_template = "var csv = '\\uFEFF' + '学号,姓名,班级\\n2024001,张三,计科2401\\n2024002,李四,计科2401\\n2024003,王五,软工2401';"
content = content.replace(old_template, new_template)

# 5. 修改CSV解析，支持班级列
old_parse = "var parts = line.split(/[,，\\t]/);\n        if (parts.length >= 2) {\n          var sid = parts[0].trim();\n          var name = parts[1].trim();"
new_parse = "var parts = line.split(/[,，\\t]/);\n        if (parts.length >= 2) {\n          var sid = parts[0].trim();\n          var name = parts[1].trim();\n          var clazz = parts[2] ? parts[2].trim() : '';"
content = content.replace(old_parse, new_parse)

# 6. 修改学生列表push，加班级
old_push = "students.push({ studentId: sid, name: name });"
new_push = "students.push({ studentId: sid, name: name, clazz: clazz });"
content = content.replace(old_push, new_push)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
