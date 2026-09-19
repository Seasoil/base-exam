with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改学生首页，加班级下拉选择
old_home = """    var userInfoHtml = '';
    if (state.userInfo && state.userInfo.studentId) {
      userInfoHtml =
        '<div class="userinfo-display">' +
          '<div class="userinfo-row"><span class="userinfo-label">学号</span><span class="userinfo-value">' + state.userInfo.studentId + '</span></div>' +
          '<div class="userinfo-row"><span class="userinfo-label">姓名</span><span class="userinfo-value">' + state.userInfo.name + '</span></div>' +
          '<div class="userinfo-edit" data-action="edit-userinfo">修改信息</div>' +
        '</div>';
    } else {
      userInfoHtml =
        '<div class="form-group">' +
          '<label class="form-label">学号</label>' +
          '<input class="form-input" type="text" data-input="student-id" placeholder="请输入学号" maxlength="20" value="' + (state.userInfo ? state.userInfo.studentId || '' : '') + '">' +
        '</div>' +
        '<div class="form-group">' +
          '<label class="form-label">姓名</label>' +
          '<input class="form-input" type="text" data-input="student-name" placeholder="请输入姓名" maxlength="20" value="' + (state.userInfo ? state.userInfo.name || '' : '') + '">' +
        '</div>';
    }"""

new_home = """    var userInfoHtml = '';
    // 获取班级列表
    var classSet = {};
    state.studentList.forEach(function(s) { if (s.clazz) classSet[s.clazz] = true; });
    var classOptions = Object.keys(classSet);
    var classOptsHtml = '<option value="">请选择班级</option>' + classOptions.map(function(c) {
      return '<option value="' + c + '">' + c + '</option>';
    }).join('');

    if (state.userInfo && state.userInfo.studentId) {
      userInfoHtml =
        '<div class="userinfo-display">' +
          '<div class="userinfo-row"><span class="userinfo-label">学号</span><span class="userinfo-value">' + state.userInfo.studentId + '</span></div>' +
          '<div class="userinfo-row"><span class="userinfo-label">姓名</span><span class="userinfo-value">' + state.userInfo.name + '</span></div>' +
          (state.userInfo.clazz ? '<div class="userinfo-row"><span class="userinfo-label">班级</span><span class="userinfo-value">' + state.userInfo.clazz + '</span></div>' : '') +
          '<div class="userinfo-edit" data-action="edit-userinfo">修改信息</div>' +
        '</div>';
    } else {
      userInfoHtml =
        '<div class="form-group">' +
          '<label class="form-label">学号</label>' +
          '<input class="form-input" type="text" data-input="student-id" placeholder="请输入学号" maxlength="20" value="' + (state.userInfo ? state.userInfo.studentId || '' : '') + '">' +
        '</div>' +
        '<div class="form-group">' +
          '<label class="form-label">姓名</label>' +
          '<input class="form-input" type="text" data-input="student-name" placeholder="请输入姓名" maxlength="20" value="' + (state.userInfo ? state.userInfo.name || '' : '') + '">' +
        '</div>' +
        (classOptions.length > 0 ?
          '<div class="form-group">' +
            '<label class="form-label">班级</label>' +
            '<select class="form-input" data-input="student-class">' + classOptsHtml + '</select>' +
          '</div>' : '');
    }"""

content = content.replace(old_home, new_home)

# 加班级输入处理
old_input = "case 'student-name':"
new_input = """case 'student-class':
        state.userInfo.clazz = value;
        break;
      case 'student-name':"""
content = content.replace(old_input, new_input)

# 修改学号匹配时自动填班级
old_match = """if (matched) {
            state.userInfo.name = matched.name;
            // 更新姓名输入框
            var nameInput = document.querySelector('[data-input="student-name"]');
            if (nameInput) nameInput.value = matched.name;
          }"""
new_match = """if (matched) {
            state.userInfo.name = matched.name;
            state.userInfo.clazz = matched.clazz || '';
            // 更新姓名输入框
            var nameInput = document.querySelector('[data-input="student-name"]');
            if (nameInput) nameInput.value = matched.name;
            // 更新班级下拉
            var classInput = document.querySelector('[data-input="student-class"]');
            if (classInput) classInput.value = matched.clazz || '';
          }"""
content = content.replace(old_match, new_match)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
