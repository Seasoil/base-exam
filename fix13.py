with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 初始化时从云端拉取学生名单
old_init = """    // 从云端拉取最新配置
    if (Cloud.isConfigured()) {
      Cloud.fetchExamConfig().then(function(res) {
        if (res && res.length > 0 && res[0].data) {
          var cloudConfig = JSON.parse(res[0].data);
          state.examConfig = cloudConfig;
          Storage.set('exam_config', cloudConfig);
          renderPage(currentPage);
        }
      }).catch(function() {});
    }"""

new_init = """    // 从云端拉取最新配置
    if (Cloud.isConfigured()) {
      Cloud.fetchExamConfig().then(function(res) {
        if (res && res.length > 0 && res[0].data) {
          var cloudConfig = JSON.parse(res[0].data);
          state.examConfig = cloudConfig;
          Storage.set('exam_config', cloudConfig);
          renderPage(currentPage);
        }
      }).catch(function() {});

      // 从云端拉取学生名单
      Cloud.fetchStudentList().then(function(students) {
        if (students && students.length > 0) {
          state.studentList = students.map(function(s) {
            return { studentId: s.student_id, name: s.name, clazz: s.clazz || '' };
          });
          Storage.set('student_list', state.studentList);
          renderPage(currentPage);
        }
      }).catch(function() {});
    }"""

content = content.replace(old_init, new_init)

# 2. 保存学生名单时同步到云端
old_save_list = "state.studentList.push({ studentId: sid, name: name, clazz: clazz });"
new_save_list = """state.studentList.push({ studentId: sid, name: name, clazz: clazz });
    // 同步到云端
    if (Cloud.isConfigured()) {
      Cloud.uploadStudentList([{ studentId: sid, name: name, clazz: clazz }]).catch(function() {});
    }"""
content = content.replace(old_save_list, new_save_list)

# 3. 清空名单时同步到云端
old_clear = "state.studentList = [];"
new_clear = """state.studentList = [];
    // 同步清空云端
    if (Cloud.isConfigured()) {
      Cloud.clearStudentList().catch(function() {});
    }"""
# 只替换第一个
content = content.replace(old_clear, new_clear, 1)

# 4. CSV导入后同步到云端
old_csv = "state.studentList = students;"
new_csv = """state.studentList = students;
    // 同步到云端
    if (Cloud.isConfigured()) {
      Cloud.clearStudentList().then(function() {
        Cloud.uploadStudentList(students).catch(function() {});
      }).catch(function() {});
    }"""
content = content.replace(old_csv, new_csv)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
