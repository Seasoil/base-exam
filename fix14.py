with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 初始化时，如果有学号，从云端拉取该学生的所有成绩
old_init = """    // 从云端拉取学生名单
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

new_init = """    // 从云端拉取学生名单
      Cloud.fetchStudentList().then(function(students) {
        if (students && students.length > 0) {
          state.studentList = students.map(function(s) {
            return { studentId: s.student_id, name: s.name, clazz: s.clazz || '' };
          });
          Storage.set('student_list', state.studentList);
          renderPage(currentPage);
        }
      }).catch(function() {});

      // 如果已有学号，从云端拉取该学生的历史成绩
      if (state.userInfo && state.userInfo.studentId) {
        Cloud.fetchRecordsByStudent(state.userInfo.studentId).then(function(records) {
          if (records && records.length > 0) {
            // 映射字段
            var mapped = records.map(function(r) {
              return {
                studentId: r.student_id,
                name: r.name,
                score: r.score,
                correctCount: r.correct_count,
                totalCount: r.total_count,
                duration: r.duration,
                submitTime: r.submit_time,
                isTimeout: r.is_timeout,
                blurCount: r.blur_count
              };
            });
            Storage.set('my_scores', mapped);
            renderPage(currentPage);
          }
        }).catch(function() {});
      }
    }"""

content = content.replace(old_init, new_init)

# 修改"我的考试记录"从云端拉
old_my_records = """function showMyRecords() {
    var scores = Storage.get('my_scores', []);"""

new_my_records = """function showMyRecords() {
    var scores = Storage.get('my_scores', []);
    // 同时从云端拉最新的
    if (Cloud.isConfigured() && state.userInfo && state.userInfo.studentId) {
      Cloud.fetchRecordsByStudent(state.userInfo.studentId).then(function(records) {
        if (records && records.length > 0) {
          var mapped = records.map(function(r) {
            return {
              studentId: r.student_id,
              name: r.name,
              score: r.score,
              correctCount: r.correct_count,
              totalCount: r.total_count,
              duration: r.duration,
              submitTime: r.submit_time,
              isTimeout: r.is_timeout,
              blurCount: r.blur_count
            };
          });
          Storage.set('my_scores', mapped);
          renderPage('my-records');
        }
      }).catch(function() {});
    }"""

content = content.replace(old_my_records, new_my_records)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
