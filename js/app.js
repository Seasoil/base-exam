/**
 * 进制转换在线考试 - 主应用逻辑（H5版）
 * 单页应用，通过页面切换实现多页面体验
 */
(function() {
  'use strict';
  // 硬编码云端配置
  if (window.Cloud) {
    Cloud.setConfig({ url: 'https://uazwtblpwayqlpczczai.supabase.co', anonKey: 'sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs' });
  }

  // ========== 全局状态 ==========
  var state = {
    currentPage: 'home',
    userInfo: null,
    examConfig: null,
    currentPaper: null,
    currentIndex: 0,
    answers: [],
    marked: [],
    timer: null,
    endTime: 0,
    examResult: null,
    isAdmin: false,
    adminSortBy: 'maxScore',
    adminSearchKeyword: '',
    titleClickCount: 0,
    // 防作弊相关
    deviceInfo: null,
    blurCount: 0,
    studentList: [], // 学生名单 [{studentId, name}]
    activeExams: []  // 正在考试的学生（本地模式下为模拟数据）
  };

  // 默认考试配置
  var DEFAULT_CONFIG = {
    examName: '进制转换在线考试',
    startTime: null,
    endTime: null,
    duration: 30,
    totalQuestions: 100,
    allowRetake: true,
    basicMax: 255,
    advancedMax: 1024,
    advancedRatio: 0.3,
    typeWeights: {},
    status: 0,
    adminPassword: 'cjdxjsjkxxy'
  };

  // ========== 初始化 ==========
  function init() {
    // 先加载本地配置
    var config = Storage.get('exam_config', null);
    if (!config) {
      config = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      Storage.set('exam_config', config);
    }
    state.examConfig = config;

    // 从云端拉取最新配置
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
    }

    // 加载用户信息
    state.userInfo = Storage.get('userInfo', null);
    if (state.userInfo && !state.userInfo.clazz) state.userInfo.clazz = '';

    // 加载学生名单
    state.studentList = Storage.get('student_list', []);

    // 获取设备信息
    state.deviceInfo = AntiCheat.getDeviceInfo();

    // 绑定全局事件
    bindGlobalEvents();

    // 渲染首页
    renderPage('home');
  }

  // ========== 页面路由 ==========
  function renderPage(page) {
    state.currentPage = page;
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
    // 显示目标页面
    var target = document.getElementById('page-' + page);
    if (target) target.classList.add('active');

    // 页面特定渲染
    switch (page) {
      case 'home': renderHome(); break;
      case 'exam': renderExam(); break;
      case 'result': renderResult(); break;
      case 'history': renderHistory(); break;
      case 'admin': renderAdmin(); break;
      case 'admin-config': renderAdminConfig(); break;
      case 'admin-scores': renderAdminScores(); break;
      case 'admin-data': renderAdminData(); break;
      case 'admin-students': renderAdminStudents(); break;
      case 'admin-monitor': renderAdminMonitor(); break;
    }
    window.scrollTo(0, 0);
  }

  // ========== 全局事件绑定 ==========
  function bindGlobalEvents() {
    // 使用事件委托
    document.body.addEventListener('click', function(e) {
      var target = e.target.closest('[data-action]');
      if (!target) return;
      var action = target.dataset.action;
      var params = {};
      // 收集 data-* 参数
      for (var key in target.dataset) {
        if (key !== 'action') params[key] = target.dataset[key];
      }
      handleAction(action, params, target);
    });

    // 输入事件委托
    document.body.addEventListener('input', function(e) {
      var target = e.target.closest('[data-input]');
      if (!target) return;
      handleInput(target.dataset.input, target.value, target);
    });

    // 阻止表单默认提交
    document.body.addEventListener('submit', function(e) {
      e.preventDefault();
    });
  }

  function handleAction(action, params, el) {
    switch (action) {
      // 首页
      case 'start-exam': startExam(); break;
      case 'go-history': renderPage('history'); break;
      case 'edit-userinfo': editUserInfo(); break;
      case 'title-click': onTitleClick(); break;
      case 'go-admin': renderPage('admin'); break;
      case 'go-home': renderPage('home'); break;

      // 答题页
      
      case 'next-question': nextQuestion(); break;
      case 'submit-current': submitCurrent(); break;
      case 'toggle-wrong-only': state.resultOnlyWrong = !state.resultOnlyWrong; state.resultIndex = 0; renderResult(); break;
      case 'jump-question':
        var val = parseInt(document.getElementById('jump-input').value);
        if (val >= 1 && val <= (state.resultOnlyWrong ? state.examResult.questions.filter(function(q){return !q.correct;}).length : state.examResult.questions.length)) {
          state.resultIndex = val - 1;
          renderResult();
        } else {
          Util.showToast('题号超出范围');
        }
        break;
      case 'exit-exam': exitExam(); break;
      case 'toggle-mark': toggleMark(); break;
      case 'toggle-sheet': toggleAnswerSheet(); break;
      case 'jump-question': jumpQuestion(parseInt(params.index)); break;
      case 'submit-exam': submitExam(false); break;

      // 结果页
      case 'retake-exam': renderPage('home'); break;
      case 'view-history': renderPage('history'); break;

      // 教师端
      case 'admin-login': adminLogin(); break;
      case 'admin-logout': adminLogout(); break;
      case 'toggle-exam-status': toggleExamStatus(); break;
      case 'go-admin-config': renderPage('admin-config'); break;
      case 'go-admin-scores': renderPage('admin-scores'); break;
      case 'go-admin-data': renderPage('admin-data'); break;
      case 'save-config': saveConfig(); break;
      case 'reset-config': resetConfig(); break;
      case 'change-password': changePassword(); break;
      case 'reset-type-weights': resetTypeWeights(); break;
      case 'sort-scores': sortScores(params.sort); break;
      case 'export-scores': exportScores(); break;
      case 'view-student-detail': viewStudentDetail(params.studentid); break;
      case 'clear-exam-data': clearExamData(); break;
      case 'reset-all': resetAll(); break;
      case 'export-backup': exportBackup(); break;
      case 'go-admin-students': renderPage('admin-students'); break;
      case 'go-admin-monitor': renderPage('admin-monitor'); break;
      case 'import-students': importStudents(); break;
      case 'clear-student-list': clearStudentList(); break;
      case 'download-template': downloadTemplate(); break;
      case 'show-qrcode': showQRCode(); break;
      case 'add-student': addStudent(); break;
      case 'batch-import': batchImportStudents(); break;
      case 'refresh-cloud-data': loadMonitorData(); Util.showToast('已刷新'); break;
      case 'save-cloud-config': saveCloudConfig(); break;
    }
  }

  function handleInput(inputType, value, el) {
    switch (inputType) {
      case 'student-id':
        if (!state.userInfo) state.userInfo = { studentId: '', name: '' };
        state.userInfo.studentId = value.trim();
        // 如果名单不为空，输入学号后自动匹配姓名
        if (state.studentList.length > 0 && value.trim()) {
          var matched = state.studentList.find(function(s) {
            return s.studentId === value.trim();
          });
          if (matched) {
            state.userInfo.name = matched.name;
            state.userInfo.clazz = matched.clazz || '';
            // 更新姓名输入框
            var nameInput = document.querySelector('[data-input="student-name"]');
            if (nameInput) nameInput.value = matched.name;
            // 更新班级下拉
            var classInput = document.querySelector('[data-input="student-class"]');
            if (classInput) classInput.value = matched.clazz || '';
          }
        }
        break;
      case 'student-class':
        if (!state.userInfo) state.userInfo = { studentId: '', name: '', clazz: '' };
        state.userInfo.clazz = value.trim();
        break;
      case 'student-name':
        if (!state.userInfo) state.userInfo = { studentId: '', name: '' };
        state.userInfo.name = value.trim();
        break;
      case 'exam-answer':
        handleAnswerInput(value);
        break;
      case 'admin-password':
        state._adminPwdInput = value;
        break;
      case 'config-start-time':
        state.examConfig.startTime = value ? new Date(value).getTime() : null;
        break;
      case 'config-end-time':
        state.examConfig.endTime = value ? new Date(value).getTime() : null;
        break;
      case 'config-exam-name':
        state.examConfig.examName = value;
        break;
      case 'config-total-questions':
        state.examConfig.totalQuestions = parseInt(value) || 100;
        break;
      case 'config-duration':
        state.examConfig.duration = parseInt(value) || 30;
        break;
      case 'config-basic-max':
        state.examConfig.basicMax = parseInt(value) || 255;
        break;
      case 'config-advanced-max':
        state.examConfig.advancedMax = parseInt(value) || 1024;
        break;
      case 'cloud-url': state._cloudUrl = value; break;
      case 'cloud-key': state._cloudKey = value; break;
      case 'admin-search':
        state.adminSearchKeyword = value;
        renderAdminScores();
        break;
    }
  }

  // ========== 首页 ==========
  function renderHome() {
    var config = state.examConfig;
    var now = Date.now();
    var status = config.status;
    if (config.startTime && now < config.startTime) status = 0;
    else if (config.endTime && now > config.endTime) status = 2;

    var countdownText = '';
    if (config.startTime && now < config.startTime) {
      countdownText = '距离考试开始还有 ' + Util.formatDuration(Math.floor((config.startTime - now) / 1000));
    } else if (config.endTime && now < config.endTime) {
      countdownText = '距离考试结束还有 ' + Util.formatDuration(Math.floor((config.endTime - now) / 1000));
    } else if (config.endTime && now >= config.endTime) {
      countdownText = '考试已结束';
    } else {
      countdownText = '考试进行中';
    }

    var statusText = ['未开始', '进行中', '已结束'][status];
    var statusClass = ['status-pending', 'status-open', 'status-closed'][status];

    var userInfoHtml = '';
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
        '<div class="form-group">' +
          '<label class="form-label">班级</label>' +
          '<input class="form-input" type="text" data-input="student-class" placeholder="请输入班级，如：计科2401" maxlength="30" value="' + (state.userInfo ? state.userInfo.clazz || '' : '') + '" list="class-list">' +
          '<datalist id="class-list">' + classOptsHtml.replace('<option value="">请选择班级</option>', '') + '</datalist>' +
        '</div>';
    }

    var startBtnText = status === 0 ? '考试未开始' : status === 2 ? '考试已结束' : '开始考试';
    var startBtnDisabled = status !== 1 ? 'disabled' : '';

    document.getElementById('home-content').innerHTML =
      '<div class="card exam-header-card">' +
        '<div class="exam-title" data-action="title-click">' + config.examName + '</div>' +
        '<div class="exam-subtitle">二进制 · 八进制 · 十进制 · 十六进制 相互转换</div>' +
        '<div class="exam-tags">' +
          '<span class="tag tag-blue">' + config.totalQuestions + ' 题</span>' +
          '<span class="tag tag-orange">' + config.duration + ' 分钟</span>' +
          (config.allowRetake ? '<span class="tag tag-green">可多次答题</span>' : '') +
        '</div>' +
      '</div>' +

      '<div class="card">' +
        '<div class="status-row">' +
          '<span class="status-label">考试状态</span>' +
          '<span class="status-badge ' + statusClass + '">' + statusText + '</span>' +
        '</div>' +
        '<div class="countdown" id="home-countdown">' + countdownText + '</div>' +
        (config.startTime ? '<div class="time-info">开始时间：' + Util.formatTime(config.startTime) + '</div>' : '') +
        (config.endTime ? '<div class="time-info">结束时间：' + Util.formatTime(config.endTime) + '</div>' : '') +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">考生信息</div>' +
        userInfoHtml +
      '</div>' +

      '<div class="action-area">' +
        '<button class="btn btn-primary btn-lg" data-action="start-exam" ' + startBtnDisabled + '>' + startBtnText + '</button>' +
        '<button class="btn btn-secondary mt-16" data-action="go-history">我的考试记录</button>' +
      '</div>' +

      '<div class="card tips-card">' +
        '<div class="card-title">注意事项</div>' +
        '<div class="tip-item">1. 每次进入考试将随机生成全新试卷，题目互不相同。</div>' +
        '<div class="tip-item">2. 考试开始后自动计时，时间到将自动提交试卷。</div>' +
        '<div class="tip-item">3. 四位二进制题目不足四位需补前导零，如 7 → 0111。</div>' +
        '<div class="tip-item">4. 十六进制结果字母请使用大写，如 11 → B。</div>' +
        '<div class="tip-item">5. 提交后可查看错题解析，支持多次答题刷分。</div>' +
      '</div>' +

      '<div class="footer-links">' +
        '<span data-action="show-qrcode">📱 分享二维码</span>' +
        '<span class="divider">|</span>' +
        '<span data-action="go-admin">教师入口</span>' +
      '</div>';

    // 启动倒计时刷新（只更新倒计时文字，不重建整个页面，避免输入中断）
    if (state._homeTimer) clearInterval(state._homeTimer);
    state._homeTimer = setInterval(function() {
      if (state.currentPage !== 'home') return;
      var el = document.getElementById('home-countdown');
      if (!el) return;
      var cfg = state.examConfig;
      var now = Date.now();
      var text;
      if (cfg.startTime && now < cfg.startTime) {
        text = '距离考试开始还有 ' + Util.formatDuration(Math.floor((cfg.startTime - now) / 1000));
      } else if (cfg.endTime && now < cfg.endTime) {
        text = '距离考试结束还有 ' + Util.formatDuration(Math.floor((cfg.endTime - now) / 1000));
      } else if (cfg.endTime && now >= cfg.endTime) {
        text = '考试已结束';
      } else {
        text = '考试进行中';
      }
      el.textContent = text;
    }, 1000);
  }

  function onTitleClick() {
    state.titleClickCount++;
    if (state.titleClickCount >= 5) {
      Util.showToast('已显示教师管理入口', 'success');
      renderHome();
    }
  }

  function editUserInfo() {
    state.userInfo = null;
    Storage.remove('userInfo');
    renderHome();
  }

  // ========== 开始考试 ==========
  function startExam() {
    // 校验用户信息
    if (!state.userInfo || !state.userInfo.studentId || !state.userInfo.name) {
      Util.showToast('请先填写学号和姓名');
      return;
    }
    if (!Util.validateStudentId(state.userInfo.studentId)) {
      Util.showToast('学号格式不正确（4-20位字母或数字）');
      return;
    }
    if (!Util.validateName(state.userInfo.name)) {
      Util.showToast('姓名格式不正确（2-20个字符）');
      return;
    }
    if (!state.userInfo.clazz || !state.userInfo.clazz.trim()) {
      Util.showToast('请输入班级');
      return;
    }

    // 学生名单校验（如果名单不为空，必须匹配）
    if (state.studentList.length > 0) {
      var matched = state.studentList.find(function(s) {
        return s.studentId === state.userInfo.studentId;
      });
      if (!matched) {
        Util.showToast('学号不在考试名单中，请联系老师');
        return;
      }
      // 校验姓名是否匹配
      if (matched.name !== state.userInfo.name) {
        Util.showToast('姓名与学号不匹配，请检查');
        return;
      }
      // 如果名单里有班级，校验班级是否匹配
      if (matched.clazz && state.userInfo.clazz && matched.clazz !== state.userInfo.clazz) {
        Util.showToast('班级与学号不匹配，请检查');
        return;
      }
    }

    // 设备指纹防替考检查
    var deviceBindings = Storage.get('device_bindings', {});
    var fp = state.deviceInfo.fingerprint;
    var boundStudent = deviceBindings[fp];
    if (boundStudent && boundStudent.studentId !== state.userInfo.studentId) {
      Util.showModal('设备异常',
        '此设备已绑定学号：' + boundStudent.studentId + '（' + boundStudent.name + '）\n\n' +
        '为防止替考，一台设备只能绑定一名考生。\n如需更换设备，请联系老师。',
        '我知道了');
      return;
    }

    // 保存用户信息
    Storage.set('userInfo', state.userInfo);

    // 绑定设备与学号（首次）
    if (!boundStudent) {
      deviceBindings[fp] = {
        studentId: state.userInfo.studentId,
        name: state.userInfo.name,
        bindTime: Date.now()
      };
      Storage.set('device_bindings', deviceBindings);
    }

    // 检查考试状态
    var config = state.examConfig;
    var now = Date.now();
    if (config.startTime && now < config.startTime) {
      Util.showToast('考试尚未开始');
      return;
    }
    if (config.endTime && now > config.endTime) {
      Util.showToast('考试已结束');
      return;
    }

    // 检查是否有未完成的进度
    var progress = Storage.get('exam_progress', null);

    if (progress) {
      var remainTime = Math.max(0, Math.floor((progress.endTime - Date.now()) / 1000));
      if (remainTime > 0) {
        // 自定义弹窗：继续 / 重新开始
        var mask = document.createElement('div');
        mask.className = 'modal-mask';
        mask.innerHTML =
          '<div class="modal-box">' +
            '<div class="modal-title">继续考试</div>' +
            '<div class="modal-text">检测到你有未完成的考试进度：</div>' +
            '<div class="modal-text" style="text-align:left;margin:12px 0;">' +
              '已完成 ' + (progress.currentIndex + 1) + '/' + (progress.answers ? progress.answers.length : '?') + ' 题<br>' +
              '剩余时间：' + Math.floor(remainTime / 60) + ' 分钟' +
            '</div>' +
            '<div style="display:flex;flex-direction:column;gap:10px;">' +
              '<button class="modal-btn modal-confirm" id="continue-btn">继续考试</button>' +
              '<button class="modal-btn modal-cancel" id="restart-btn">重新开始</button>' +
            '</div>' +
          '</div>';
        document.body.appendChild(mask);

        mask.querySelector('#continue-btn').onclick = function() {
          mask.remove();
          // 继续考试
          state.currentPaper = progress.paper;
          state.currentIndex = progress.currentIndex;
          state.answers = progress.answers;
          state.submittedAnswers = progress.submittedAnswers || [];
          state.currentScore = progress.currentScore || 0;
          state.startTime = progress.startTime;
          state.endTime = progress.endTime;
          state.blurCount = 0;

          AntiCheat.startMonitoring(function(count) {
            state.blurCount = count;
            Util.showModal('考试警告',
              '考试期间请勿切换应用或页面，切屏行为已被记录。',
              '我知道了');
          });

          renderPage('exam');
        };
        mask.querySelector('#restart-btn').onclick = function() {
          mask.remove();
          Storage.remove('exam_progress');
          startNewExam();
        };
        mask.onclick = function(e) { if (e.target === mask) mask.remove(); };
        return;
      } else {
        Storage.remove('exam_progress');
      }
    }

    startNewExam();
  }

  function startNewExam() {
    var config = state.examConfig;
    Util.showModal('开始考试',
      '本次考试共 ' + config.totalQuestions + ' 题，时长 ' + config.duration + ' 分钟。\n\n' +
      '⚠️ 考试期间请不要切换到其他应用或页面，切屏将被记录。\n\n确定要开始吗？',
      '开始考试').then(function(confirmed) {
      if (!confirmed) return;

      // 生成试卷
      var paper = Converter.generatePaper(config.totalQuestions, {
        basicMax: config.basicMax,
        advancedMax: config.advancedMax,
        advancedRatio: config.advancedRatio,
        typeWeights: config.typeWeights
      });

      state.currentPaper = paper;
      state.currentIndex = 0;
      state.answers = new Array(paper.questions.length).fill('');
      state.submittedAnswers = [];
      state.currentScore = 0;
      state.startTime = Date.now();
      state.endTime = Date.now() + config.duration * 60 * 1000;
      state.blurCount = 0;

      // 启动切屏监控
      AntiCheat.startMonitoring(function(count) {
        state.blurCount = count;
        Util.showModal('考试警告',
          '考试期间请勿切换应用或页面，切屏行为已被记录。',
          '我知道了');
      });

      // 保存进度
      saveExamProgress();

      renderPage('exam');
    });
  }

  // ========== 答题页 ==========
  function renderExam() {
    var paper = state.currentPaper;
    if (!paper) { renderPage('home'); return; }

    var q = paper.questions[state.currentIndex];
    var remaining = Math.max(0, Math.floor((state.endTime - Date.now()) / 1000));
    var answeredCount = state.submittedCount || 0;
    var isSubmitted = state.submittedAnswers && state.submittedAnswers[state.currentIndex];

    // 累计得分
    var totalScore = state.currentScore || 0;

    // 构建答题卡（只能看不能点）
    var sheetHtml = '';
    for (var i = 0; i < paper.questions.length; i++) {
      var cls = 'sheet-item';
      if (state.submittedAnswers && state.submittedAnswers[i]) {
        cls += state.submittedAnswers[i].correct ? ' answered' : ' wrong';
      } else {
        cls += ' unanswered';
      }
      if (i === state.currentIndex) cls += ' current';
      sheetHtml += '<div class="' + cls + '">' + (i + 1) + '</div>';
    }

    var isLast = state.currentIndex === paper.questions.length - 1;

    // 解析内容
    var analysisHtml = '';
    if (isSubmitted) {
      var sa = state.submittedAnswers[state.currentIndex];
      var correctClass = sa.correct ? 'correct' : 'wrong';
      var correctIcon = sa.correct ? '✅ 回答正确' : '❌ 回答错误';
      analysisHtml =
        '<div class="analysis-box ' + correctClass + '">' +
          '<div class="analysis-title">' + correctIcon + '</div>' +
          '<div class="analysis-item">你的答案：<span class="your-answer">' + (sa.userAnswer || '空') + '</span></div>' +
          '<div class="analysis-item">正确答案：<span class="right-answer">' + q.answer + '</span></div>' +
          '<div class="analysis-item">本题得分：' + (sa.correct ? (100 / paper.questions.length).toFixed(1) : 0) + ' 分</div>' +
          '<div class="analysis-explain"><pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.7;margin:0;">' + Converter.generateExplanation(q, sa.userAnswer) + '</pre></div>' +
        '</div>';
    }

    document.getElementById('exam-content').innerHTML =
      '<div class="exam-topbar">' +
        '<div class="exam-topbar-left" data-action="exit-exam" style="cursor:pointer;color:#ef4444;">← 退出</div>' +
        '<div class="exam-topbar-center ' + (remaining <= 60 ? 'time-warning' : '') + '">⏱ ' + Util.formatDuration(remaining) + '</div>' +
        '<div class="exam-topbar-right">累计 <span style="color:#22c55e;font-weight:600;">' + totalScore.toFixed(1) + '</span> 分</div>' +
      '</div>' +

      '<div class="exam-question-area">' +
        '<div class="question-card">' +
          '<div class="question-type-tags">' +
            '<span class="tag tag-blue">' + q.typeName + '</span>' +
          '</div>' +
          '<div class="question-text">' + q.question + '</div>' +
          '<div class="source-value-box">' +
            '<span class="source-label">原数：</span>' +
            '<span class="source-num">' + q.sourceValue + '</span>' +
            '<span class="source-base">(' + q.fromBase + '进制)</span>' +
          '</div>' +
          (isSubmitted ? '' :
          '<div class="answer-input-area">' +
            '<label class="answer-label">请输入答案（' + q.toBase + '进制）</label>' +
            '<input class="answer-input" type="text" data-input="exam-answer" placeholder="在此输入答案" value="' + (state.answers[state.currentIndex] || '') + '" autofocus>' +
            (q.padLength > 0 ? '<div class="answer-hint">提示：结果需为 ' + q.padLength + ' 位，不足请补前导零</div>' : '') +
            (q.toBase === 16 ? '<div class="answer-hint">提示：十六进制字母请使用大写（A-F）</div>' : '') +
          '</div>') +
          analysisHtml +
        '</div>' +
      '</div>' +

      '<div class="exam-bottombar">' +
        (isSubmitted ?
          '<button class="btn btn-footer btn-next" data-action="' + (isLast ? 'submit-exam' : 'next-question') + '">' + (isLast ? '交卷' : '下一题') + '</button>'
          :
          '<button class="btn btn-footer btn-next btn-primary" data-action="submit-current">提交本题</button>'
        ) +
      '</div>' +

      '<div class="sheet-mask" id="sheet-mask" style="display:none;">' +
        '<div class="sheet-panel">' +
          '<div class="sheet-header"><span>答题卡</span><span class="sheet-close" data-action="toggle-sheet">✕</span></div>' +
          '<div class="sheet-stats">' +
            '<span><span class="dot dot-answered"></span>正确 ' + (state.submittedAnswers ? state.submittedAnswers.filter(function(a){return a&&a.correct;}).length : 0) + '</span>' +
            '<span><span class="dot dot-unanswered"></span>错误 ' + (state.submittedAnswers ? state.submittedAnswers.filter(function(a){return a&&!a.correct;}).length : 0) + '</span>' +
            '<span><span class="dot dot-marked"></span>未做 ' + (paper.questions.length - answeredCount) + '</span>' +
          '</div>' +
          '<div class="sheet-grid">' + sheetHtml + '</div>' +
        '</div>' +
      '</div>';

    // 聚焦输入框
    if (!isSubmitted) {
      setTimeout(function() {
        var input = document.querySelector('.answer-input');
        if (input) input.focus();
      }, 100);
    }

    // 启动计时
    if (state._examTimer) clearInterval(state._examTimer);
    state._examTimer = setInterval(function() {
      if (state.currentPage !== 'exam') return;
      var rem = Math.max(0, Math.floor((state.endTime - Date.now()) / 1000));
      var timeEl = document.querySelector('.exam-topbar-center');
      if (timeEl) {
        timeEl.textContent = '⏱ ' + Util.formatDuration(rem);
        if (rem <= 60) timeEl.classList.add('time-warning');
      }
      if (rem <= 0) {
        clearInterval(state._examTimer);
        autoSubmit();
      }
    }, 1000);
  }

  function handleAnswerInput(value) {
    var q = state.currentPaper.questions[state.currentIndex];
    // 十六进制自动转大写
    if (q.toBase === 16) value = value.toUpperCase();
    state.answers[state.currentIndex] = value;
    saveExamProgress();
    // 更新答题卡计数
    var answeredCount = state.answers.filter(function(a) { return a && a.trim() !== ''; }).length;
    var countEl = document.querySelector('.sheet-count');
    if (countEl) countEl.textContent = answeredCount + '/' + state.currentPaper.questions.length;
  }

  function prevQuestion() {
    if (state.currentIndex > 0) {
      state.currentIndex--;
      saveExamProgress();
      renderExam();
    }
  }

  function nextQuestion() {
    if (state.currentIndex < state.currentPaper.questions.length - 1) {
      state.currentIndex++;
      saveExamProgress();
      renderExam();
    }
  }

  // 退出考试弹窗
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
      saveMidProgress();
      mask.remove();
      state.currentPaper = null;
      renderPage('home');
      Util.showToast('进度已保存，考试期间可继续');
    };
    // 直接交卷
    mask.querySelector('#exit-confirm-btn').onclick = function() {
      mask.remove();
      doSubmit();
    };
    mask.onclick = function(e) { if (e.target === mask) mask.remove(); };
  }

  // 提交当前题，即时判题
  function submitCurrent() {
    var paper = state.currentPaper;
    var q = paper.questions[state.currentIndex];
    var userAnswer = (state.answers[state.currentIndex] || '').trim().toUpperCase();
    var correctAnswer = q.answer.toUpperCase();
    var correct = userAnswer === correctAnswer;

    // 初始化数组
    if (!state.submittedAnswers) state.submittedAnswers = [];
    if (typeof state.currentScore !== 'number') state.currentScore = 0;

    // 记录本题结果
    state.submittedAnswers[state.currentIndex] = {
      userAnswer: userAnswer,
      correct: correct
    };

    // 累计得分
    if (correct) state.currentScore += 100 / paper.questions.length;

    // 更新已提交计数
    state.submittedCount = state.submittedAnswers.filter(function(a) { return a; }).length;

    saveExamProgress();
    renderExam();
  }

  function toggleMark() {
    state.marked[state.currentIndex] = !state.marked[state.currentIndex];
    saveExamProgress();
    renderExam();
  }

  function toggleAnswerSheet() {
    var mask = document.getElementById('sheet-mask');
    if (mask) {
      mask.style.display = mask.style.display === 'none' ? 'flex' : 'none';
    }
  }

  function jumpQuestion(index) {
    state.currentIndex = index;
    saveExamProgress();
    toggleAnswerSheet();
    renderExam();
  }

  function saveExamProgress() {
    if (!state.currentPaper) return;
    var progress = {
      paper: state.currentPaper,
      currentIndex: state.currentIndex,
      answers: state.answers,
      submittedAnswers: state.submittedAnswers || [],
      currentScore: state.currentScore || 0,
      startTime: state.startTime,
      endTime: state.endTime,
      savedAt: Date.now()
    };
    Storage.set('exam_progress', progress);
  }

  // 退出时保存中途进度到云端
  function saveMidProgress() {
    if (!state.currentPaper || !Cloud.isConfigured() || !state.userInfo || !state.userInfo.studentId) return;
    var score = state.currentScore || 0;
    var correctCount = (state.submittedAnswers || []).filter(function(a){return a&&a.correct;}).length;
    // 先删掉之前的中途记录，再上传新的
    Cloud.fetchRecordsByStudent(state.userInfo.studentId).then(function(records) {
      var delPromises = [];
      records.forEach(function(r) {
        if (!r.is_final) {
          delPromises.push(fetch('https://uazwtblpwayqlpczczai.supabase.co/rest/v1/exam_records?id=eq.' + r.id, {
            method: 'DELETE',
            headers: {
              'apikey': 'sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs',
              'Authorization': 'Bearer sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs'
            }
          }));
        }
      });
      Promise.all(delPromises).then(function() {
        Cloud.uploadRecord({
          student_id: state.userInfo.studentId,
          name: state.userInfo.name,
          clazz: state.userInfo.clazz || '',
          score: score,
          correct_count: correctCount,
          total_count: state.currentPaper.questions.length,
          duration: Math.floor((Date.now() - state.startTime) / 1000),
          submit_time: Date.now(),
          is_timeout: false,
          blur_count: state.blurCount || 0,
          device_fingerprint: state.deviceInfo.fingerprint,
          device_model: state.deviceInfo.deviceModel,
          start_time: state.startTime,
          is_final: false
        }).catch(function() {});
      });
    }).catch(function() {});
  }

  // ========== 交卷 ==========
  function submitExam(isTimeout) {
    if (state._submitting) return;

    if (!isTimeout) {
      var unanswered = state.currentPaper.questions.length - state.answers.filter(function(a) { return a && a.trim() !== ''; }).length;
      var content = '确定要交卷吗？\n已答 ' + (state.currentPaper.questions.length - unanswered) + ' 题，未答 ' + unanswered + ' 题。';
      if (unanswered > 0) content += '\n交卷后未答题目将计为错误。';

      Util.showModal('交卷确认', content, '确认交卷').then(function(confirmed) {
        if (confirmed) doSubmit(false);
      });
    } else {
      doSubmit(true);
    }
  }

  function autoSubmit() {
    Util.showToast('考试时间到，自动交卷', 'info');
    setTimeout(function() { doSubmit(true); }, 1500);
  }

  function doSubmit(isTimeout) {
    if (state._submitting) return;
    state._submitting = true;
    if (state._examTimer) clearInterval(state._examTimer);
    // 停止切屏监控
    AntiCheat.stopMonitoring();

    var paper = state.currentPaper;
    var questions = paper.questions;
    var answers = state.answers;
    var duration = Math.floor((Date.now() - (state.endTime - state.examConfig.duration * 60 * 1000)) / 1000);
    var blurCount = AntiCheat.getBlurCount();

    // 判分
    var correctCount = 0;
    var wrongQuestions = [];
    for (var i = 0; i < questions.length; i++) {
      var q = questions[i];
      var userAnswer = answers[i] || '';
      var isCorrect = Converter.checkAnswer(q, userAnswer);
      if (isCorrect) {
        correctCount++;
      } else {
        wrongQuestions.push({
          ...q,
          userAnswer: userAnswer,
          explanation: Converter.generateExplanation(q, userAnswer)
        });
      }
    }

    var score = Math.round((correctCount / questions.length) * 1000) / 10;
    var now = Date.now();

    // 保存考试记录（含防作弊数据）
    var record = {
      recordId: 'rec_' + now + '_' + Math.random().toString(36).slice(2, 6),
      paperId: paper.paperId,
      studentId: state.userInfo.studentId,
      name: state.userInfo.name,
      score: score,
      correctCount: correctCount,
      totalCount: questions.length,
      duration: duration,
      submitTime: now,
      isTimeout: isTimeout,
      blurCount: blurCount,
      deviceFingerprint: state.deviceInfo.fingerprint,
      deviceModel: state.deviceInfo.deviceModel,
      questions: questions,
      answers: answers,
      wrongQuestions: wrongQuestions
    };

    var records = Storage.get('exam_records', []);
    records.push(record);
    Storage.set('exam_records', records);

    // 更新成绩表
    var scores = Storage.get('scores', []);
    var existingIdx = -1;
    for (var j = 0; j < scores.length; j++) {
      if (scores[j].studentId === state.userInfo.studentId) { existingIdx = j; break; }
    }
    if (existingIdx >= 0) {
      var existing = scores[existingIdx];
      scores[existingIdx] = {
        ...existing,
        name: state.userInfo.name,
        maxScore: Math.max(existing.maxScore, score),
        latestScore: score,
        examCount: existing.examCount + 1,
        latestDuration: duration,
        latestSubmitTime: now,
        latestBlurCount: blurCount,
        maxBlurCount: Math.max(existing.maxBlurCount || 0, blurCount),
        deviceFingerprint: state.deviceInfo.fingerprint,
        deviceModel: state.deviceInfo.deviceModel,
        updateTime: now
      };
    } else {
      scores.push({
        studentId: state.userInfo.studentId,
        name: state.userInfo.name,
        maxScore: score,
        latestScore: score,
        examCount: 1,
        latestDuration: duration,
        latestSubmitTime: now,
        latestBlurCount: blurCount,
        maxBlurCount: blurCount,
        deviceFingerprint: state.deviceInfo.fingerprint,
        deviceModel: state.deviceInfo.deviceModel,
        createTime: now,
        updateTime: now
      });
    }
    Storage.set('scores', scores);

    // 云端同步：上传考试记录
    if (Cloud.isConfigured()) {
      Cloud.uploadRecord({
        student_id: state.userInfo.studentId,
        name: state.userInfo.name,
        clazz: state.userInfo.clazz || '',
        score: score,
        correct_count: correctCount,
        total_count: questions.length,
        duration: duration,
        submit_time: now,
        start_time: state.startTime,
        is_timeout: isTimeout,
        blur_count: blurCount,
        device_fingerprint: state.deviceInfo.fingerprint,
        device_model: state.deviceInfo.deviceModel,
        is_final: true
      }).then(function() {
        console.log('成绩已同步到云端');
      }).catch(function(err) {
        console.warn('云端同步失败：', err.message);
      });
    }

    // 清除进度
    Storage.remove('exam_progress');

    state.examResult = record;
    state._submitting = false;
    renderPage('result');
  }

  // ========== 结果页 ==========
  function renderResult() {
    var r = state.examResult;
    if (!r) { renderPage('home'); return; }

    var accuracy = r.totalCount > 0 ? Math.round((r.correctCount / r.totalCount) * 1000) / 10 : 0;

    // 当前题号（默认0）
    if (typeof state.resultIndex !== 'number') state.resultIndex = 0;
    if (typeof state.resultOnlyWrong !== 'boolean') state.resultOnlyWrong = false;

    // 获取题目列表（全部或仅错题）
    var questions = r.questions || [];
    var wrongIdxList = [];
    questions.forEach(function(q, i) {
      if (q.correct === false) wrongIdxList.push(i);
    });

    var displayList = state.resultOnlyWrong ? wrongIdxList.map(function(i){return {q: questions[i], idx: i};}) : questions.map(function(q,i){return {q:q, idx:i};});
    var cur = displayList[state.resultIndex];
    if (!cur) { state.resultIndex = 0; cur = displayList[0]; }

    // 题号导航HTML
    var navHtml = '';
    displayList.forEach(function(item, i) {
      var cls = 'nav-item';
      if (item.q.correct) cls += ' nav-correct';
      else cls += ' nav-wrong';
      if (i === state.resultIndex) cls += ' nav-current';
      var num = state.resultOnlyWrong ? (i+1) : (item.idx+1);
      navHtml += '<div class="' + cls + '" data-action="result-nav" data-index="' + i + '">' + num + '</div>';
    });

    // 当前题解析
    var curHtml = '';
    if (cur) {
      var q = cur.q;
      var correctClass = q.correct ? 'correct' : 'wrong';
      var correctIcon = q.correct ? '✅ 回答正确' : '❌ 回答错误';
      curHtml =
        '<div class="analysis-box ' + correctClass + '">' +
          '<div class="analysis-title">' + correctIcon + ' · 第 ' + (cur.idx+1) + ' 题</div>' +
          '<div class="analysis-item">题型：' + q.typeName + '</div>' +
          '<div class="analysis-item">题目：' + q.question + '</div>' +
          '<div class="analysis-item">原数：' + q.sourceValue + '（' + q.fromBase + '进制）</div>' +
          '<div class="analysis-item">你的答案：<span class="your-answer">' + (q.userAnswer || '空') + '</span></div>' +
          '<div class="analysis-item">正确答案：<span class="right-answer">' + q.answer + '</span></div>' +
          '<div class="analysis-explain"><pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.7;margin:0;">' + Converter.generateExplanation(q, q.userAnswer) + '</pre></div>' +
        '</div>';
    }

    document.getElementById('result-content').innerHTML =
      '<div class="result-score-card">' +
        '<div class="result-score-header">考试成绩' + (r.isTimeout ? '<span class="tag tag-orange" style="margin-left:12px;">超时自动提交</span>' : '') + '</div>' +
        '<div class="result-score-num">' + r.score + '<span class="score-unit">分</span></div>' +
        '<div class="result-stats">' +
          '<div class="rs-item"><div class="rs-value text-success">' + r.correctCount + '</div><div class="rs-label">正确</div></div>' +
          '<div class="rs-item"><div class="rs-value text-danger">' + (r.totalCount - r.correctCount) + '</div><div class="rs-label">错误</div></div>' +
          '<div class="rs-item"><div class="rs-value text-primary">' + accuracy + '%</div><div class="rs-label">正确率</div></div>' +
          '<div class="rs-item"><div class="rs-value">' + Util.formatDuration(r.duration) + '</div><div class="rs-label">用时</div></div>' +
        '</div>' +
        '<div class="result-submit-time">提交时间：' + Util.formatTime(r.submitTime) + '</div>' +
      '</div>' +

      '<div class="result-actions">' +
        '<button class="btn btn-primary" data-action="retake-exam">再考一次</button>' +
        '<div class="btn-row mt-16">' +
          '<button class="btn btn-secondary flex-1" data-action="view-history">历史记录</button>' +
          '<button class="btn btn-secondary flex-1" data-action="go-home">返回首页</button>' +
        '</div>' +
      '</div>' +

      '<div class="card" style="margin-top:16px;">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">' +
          '<div style="font-weight:600;">题目解析</div>' +
          '<button class="btn btn-secondary" data-action="toggle-wrong-only" style="padding:6px 12px;font-size:13px;">' + (state.resultOnlyWrong ? '显示全部题' : '只看错题') + '</button>' +
        '</div>' +
        '<div style="display:flex;gap:8px;align-items:center;margin-bottom:16px;">' +
          '<span>跳转到：</span>' +
          '<input type="number" id="jump-input" min="1" max="' + (state.resultOnlyWrong ? wrongIdxList.length : questions.length) + '" style="width:70px;padding:6px;border:1px solid #e5e7eb;border-radius:6px;text-align:center;">' +
          '<button class="btn btn-secondary" data-action="jump-question" style="padding:6px 12px;font-size:13px;">跳转</button>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:6px;margin-bottom:16px;">' + navHtml + '</div>' +
        curHtml +
      '</div>';

    // 暴露导航事件
    var navBtns = document.querySelectorAll('[data-action="result-nav"]');
    navBtns.forEach(function(btn) {
      btn.onclick = function() {
        state.resultIndex = parseInt(btn.dataset.index);
        renderResult();
      };
    });
  }

  // ========== 历史记录页 ==========
  function renderHistory() {
    if (!state.userInfo || !state.userInfo.studentId) {
      Util.showToast('请先填写身份信息');
      renderPage('home');
      return;
    }

    var records = Storage.get('exam_records', [])
      .filter(function(r) { return r.studentId === state.userInfo.studentId; })
      .sort(function(a, b) { return b.submitTime - a.submitTime; });

    var stats = {
      totalExams: records.length,
      maxScore: records.length > 0 ? Math.max.apply(null, records.map(function(r) { return r.score; })) : 0,
      avgScore: records.length > 0 ? Math.round(records.reduce(function(s, r) { return s + r.score; }, 0) / records.length * 10) / 10 : 0
    };

    var recordsHtml = '';
    if (records.length === 0) {
      recordsHtml = '<div class="empty"><div class="empty-icon">📋</div><div>暂无考试记录</div><button class="btn btn-primary mt-24" data-action="go-home">去考试</button></div>';
    } else {
      records.forEach(function(r) {
        var scoreClass = r.score >= 90 ? 'score-high' : r.score >= 60 ? 'score-mid' : 'score-low';
        var accuracy = r.totalCount > 0 ? Math.round((r.correctCount / r.totalCount) * 1000) / 10 : 0;
        recordsHtml +=
          '<div class="history-record">' +
            '<div class="hr-score ' + scoreClass + '">' + r.score + '</div>' +
            '<div class="hr-content">' +
              '<div class="hr-top">正确率 ' + accuracy + '%' + (r.isTimeout ? '<span class="tag tag-orange" style="margin-left:8px;">超时</span>' : '') + '</div>' +
              '<div class="hr-meta">正确 ' + r.correctCount + '/' + r.totalCount + ' · 用时 ' + Util.formatDuration(r.duration) + '</div>' +
              '<div class="hr-time">' + Util.formatTime(r.submitTime) + '</div>' +
            '</div>' +
          '</div>';
      });
    }

    document.getElementById('history-content').innerHTML =
      '<div class="card user-card">' +
        '<div class="user-avatar">' + state.userInfo.name[0] + '</div>' +
        '<div class="user-info-text"><div class="user-name">' + state.userInfo.name + '</div><div class="user-id">学号：' + state.userInfo.studentId + '</div></div>' +
      '</div>' +

      '<div class="stats-card">' +
        '<div class="stats-title">学习统计</div>' +
        '<div class="stats-grid">' +
          '<div class="stat-item"><div class="stat-num">' + stats.totalExams + '</div><div class="stat-label">考试次数</div></div>' +
          '<div class="stat-item"><div class="stat-num text-success">' + stats.maxScore + '</div><div class="stat-label">最高分</div></div>' +
          '<div class="stat-item"><div class="stat-num text-primary">' + stats.avgScore + '</div><div class="stat-label">平均分</div></div>' +
        '</div>' +
      '</div>' +

      '<div class="section-title">考试记录</div>' +
      recordsHtml +

      '<div class="bottom-actions"><button class="btn btn-secondary" data-action="go-home">返回首页</button></div>';
  }

  // ========== 教师管理端 ==========
  function renderAdmin() {
    if (!state.isAdmin) {
      // 登录页
      document.getElementById('admin-content').innerHTML =
        '<div class="login-wrap">' +
          '<div class="login-card">' +
            '<div class="login-icon">🔐</div>' +
            '<div class="login-title">教师管理入口</div>' +
            '<div class="login-subtitle">请输入管理员密码登录</div>' +
            '<div class="form-group mt-32">' +
              '<input class="form-input" type="password" data-input="admin-password" placeholder="请输入管理员密码" value="">' +
            '</div>' +
            '<button class="btn btn-primary mt-24" data-action="admin-login">登录</button>' +
            '<div class="login-tip">默认密码：admin123（可在配置中修改）</div>' +
          '</div>' +
        '</div>';
      return;
    }

    // 管理首页
    var config = state.examConfig;
    var scores = Storage.get('scores', []);
    var stats = {
      totalStudents: scores.length,
      totalExams: scores.reduce(function(s, i) { return s + i.examCount; }, 0),
      avgScore: scores.length > 0 ? Math.round(scores.reduce(function(s, i) { return s + i.maxScore; }, 0) / scores.length * 10) / 10 : 0,
      maxScore: scores.length > 0 ? Math.max.apply(null, scores.map(function(s) { return s.maxScore; })) : 0
    };

    var statusText = config.status === 1 ? '进行中' : config.status === 0 ? '未开始' : '已结束';
    var statusClass = config.status === 1 ? 'status-open' : 'status-closed';
    var toggleBtnText = config.status === 1 ? '关闭考试' : '开启考试';
    var toggleBtnClass = config.status === 1 ? 'btn-danger' : 'btn-primary';

    document.getElementById('admin-content').innerHTML =
      '<div class="admin-header">' +
        '<div class="admin-title">教师管理中心</div>' +
        '<div class="admin-logout" data-action="admin-logout">退出</div>' +
      '</div>' +

      '<div class="card">' +
        '<div class="status-header"><span class="status-title">' + config.examName + '</span><span class="status-badge ' + statusClass + '">' + statusText + '</span></div>' +
        '<div class="status-info-grid">' +
          '<div class="si-item"><div class="si-label">题量</div><div class="si-value">' + config.totalQuestions + '题</div></div>' +
          '<div class="si-item"><div class="si-label">时长</div><div class="si-value">' + config.duration + '分钟</div></div>' +
          '<div class="si-item"><div class="si-label">重考</div><div class="si-value">' + (config.allowRetake ? '允许' : '不允许') + '</div></div>' +
        '</div>' +
        '<button class="btn ' + toggleBtnClass + ' mt-24" data-action="toggle-exam-status">' + toggleBtnText + '</button>' +
      '</div>' +

      '<div class="admin-stats-grid">' +
        '<div class="as-card"><div class="as-num">' + stats.totalStudents + '</div><div class="as-label">参考学生</div></div>' +
        '<div class="as-card"><div class="as-num">' + stats.totalExams + '</div><div class="as-label">考试次数</div></div>' +
        '<div class="as-card"><div class="as-num text-primary">' + stats.avgScore + '</div><div class="as-label">平均分</div></div>' +
        '<div class="as-card"><div class="as-num text-success">' + stats.maxScore + '</div><div class="as-label">最高分</div></div>' +
      '</div>' +

      '<div class="admin-menu">' +
        '<div class="menu-item" data-action="go-admin-config"><div class="menu-icon config-icon">⚙️</div><div class="menu-content"><div class="menu-title">考试配置</div><div class="menu-desc">设置考试时间、题量、题型、难度</div></div><div class="menu-arrow">›</div></div>' +
        '<div class="menu-item" data-action="go-admin-students"><div class="menu-icon students-icon">👥</div><div class="menu-content"><div class="menu-title">学生名单</div><div class="menu-desc">导入学生名单、学号校验、防替考绑定</div></div><div class="menu-arrow">›</div></div>' +
        '<div class="menu-item" data-action="go-admin-monitor"><div class="menu-icon monitor-icon">📡</div><div class="menu-content"><div class="menu-title">考试监控</div><div class="menu-desc">实时查看切屏次数、设备信息、作弊预警</div></div><div class="menu-arrow">›</div></div>' +
        '<div class="menu-item" data-action="go-admin-scores"><div class="menu-icon scores-icon">📊</div><div class="menu-content"><div class="menu-title">成绩管理</div><div class="menu-desc">查看学生成绩、排名、导出Excel</div></div><div class="menu-arrow">›</div></div>' +
        '<div class="menu-item" data-action="go-admin-data"><div class="menu-icon data-icon">🗑️</div><div class="menu-content"><div class="menu-title">数据管理</div><div class="menu-desc">清空考试数据、重置系统、备份</div></div><div class="menu-arrow">›</div></div>' +
      '</div>' +

      '<button class="btn btn-secondary mt-32" data-action="go-home">返回首页</button>';
  }

  function adminLogin() {
    var pwd = state._adminPwdInput || '';
    if (!pwd) { Util.showToast('请输入管理员密码'); return; }
    if (pwd === state.examConfig.adminPassword) {
      state.isAdmin = true;
      Util.showToast('登录成功', 'success');
      renderAdmin();
    } else {
      Util.showToast('密码错误');
    }
  }

  function adminLogout() {
    state.isAdmin = false;
    renderAdmin();
  }

  function toggleExamStatus() {
    var newStatus = state.examConfig.status === 1 ? 2 : 1;
    var actionText = newStatus === 1 ? '开启' : '关闭';
    Util.showModal(actionText + '考试', '确定要' + actionText + '考试吗？' + (newStatus === 2 ? '关闭后学生将无法进入考试。' : ''), '确认' + actionText).then(function(confirmed) {
      if (!confirmed) return;
      state.examConfig.status = newStatus;
      Storage.set('exam_config', state.examConfig);
    // 上传到云端
    if (Cloud.isConfigured()) {
      Cloud.saveExamConfig(state.examConfig).catch(function() {});
    }
      Util.showToast('已' + actionText + '考试', 'success');
      renderAdmin();
    });
  }

  // ========== 考试配置页 ==========
  function renderAdminConfig() {
    var config = state.examConfig;
    var questionTypes = Converter.QUESTION_TYPES.map(function(t) {
      var weight = config.typeWeights && config.typeWeights[t.id] != null ? config.typeWeights[t.id] : (1 / Converter.QUESTION_TYPES.length);
      var locked = config.typeWeightsLocked && config.typeWeightsLocked[t.id] ? true : false;
      return { id: t.id, name: t.name, weight: weight, locked: locked };
    });

    var typeHtml = '';
    questionTypes.forEach(function(t) {
      typeHtml +=
        '<div class="type-config-item">' +
          '<label style="display:flex;align-items:center;gap:8px;flex:1;">' +
            '<input type="checkbox" data-type-lock="' + t.id + '" ' + (t.locked ? 'checked' : '') + ' onchange="window.App.lockTypeWeight(this)" style="width:18px;height:18px;cursor:pointer;">' +
            '<span class="type-config-name">' + t.name + '</span>' +
          '</label>' +
          '<div style="display:flex;align-items:center;gap:8px;">' +
            '<input type="number" class="type-config-num" min="0" max="100" value="' + Math.round(t.weight * 100) + '" data-type-id="' + t.id + '" oninput="window.App.updateTypeWeight(this)" style="width:60px;padding:4px 8px;border:1px solid #e5e7eb;border-radius:6px;text-align:center;">' +
            '<span style="width:30px;">%</span>' +
          '</div>' +
          '<input type="range" class="type-config-slider" min="0" max="100" value="' + Math.round(t.weight * 100) + '" data-type-id="' + t.id + '" oninput="window.App.updateTypeWeight(this)" style="flex:1;">' +
        '</div>';
    });

    var statusText = config.status === 1 ? '进行中' : (config.status === 2 ? '已结束' : '未开启');
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
      '</div>' +

      '<div class="card"><div class="card-title">难度配置</div>' +
        '<div class="form-row">' +
          '<div class="form-group flex-1"><label class="form-label">基础题最大值</label><input class="form-input" type="number" data-input="config-basic-max" value="' + config.basicMax + '"></div>' +
          '<div class="form-group flex-1"><label class="form-label">进阶题最大值</label><input class="form-input" type="number" data-input="config-advanced-max" value="' + config.advancedMax + '"></div>' +
        '</div>' +
        '<div class="form-group"><label class="form-label">进阶题占比：' + Math.round(config.advancedRatio * 100) + '%</label><input type="range" class="full-slider" min="0" max="100" value="' + Math.round(config.advancedRatio * 100) + '" oninput="window.App.updateAdvancedRatio(this)"></div>' +
      '</div>' +

      '<div class="card"><div class="card-title-row"><div class="card-title">题型权重配置</div><div class="reset-link" data-action="reset-type-weights">重置为平均</div></div>' +
        '<div class="type-tip">调整各题型在试卷中的占比，权重越高题目越多</div>' +
        typeHtml +
      '</div>' +

      '<div class="card"><div class="card-title">安全配置</div>' +
        '<div class="form-item-click" data-action="change-password"><div class="form-label">管理员密码</div><div class="form-value">点击修改（当前：已设置）</div></div>' +
      '</div>' +

      (function(){ var c = Cloud.getConfig(); var on = Cloud.isConfigured();
        return '<div class="card"><div class="card-title">云端配置（Supabase）</div>' +
        '<div class="card-desc">配置后学生成绩自动上传云端，老师可在监控页实时查看所有学生数据。</div>' +
        '<div class="form-group"><label class="form-label">Supabase URL</label><input class="form-input" type="text" data-input="cloud-url" placeholder="https://xxx.supabase.co" value="' + c.url + '"></div>' +
        '<div class="form-group"><label class="form-label">anon Key</label><input class="form-input" type="text" data-input="cloud-key" placeholder="eyJhbGciOi..." value="' + c.anonKey + '"></div>' +
        '<button class="btn btn-primary mt-16" data-action="save-cloud-config">' + (on ? '更新云端配置' : '保存云端配置') + '</button>' +
      '</div>'; })() +

      '<div class="action-area">' +
        '<button class="btn btn-primary" data-action="save-config">保存配置</button>' +
        '<button class="btn btn-secondary mt-16" data-action="reset-config">恢复默认配置</button>' +
        '<button class="btn btn-secondary mt-16" data-action="go-admin">返回管理首页</button>' +
      '</div>';
  }

  // 暴露给内联事件的方法
  window.App = {
    updateTypeWeight: function(el) {
      var typeId = el.dataset.typeId;
      var weight = parseInt(el.value) / 100;
      if (!state.examConfig.typeWeights) state.examConfig.typeWeights = {};
      state.examConfig.typeWeights[typeId] = weight;
      el.previousElementSibling.textContent = Math.round(weight * 100) + '%';
    },
    updateAdvancedRatio: function(el) {
      state.examConfig.advancedRatio = parseInt(el.value) / 100;
      el.previousElementSibling.textContent = '进阶题占比：' + el.value + '%';
    },
    toggleAllowRetake: function(el) {
      state.examConfig.allowRetake = el.checked;
    }
  };

  function saveConfig() {
    if (!state.examConfig.examName || !state.examConfig.examName.trim()) {
      Util.showToast('请输入考试名称');
      return;
    }
    Storage.set('exam_config', state.examConfig);
    Util.showToast('保存成功', 'success');
    setTimeout(function() { renderPage('admin'); }, 1000);
  }

  function resetConfig() {
    Util.showModal('恢复默认', '确定要恢复默认配置吗？当前修改将丢失。', '恢复默认').then(function(confirmed) {
      if (!confirmed) return;
      state.examConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      Storage.set('exam_config', state.examConfig);
      Util.showToast('已恢复默认', 'success');
      renderAdminConfig();
    });
  }

  function changePassword() {
    Util.showModal('修改管理员密码', '请输入新密码（在弹出的输入框中输入）', '确定').then(function() {
      // 用 prompt 替代
      var newPwd = prompt('请输入新的管理员密码：');
      if (newPwd && newPwd.trim()) {
        state.examConfig.adminPassword = newPwd.trim();
        Util.showToast('密码已更新，保存后生效', 'success');
      }
    });
  }

  function resetTypeWeights() {
    state.examConfig.typeWeights = {};
    renderAdminConfig();
  }

  // ========== 成绩管理页 ==========
  function renderAdminScores() {
    var bodyEl = document.getElementById('admin-scores-content');
    if (bodyEl) bodyEl.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><div>正在从云端加载...</div></div>';
    if (Cloud.isConfigured()) {
      Cloud.fetchAllRecords(1000).then(function(records) {
        // 统一字段映射：蛇形 -> 驼峰
        records = records.map(function(r) {
          return {
            id: r.id,
            studentId: r.student_id,
            name: r.name,
            clazz: r.clazz || '',
            score: r.score,
            correctCount: r.correct_count,
            totalCount: r.total_count,
            duration: r.duration,
            submitTime: r.submit_time,
            isTimeout: r.is_timeout,
            blurCount: r.blur_count,
            deviceFingerprint: r.device_fingerprint,
            deviceModel: r.device_model
          };
        });
        // 存到全局，供详情页使用
        state.cloudRecords = records;
        var scoresMap = {};
        records.forEach(function(r) {
          var sid = r.studentId;
          if (!scoresMap[sid]) {
            scoresMap[sid] = { studentId: sid, name: r.name, clazz: r.clazz, maxScore: r.score, latestScore: r.score, examCount: 1, latestBlurCount: r.blurCount, maxBlurCount: r.blurCount, latestSubmitTime: r.submitTime };
          } else {
            var s = scoresMap[sid];
            s.maxScore = Math.max(s.maxScore, r.score);
            s.latestScore = r.score;
            s.examCount++;
            s.maxBlurCount = Math.max(s.maxBlurCount, r.blurCount);
            s.latestSubmitTime = r.submitTime;
          }
        });
        renderScoresList(Object.values(scoresMap));
      }).catch(function() {
        renderScoresList(Storage.get('scores', []));
      });
    } else {
      renderScoresList(Storage.get('scores', []));
    }
  }

  function renderScoresList(scores) {
    // 排序
    if (state.adminSortBy === 'maxScore') {
      scores.sort(function(a, b) { return b.maxScore - a.maxScore || b.latestSubmitTime - a.latestSubmitTime; });
    } else if (state.adminSortBy === 'latest') {
      scores.sort(function(a, b) { return b.latestSubmitTime - a.latestSubmitTime; });
    } else if (state.adminSortBy === 'studentId') {
      scores.sort(function(a, b) { return a.studentId.localeCompare(b.studentId); });
    }
    // 搜索
    if (state.adminSearchKeyword && state.adminSearchKeyword.trim()) {
      var kw = state.adminSearchKeyword.trim().toLowerCase();
      scores = scores.filter(function(s) {
        return s.studentId.toLowerCase().indexOf(kw) >= 0 || s.name.toLowerCase().indexOf(kw) >= 0;
      });
    }

    var avgScore = scores.length > 0 ? Math.round(scores.reduce(function(s, i) { return s + i.maxScore; }, 0) / scores.length * 10) / 10 : 0;

    var scoresHtml = '';
    if (scores.length === 0) {
      scoresHtml = '<div class="empty"><div class="empty-icon">📊</div><div>暂无成绩数据</div></div>';
    } else {
      scores.forEach(function(s, idx) {
        var rankClass = idx < 3 ? 'rank-' + (idx + 1) : 'rank-normal';
        scoresHtml +=
          '<div class="score-row" data-action="view-student-detail" data-studentid="' + s.studentId + '">' +
            '<div class="score-rank ' + rankClass + '">' + (idx + 1) + '</div>' +
            '<div class="score-student"><div class="ss-name">' + s.name + '</div><div class="ss-id">' + s.studentId + (s.clazz ? ' · ' + s.clazz : '') + '</div></div>' +
            '<div class="score-info-text"><div class="si-score">' + s.maxScore + '<span class="si-unit">分</span></div><div class="si-meta">最新：' + s.latestScore + '分 · ' + s.examCount + '次' + ((s.maxBlurCount || 0) > 0 ? ' · <span style="color:#EF4444;">切屏' + s.maxBlurCount + '次</span>' : '') + '</div></div>' +
            '<div class="score-arrow">›</div>' +
          '</div>';
      });
    }

    var sortTabClass = function(sort) { return state.adminSortBy === sort ? 'active' : ''; };

    document.getElementById('admin-scores-content').innerHTML =
      '<div class="scores-toolbar">' +
        '<input class="search-input" type="text" data-input="admin-search" placeholder="搜索学号或姓名" value="' + (state.adminSearchKeyword || '') + '">' +
        '<button class="btn btn-primary btn-sm" data-action="export-scores">📥 导出</button>' +
      '</div>' +

      '<div class="sort-tabs">' +
        '<div class="sort-tab ' + sortTabClass('maxScore') + '" data-action="sort-scores" data-sort="maxScore">按最高分</div>' +
        '<div class="sort-tab ' + sortTabClass('latest') + '" data-action="sort-scores" data-sort="latest">按最新提交</div>' +
        '<div class="sort-tab ' + sortTabClass('studentId') + '" data-action="sort-scores" data-sort="studentId">按学号</div>' +
      '</div>' +

      '<div class="scores-stats">共 ' + scores.length + ' 名学生' + (scores.length > 0 ? ' · 平均分：' + avgScore : '') + '</div>' +

      scoresHtml +

      '<div class="bottom-actions"><button class="btn btn-secondary" data-action="go-admin">返回管理首页</button></div>';
  }

  function sortScores(sort) {
    state.adminSortBy = sort;
    renderAdminScores();
  }

  function exportScores() {
    var scores = Storage.get('scores', []);
    if (scores.length === 0) { Util.showToast('暂无成绩可导出'); return; }
    Util.exportCSV(scores);
    Util.showToast('导出成功', 'success');
  }

  function viewStudentDetail(studentId) {
    var records = Storage.get('exam_records', [])
      .filter(function(r) { return r.studentId === studentId; })
      .sort(function(a, b) { return b.submitTime - a.submitTime; });

    if (records.length === 0) {
      Util.showToast('该学生暂无考试记录');
      return;
    }

    // 显示学生详情弹窗
    var studentName = records[0].name;
    var stats = {
      totalExams: records.length,
      maxScore: Math.max.apply(null, records.map(function(r) { return r.score; })),
      avgScore: Math.round(records.reduce(function(s, r) { return s + r.score; }, 0) / records.length * 10) / 10
    };

    var recordsHtml = '';
    records.forEach(function(r, idx) {
      var scoreClass = r.score >= 90 ? 'score-high' : r.score >= 60 ? 'score-mid' : 'score-low';
      recordsHtml +=
        '<div class="detail-record">' +
          '<div class="dr-score ' + scoreClass + '">' + r.score + '</div>' +
          '<div class="dr-content">' +
            '<div>正确 ' + (r.correct_count || r.correctCount) + '/' + (r.total_count || r.totalCount) + ' · 用时 ' + Util.formatDuration(r.duration) + '</div>' +
            '<div class="dr-time">' + Util.formatTime(r.submit_time || r.submitTime) + '</div>' +
          '</div>' +
        '</div>';
    });

    var mask = document.createElement('div');
    mask.className = 'modal-mask';
    mask.innerHTML =
      '<div class="modal-box modal-large">' +
        '<div class="modal-title">' + studentName + ' 的考试记录</div>' +
        '<div class="modal-stats">' +
          '<span>共 ' + stats.totalExams + ' 次</span>' +
          '<span>最高分 ' + stats.maxScore + '</span>' +
          '<span>平均分 ' + stats.avgScore + '</span>' +
        '</div>' +
        '<div class="modal-records">' + recordsHtml + '</div>' +
        '<div class="modal-buttons"><button class="modal-btn modal-confirm">关闭</button></div>' +
      '</div>';
    document.body.appendChild(mask);
    mask.querySelector('.modal-confirm').onclick = function() { mask.remove(); };
    mask.querySelector('.modal-box').onclick = function(e) { e.stopPropagation(); };
    mask.onclick = function() { mask.remove(); };
  }

  // ========== 数据管理页 ==========
  function renderAdminData() {
    var scores = Storage.get('scores', []);
    var records = Storage.get('exam_records', []);
    var stats = {
      totalStudents: scores.length,
      totalExams: records.length
    };

    document.getElementById('admin-data-content').innerHTML =
      '<div class="card"><div class="card-title">数据概览</div>' +
        '<div class="data-stats-row">' +
          '<div class="ds-item"><div class="ds-num">' + stats.totalStudents + '</div><div class="ds-label">学生数</div></div>' +
          '<div class="ds-item"><div class="ds-num">' + stats.totalExams + '</div><div class="ds-label">考试记录</div></div>' +
        '</div>' +
      '</div>' +

      '<div class="card"><div class="card-title">数据操作</div>' +
        '<div class="data-action-item" data-action="export-backup"><div class="dai-icon">💾</div><div class="dai-content"><div class="dai-title">导出数据备份</div><div class="dai-desc">导出所有考试数据为JSON文件，可用于备份或迁移</div></div><div class="dai-arrow">›</div></div>' +
        '<div class="divider"></div>' +
        '<div class="data-action-item danger" data-action="clear-exam-data"><div class="dai-icon">🗑️</div><div class="dai-content"><div class="dai-title">清空考试数据</div><div class="dai-desc">删除所有考试记录和成绩，保留学生身份信息</div></div><div class="dai-arrow">›</div></div>' +
        '<div class="divider"></div>' +
        '<div class="data-action-item danger" data-action="reset-all"><div class="dai-icon">⚠️</div><div class="dai-content"><div class="dai-title">全量重置系统</div><div class="dai-desc">删除所有数据（含学生信息），系统恢复初始状态</div></div><div class="dai-arrow">›</div></div>' +
      '</div>' +

      '<div class="warning-card">' +
        '<div class="warning-title">⚠️ 安全提示</div>' +
        '<div class="warning-item">1. 清空和重置操作不可恢复，请谨慎操作。</div>' +
        '<div class="warning-item">2. 建议在清空前先导出数据备份。</div>' +
        '<div class="warning-item">3. 全量重置后需要重新配置考试参数。</div>' +
        '<div class="warning-item">4. 数据存储在浏览器本地，清除浏览器缓存也会丢失数据。</div>' +
      '</div>' +

      '<div class="bottom-actions"><button class="btn btn-secondary" data-action="go-admin">返回管理首页</button></div>';
  }

  function clearExamData() {
    var records = Storage.get('exam_records', []);
    Util.showModal('清空考试数据', '此操作将删除所有考试记录和成绩数据（共 ' + records.length + ' 条记录），但保留学生身份信息。\n\n此操作不可恢复，确定要继续吗？', '确认清空').then(function(c1) {
      if (!c1) return;
      Util.showModal('再次确认', '数据清空后将无法恢复，确定要清空所有考试数据吗？', '我确定清空').then(function(c2) {
        if (!c2) return;
        Storage.remove('exam_records');
        Storage.remove('scores');
        // 清除所有进度
        var keys = [];
        for (var i = 0; i < localStorage.length; i++) {
          var k = localStorage.key(i);
          if (k && k.indexOf('base_exam_exam_progress_') === 0) keys.push(k);
        }
        keys.forEach(function(k) { localStorage.removeItem(k); });
        Util.showToast('清空成功', 'success');
        renderAdminData();
      });
    });
  }

  function resetAll() {
    Util.showModal('全量重置系统', '此操作将删除所有数据，包括：\n- 所有考试记录和成绩\n- 所有学生身份信息\n- 系统将恢复到初始状态\n\n此操作不可恢复，确定要继续吗？', '确认重置').then(function(c1) {
      if (!c1) return;
      var input = prompt('请输入 "RESET" 确认全量重置系统：');
      if (input !== 'RESET') {
        Util.showToast('已取消重置');
        return;
      }
      Storage.clearAll();
      state.examConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      Storage.set('exam_config', state.examConfig);
      state.userInfo = null;
      state.isAdmin = false;
      Util.showToast('系统已重置', 'success');
      setTimeout(function() { renderPage('home'); }, 1500);
    });
  }

  function exportBackup() {
    var backup = {
      exportTime: Util.formatTime(Date.now()),
      examConfig: state.examConfig,
      scores: Storage.get('scores', []),
      examRecords: Storage.get('exam_records', []),
      users: Storage.get('users', [])
    };
    var blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = '数据备份_' + Util.formatTime(Date.now(), 'YYYYMMDD_HHmmss') + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    Util.showToast('备份导出成功', 'success');
  }

  // ========== 学生名单管理 ==========
  function renderAdminStudents() {
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
        '<div class="card-title">手动添加学生</div>' +
        '<div class="card-desc">用于补充漏掉的个别学生，填写后点添加</div>' +
        '<div class="form-group"><label class="form-label">学号</label><input class="form-input" type="text" id="add-sid" placeholder="请输入学号"></div>' +
        '<div class="form-group"><label class="form-label">姓名</label><input class="form-input" type="text" id="add-sname" placeholder="请输入姓名"></div>' +
        '<div class="form-group"><label class="form-label">班级</label><input class="form-input" type="text" id="add-sclass" placeholder="请输入班级，如：计科2401"></div>' +
        '<button class="btn btn-primary mt-16" data-action="add-student">➕ 添加学生</button>' +
      '</div>' +

      '<div class="card">' +
        '<div class="card-title">CSV文件导入</div>' +
        '<div class="card-desc">导入CSV格式名单，列：学号,姓名,班级</div>' +
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
  }

  function downloadTemplate() {
    var csv = '\uFEFF' + '学号,姓名,班级\n2024001,张三,计科2401\n2024002,李四,计科2401\n2024003,王五,软工2401';
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = '学生名单模板.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    Util.showToast('模板已下载', 'success');
  }

  window.App.handleStudentFile = function(input) {
    var file = input.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function(e) {
      var text = e.target.result;
      var lines = text.split(/\r?\n/);
      var students = [];
      var skipped = 0;

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (!line) continue;
        // 跳过表头
        if (i === 0 && (line.indexOf('学号') >= 0 || line.indexOf('student') >= 0 || line.indexOf('name') >= 0)) {
          continue;
        }
        var parts = line.split(/[,，\t]/);
        if (parts.length >= 2) {
          var sid = parts[0].trim();
          var name = parts[1].trim();
          var clazz = parts[2] ? parts[2].trim() : '';
          if (sid && name) {
            students.push({ studentId: sid, name: name, clazz: clazz });
          } else {
            skipped++;
          }
        } else {
          skipped++;
        }
      }

      if (students.length === 0) {
        Util.showToast('未解析到有效数据，请检查文件格式');
        return;
      }

      Util.showModal('导入确认',
        '成功解析 ' + students.length + ' 名学生' + (skipped > 0 ? '，跳过 ' + skipped + ' 行无效数据' : '') + '。\n\n导入后将覆盖现有名单，确定吗？',
        '确认导入').then(function(confirmed) {
        if (!confirmed) return;
        state.studentList = students;
    // 同步到云端
    if (Cloud.isConfigured()) {
      Cloud.clearStudentList().then(function() {
        Cloud.uploadStudentList(students).catch(function() {});
      }).catch(function() {});
    }
        Storage.set('student_list', students);
        Util.showToast('成功导入 ' + students.length + ' 名学生', 'success');
        renderAdminStudents();
      });
    };
    reader.readAsText(file, 'UTF-8');
    input.value = '';
  };

  function batchImportStudents() {
    var text = document.getElementById('batch-students').value.trim();
    if (!text) {
      Util.showToast('请输入学生信息');
      return;
    }
    var lines = text.split('\n');
    var added = 0;
    var skipped = 0;
    lines.forEach(function(line) {
      line = line.trim();
      if (!line) return;
      // 支持空格、逗号、制表符分隔
      var parts = line.split(/[\s,，\t]+/);
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

  function addStudent() {
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
    // 同步到云端
    if (Cloud.isConfigured()) {
      Cloud.uploadStudentList([{ studentId: sid, name: name, clazz: clazz }]).catch(function() {});
    }
    Storage.set('student_list', state.studentList);
    Util.showToast('添加成功', 'success');
    renderAdminStudents();
  }

  function clearStudentList() {
    Util.showModal('清空名单',
      '确定要清空所有学生名单吗？\n清空后学生身份校验将关闭。',
      '确认清空').then(function(confirmed) {
      if (!confirmed) return;
      state.studentList = [];
    // 同步清空云端
    if (Cloud.isConfigured()) {
      Cloud.clearStudentList().catch(function() {});
    }
      Storage.set('student_list', []);
      Util.showToast('已清空', 'success');
      renderAdminStudents();
    });
  }

  // ========== 二维码生成 ==========
  function showQRCode() {
    var url = window.location.href;

    // 创建弹窗
    var modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML =
      '<div class="modal-mask"></div>' +
      '<div class="modal-content">' +
        '<div class="modal-title">考试二维码</div>' +
        '<div class="modal-body" style="text-align:center;">' +
          '<p style="font-size:14px;color:var(--gray-600);margin-bottom:16px;">学生扫码即可进入考试</p>' +
          '<div id="qrcode-box" style="display:inline-block;padding:16px;background:#fff;border-radius:12px;"></div>' +
          '<p style="font-size:12px;color:var(--gray-500);margin-top:16px;word-break:break-all;line-height:1.5;">' + url + '</p>' +
        '</div>' +
        '<div class="modal-buttons">' +
          '<button class="modal-btn modal-confirm" id="qrcode-close-btn">关闭</button>' +
        '</div>' +
      '</div>';

    document.body.appendChild(modal);

    // 生成二维码
    var qrcodeEl = modal.querySelector('#qrcode-box');
    if (window.QRCode) {
      new QRCode(qrcodeEl, {
        text: url,
        width: 180,
        height: 180,
        colorDark: '#1F2937',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.M
      });
    } else {
      qrcodeEl.innerHTML = '<p style="color:var(--danger);">二维码库加载失败，请检查网络</p>';
    }

    // 关闭事件
    modal.querySelector('.modal-mask').onclick = function() { document.body.removeChild(modal); };
    modal.querySelector('#qrcode-close-btn').onclick = function() { document.body.removeChild(modal); };
  }

  // ========== 云端配置 ==========
  function saveCloudConfig() {
    var url = (state._cloudUrl || '').trim();
    var key = (state._cloudKey || '').trim();
    if (!url || !key) { Util.showToast('请填写完整的URL和Key'); return; }
    Cloud.setConfig({ url: url, anonKey: key });
    Util.showToast('云端配置已保存', 'success');
    renderAdminConfig();
  }

  // ========== 考试监控 ==========
  function renderAdminMonitor() {
    var isCloud = Cloud.isConfigured();
    var cloudStatus = isCloud ? '云端模式' : '本地模式（未配置云端）';
    document.getElementById('admin-monitor-content').innerHTML =
      '<div class="admin-header"><div class="admin-title">考试监控</div><div class="admin-logout" data-action="go-admin">返回</div></div>' +
      '<div class="cloud-status-bar"><span class="cloud-badge '+(isCloud?'cloud-on':'cloud-off')+'">'+cloudStatus+'</span>'+
      (isCloud?'<button class="btn btn-sm btn-primary" data-action="refresh-cloud-data">🔄 刷新</button>':'')+'</div>' +
      '<div id="monitor-body"><div class="empty">加载中...</div></div>' +
      '<div class="warning-card"><div class="warning-title">⚠️ 监控说明</div>' +
      '<div class="warning-item">1. 切屏会被自动记录，次数多的请重点关注。</div>' +
      '<div class="warning-item">2. 同一台手机绑定一名考生，换设备会被拦截。</div>' +
      '<div class="warning-item">3. 切屏超3次重点关注，超5次成绩可作废。</div></div>';
    loadMonitorData();
  }

  function loadMonitorData() {
    var bodyEl = document.getElementById('monitor-body');
    if (!bodyEl) return;
    function renderLocal() {
      renderMonitorBody(Storage.get('scores', []), [], false);
    }
    if (Cloud.isConfigured()) {
      Cloud.fetchAllRecords(500).then(function(res) {
        var records = res.results || [];
        var m = {};
        records.forEach(function(r) {
          var sid = r.student_id || r.studentId;
          var bc = r.blur_count || r.blurCount || 0;
          var dm = r.device_model || r.deviceModel || '未知';
          if (!m[sid]) m[sid] = { studentId: sid, name: r.name, latestScore: r.score, maxBlurCount: bc, deviceModel: dm };
          else { m[sid].maxBlurCount = Math.max(m[sid].maxBlurCount, bc); m[sid].latestScore = r.score; }
        });
        renderMonitorBody(Object.values(m), records, true);
      }).catch(function() { renderLocal(); });
    } else {
      renderLocal();
    }
  }

  function renderMonitorBody(scores, records, isCloud) {
    var bodyEl = document.getElementById('monitor-body');
    if (!bodyEl) return;
    var cheating = scores.filter(function(s){return (s.maxBlurCount||0)>0;}).length;
    var rows = scores.map(function(s){
      return {name:s.name, sid:s.studentId, score:s.latestScore, blur:s.maxBlurCount||0, dev:s.deviceModel||'未知'};
    }).sort(function(a,b){return b.blur-a.blur;});
    var html = rows.length===0 ? '<div class="empty">暂无考试数据</div>' :
      rows.map(function(r){
        var w = r.blur>0?'warning':'';
        return '<div class="monitor-row '+w+'"><div class="monitor-main"><div class="monitor-name">'+r.name+' <span class="monitor-sid">'+r.sid+'</span></div><div class="monitor-device">📱 '+r.dev+'</div></div><div class="monitor-right"><div class="monitor-score">'+r.score+'分</div><div class="monitor-blur '+(r.blur>0?'has-blur':'')+'">切屏 '+r.blur+'次</div></div></div>';
      }).join('');
    bodyEl.innerHTML =
      '<div class="monitor-summary">'+
        '<div class="ms-item"><div class="ms-num">'+scores.length+'</div><div class="ms-label">已考学生</div></div>'+
        '<div class="ms-item"><div class="ms-num '+(cheating>0?'text-danger':'text-success')+'">'+cheating+'</div><div class="ms-label">有切屏记录</div></div>'+
        '<div class="ms-item"><div class="ms-num">'+(isCloud?records.length:0)+'</div><div class="ms-label">'+(isCloud?'考试记录':'绑定设备')+'</div></div></div>'+
      '<div class="card"><div class="card-title">学生防作弊监控'+(isCloud?'（云端）':'')+'</div>'+html+'</div>';
  }


  // ========== 启动 ==========
  document.addEventListener('DOMContentLoaded', init);
})();
