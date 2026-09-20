with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改学生名单管理页，加批量粘贴导入
old = """      '<div class="card">' +
        '<div class="card-title">名单导入</div>' +
        '<div class="card-desc">导入CSV格式名单，第一列学号，第二列姓名。导入后学生必须在名单中且姓名匹配才能考试。</div>' +
        '<input type="file" id="student-file-input" accept=".csv,.txt" style="display:none;" onchange="window.App.handleStudentFile(this)">' +
        '<button class="btn btn-primary mt-16" onclick="document.getElementById(\\'student-file-input\\').click()">📁 选择CSV文件导入</button>' +
        '<button class="btn btn-secondary mt-16" data-action="download-template">下载CSV模板</button>' +
      '</div>'"""

new = """      '<div class="card">' +
        '<div class="card-title">批量粘贴导入</div>' +
        '<div class="card-desc">每行一个学生，格式：学号 姓名 班级（用空格或逗号分隔），班级可留空</div>' +
        '<textarea id="batch-students" rows="6" class="form-input" style="width:100%;font-family:monospace;font-size:13px;resize:vertical;" placeholder="2024001 张三 计科2401\\n2024002 李四 计科2401\\n2024003 王五 软工2401"></textarea>' +
        '<button class="btn btn-primary mt-16" data-action="batch-import">📋 批量导入</button>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">CSV文件导入</div>' +
        '<div class="card-desc">导入CSV格式名单，列：学号,姓名,班级</div>' +
        '<input type="file" id="student-file-input" accept=".csv,.txt" style="display:none;" onchange="window.App.handleStudentFile(this)">' +
        '<button class="btn btn-primary mt-16" onclick="document.getElementById(\\'student-file-input\\').click()">📁 选择CSV文件导入</button>' +
        '<button class="btn btn-secondary mt-16" data-action="download-template">下载CSV模板</button>' +
      '</div>'"""

content = content.replace(old, new)

# 加batch-import动作
old_action = "case 'add-student': addStudent(); break;"
new_action = """case 'add-student': addStudent(); break;
      case 'batch-import': batchImportStudents(); break;"""
content = content.replace(old_action, new_action)

# 加batchImportStudents函数
old_add = """  function addStudent() {"""

new_add = """  function batchImportStudents() {
    var text = document.getElementById('batch-students').value.trim();
    if (!text) {
      Util.showToast('请输入学生信息');
      return;
    }
    var lines = text.split('\\n');
    var added = 0;
    var skipped = 0;
    lines.forEach(function(line) {
      line = line.trim();
      if (!line) return;
      // 支持空格、逗号、制表符分隔
      var parts = line.split(/[\\s,，\\t]+/);
      if (parts.length >= 2) {
        var sid = parts[0].trim();
        var name = parts[1].trim();
        var clazz = parts[2] ? parts[2].trim() : '';
        var exists = state.studentList.find(function(s) { return s.studentId === sid; });
        if (!exists) {
          state.studentList.push({ studentId: sid, name: name, clazz: clazz });
          added++;
        } else {
          skipped++;
        }
      }
    });
    if (added > 0) {
      Storage.set('student_list', state.studentList);
      // 同步到云端
      if (Cloud.isConfigured()) {
        Cloud.clearStudentList().then(function() {
          Cloud.uploadStudentList(state.studentList).catch(function() {});
        }).catch(function() {});
      }
      Util.showToast('成功导入 ' + added + ' 人' + (skipped > 0 ? '，跳过重复 ' + skipped + ' 人' : ''), 'success');
      renderAdminStudents();
    } else {
      Util.showToast('没有新学生（可能都重复了）');
    }
  }

  function addStudent() {"""

content = content.replace(old_add, new_add)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
