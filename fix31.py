with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 去掉批量粘贴导入卡片，保留手动添加
old = """      '<div class="card">' +
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

new = """      '<div class="card">' +
        '<div class="card-title">手动添加学生</div>' +
        '<div class="card-desc">文件导入后，漏掉的学生可以在这里单个添加</div>' +
        '<div class="form-row">' +
          '<div class="form-group flex-1"><label class="form-label">学号</label><input class="form-input" type="text" id="add-sid" placeholder="学号"></div>' +
          '<div class="form-group flex-1"><label class="form-label">姓名</label><input class="form-input" type="text" id="add-sname" placeholder="姓名"></div>' +
        '</div>' +
        '<div class="form-group"><label class="form-label">班级</label><input class="form-input" type="text" id="add-sclass" placeholder="班级，如：计科2401"></div>' +
        '<button class="btn btn-primary mt-16" data-action="add-student">➕ 添加学生</button>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">CSV文件导入</div>' +
        '<div class="card-desc">导入CSV格式名单，列：学号,姓名,班级</div>' +
        '<input type="file" id="student-file-input" accept=".csv,.txt" style="display:none;" onchange="window.App.handleStudentFile(this)">' +
        '<button class="btn btn-primary mt-16" onclick="document.getElementById(\\'student-file-input\\').click()">📁 选择CSV文件导入</button>' +
        '<button class="btn btn-secondary mt-16" data-action="download-template">下载CSV模板</button>' +
      '</div>'"""

content = content.replace(old, new)

# 2. 修复班级校验 - 检查班级输入框有没有正确绑定
old_class_input = """      case 'student-class':
        state.userInfo.clazz = value;
        break;"""
new_class_input = """      case 'student-class':
        state.userInfo.clazz = value.trim();
        break;"""
content = content.replace(old_class_input, new_class_input)

# 3. 确保userInfo初始化时有clazz字段
old_init_user = """    state.userInfo = Storage.get('userInfo', null);"""
new_init_user = """    state.userInfo = Storage.get('userInfo', null);
    if (state.userInfo && !state.userInfo.clazz) state.userInfo.clazz = '';"""
content = content.replace(old_init_user, new_init_user)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
