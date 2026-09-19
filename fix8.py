with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 默认状态改为关闭(0)
old_default = """  var DEFAULT_CONFIG = {
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
    status: 1,
    adminPassword: 'cjdxjsjkxxy'
  };"""

new_default = """  var DEFAULT_CONFIG = {
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
  };"""

content = content.replace(old_default, new_default)

# 2. 初始化时从云端拉取配置
old_init = """  function init() {
    // 加载配置
    var config = Storage.get('exam_config', null);
    if (!config) {
      config = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      Storage.set('exam_config', config);
    }
    state.examConfig = config;"""

new_init = """  function init() {
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
    }"""

content = content.replace(old_init, new_init)

# 3. 保存配置时上传到云端
old_save = """    Storage.set('exam_config', state.examConfig);"""
new_save = """    Storage.set('exam_config', state.examConfig);
    // 上传到云端
    if (Cloud.isConfigured()) {
      Cloud.saveExamConfig(state.examConfig).catch(function() {});
    }"""
# 只替换第一个
content = content.replace(old_save, new_save, 1)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
