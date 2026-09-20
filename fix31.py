with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复班级输入初始化
old = """      case 'student-class':
        state.userInfo.clazz = value;
        break;"""
new = """      case 'student-class':
        if (!state.userInfo) state.userInfo = { studentId: '', name: '', clazz: '' };
        state.userInfo.clazz = value.trim();
        break;"""
content = content.replace(old, new)

# 2. 把批量粘贴改成三个输入框
old_batch = """      '<div class="card">' +
        '<div class="card-title">批量粘贴导入</div>' +
        '<div class="card-desc">每行一个学生，格式：学号 姓名 班级（用空格或逗号分隔），班级可留空</div>' +
        '<textarea id="batch-students" rows="6" class="form-input" style="width:100%;font-family:monospace;font-size:13px;resize:vertical;" placeholder="2024001 张三 计科2401\\n2024002 李四 计科2401\\n2024003 王五 软工2401"></textarea>' +
        '<button class="btn btn-primary mt-16" data-action="batch-import">📋 批量导入</button>' +
      '</div>' +"""

new_batch = """      '<div class="card">' +
        '<div class="card-title">手动添加学生</div>' +
        '<div class="card-desc">用于补充漏掉的个别学生，填写后点添加</div>' +
        '<div class="form-group"><label class="form-label">学号</label><input class="form-input" type="text" id="add-sid" placeholder="请输入学号"></div>' +
        '<div class="form-group"><label class="form-label">姓名</label><input class="form-input" type="text" id="add-sname" placeholder="请输入姓名"></div>' +
        '<div class="form-group"><label class="form-label">班级</label><input class="form-input" type="text" id="add-sclass" placeholder="请输入班级，如：计科2401"></div>' +
        '<button class="btn btn-primary mt-16" data-action="add-student">➕ 添加学生</button>' +
      '</div>' +"""

content = content.replace(old_batch, new_batch)

# 3. 名单校验也校验班级（如果名单里有班级）
old_check = """      // 校验姓名是否匹配
      if (matched.name !== state.userInfo.name) {
        Util.showToast('姓名与学号不匹配，请检查');
        return;
      }
    }"""

new_check = """      // 校验姓名是否匹配
      if (matched.name !== state.userInfo.name) {
        Util.showToast('姓名与学号不匹配，请检查');
        return;
      }
      // 如果名单里有班级，校验班级是否匹配
      if (matched.clazz && state.userInfo.clazz && matched.clazz !== state.userInfo.clazz) {
        Util.showToast('班级与学号不匹配，请检查');
        return;
      }
    }"""

content = content.replace(old_check, new_check)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
