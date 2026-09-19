/**
 * Supabase 云端同步模块
 * 纯REST API实现，无需SDK
 */
window.Cloud = (function() {

  var config = {
    url: 'https://uazwtblpwayqlpczczai.supabase.co',
    anonKey: 'sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs'
  };

  // 从本地存储加载配置
  function loadConfig() {
    var saved = JSON.parse(localStorage.getItem('base_exam_cloud_config') || '{}');
    if (saved.url) config.url = saved.url;
    if (saved.anonKey) config.anonKey = saved.anonKey;
  }
  loadConfig();

  function setConfig(cfg) {
    config.url = (cfg.url || '').replace(/\/$/, ''); // 去掉末尾斜杠
    config.anonKey = cfg.anonKey || '';
    localStorage.setItem('base_exam_cloud_config', JSON.stringify(config));
  }

  function getConfig() {
    return { ...config };
  }

  function isConfigured() {
    return !!config.url && !!config.anonKey;
  }

  // 通用请求
  function request(method, path, data) {
    return new Promise(function(resolve, reject) {
      if (!isConfigured()) {
        reject(new Error('云端未配置'));
        return;
      }

      var xhr = new XMLHttpRequest();
      xhr.open(method, config.url + '/rest/v1' + path);
      xhr.setRequestHeader('apikey', config.anonKey);
      xhr.setRequestHeader('Authorization', 'Bearer ' + config.anonKey);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader('Prefer', 'return=representation');

      xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch (e) {
            resolve(xhr.responseText);
          }
        } else {
          reject(new Error('HTTP ' + xhr.status + ': ' + xhr.responseText.substring(0, 100)));
        }
      };
      xhr.onerror = function() {
        reject(new Error('网络请求失败'));
      };

      xhr.send(data ? JSON.stringify(data) : undefined);
    });
  }

  // ========== 考试记录 ==========
  // 上传考试记录
  function uploadRecord(record) {
    return request('POST', '/exam_records', [record]);
  }

  // 查询所有考试记录（按提交时间降序）
  function fetchAllRecords(limit) {
    limit = limit || 500;
    return request('GET', '/exam_records?select=*&order=submitTime.desc&limit=' + limit);
  }

  // 按学号查询某学生的所有记录
  function fetchRecordsByStudent(studentId) {
    return request('GET', '/exam_records?select=*&studentId=eq.' + encodeURIComponent(studentId) + '&order=submitTime.desc');
  }

  // ========== 学生名单 ==========
  // 上传学生名单（批量）
  function uploadStudentList(students) {
    var rows = students.map(function(s) {
      return { student_id: s.studentId, name: s.name };
    });
    return request('POST', '/students', rows);
  }

  // 拉取学生名单
  function fetchStudentList() {
    return request('GET', '/students?select=*&order=student_id');
  }

  // 清空学生名单
  function clearStudentList() {
    return request('DELETE', '/students?id=gt.0');
  }

  // ========== 设备绑定 ==========
  // 检查设备是否已绑定其他学号
  function checkDeviceBinding(fingerprint) {
    return request('GET', '/device_bindings?select=*&fingerprint=eq.' + encodeURIComponent(fingerprint));
  }

  // 上传设备绑定
  function uploadDeviceBinding(binding) {
    return request('POST', '/device_bindings', [binding]);
  }

  // ========== 工具 ==========
  // 测试连接
  function testConnection() {
    return request('GET', '/exam_records?select=id&limit=1');
  }

  return {
    setConfig: setConfig,
    getConfig: getConfig,
    isConfigured: isConfigured,
    uploadRecord: uploadRecord,
    fetchAllRecords: fetchAllRecords,
    fetchRecordsByStudent: fetchRecordsByStudent,
    uploadStudentList: uploadStudentList,
    fetchStudentList: fetchStudentList,
    clearStudentList: clearStudentList,
    checkDeviceBinding: checkDeviceBinding,
    uploadDeviceBinding: uploadDeviceBinding,
    testConnection: testConnection
  };
})();
