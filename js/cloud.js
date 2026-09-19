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
    config.url = (cfg.url || '').replace(/\/$/, '');
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

  // ========== 考试配置 ==========
  // 保存考试配置到云端（id=1，全局唯一）
  function saveExamConfig(cfg) {
    var row = { id: 1, data: JSON.stringify(cfg), updated_at: new Date().toISOString() };
    return request('POST', '/exam_config?on_conflict=id', [row]);
  }

  // 从云端拉取考试配置
  function fetchExamConfig() {
    return request('GET', '/exam_config?id=eq.1&select=*');
  }

  // ========== 考试记录 ==========
  function uploadRecord(record) {
    return request('POST', '/exam_records', [record]);
  }

  function fetchAllRecords(limit) {
    limit = limit || 500;
    return request('GET', '/exam_records?select=*&order=submit_time.desc&limit=' + limit);
  }

  function fetchRecordsByStudent(studentId) {
    return request('GET', '/exam_records?select=*&student_id=eq.' + encodeURIComponent(studentId) + '&order=submit_time.desc');
  }

  // ========== 学生名单 ==========
  function uploadStudentList(students) {
    var rows = students.map(function(s) {
      return { student_id: s.studentId, name: s.name };
    });
    return request('POST', '/students', rows);
  }

  function fetchStudentList() {
    return request('GET', '/students?select=*&order=student_id');
  }

  function clearStudentList() {
    return request('DELETE', '/students?id=gt.0');
  }

  // ========== 设备绑定 ==========
  function checkDeviceBinding(fingerprint) {
    return request('GET', '/device_bindings?select=*&fingerprint=eq.' + encodeURIComponent(fingerprint));
  }

  function uploadDeviceBinding(binding) {
    return request('POST', '/device_bindings', [binding]);
  }

  // ========== 工具 ==========
  function testConnection() {
    return request('GET', '/exam_records?select=id&limit=1');
  }

  return {
    setConfig: setConfig,
    getConfig: getConfig,
    isConfigured: isConfigured,
    saveExamConfig: saveExamConfig,
    fetchExamConfig: fetchExamConfig,
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
