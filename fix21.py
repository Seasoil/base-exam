with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改题型权重配置
old = """    var questionTypes = Converter.QUESTION_TYPES.map(function(t) {
      var weight = config.typeWeights && config.typeWeights[t.id] != null ? config.typeWeights[t.id] : (1 / Converter.QUESTION_TYPES.length);
      return { id: t.id, name: t.name, weight: weight };
    });

    var typeHtml = '';
    questionTypes.forEach(function(t) {
      typeHtml +=
        '<div class="type-config-item">' +
          '<div class="type-config-name">' + t.name + '</div>' +
          '<div class="type-config-weight">' + Math.round(t.weight * 100) + '%</div>' +
          '<input type="range" class="type-config-slider" min="0" max="100" value="' + Math.round(t.weight * 100) + '" data-type-id="' + t.id + '" oninput="window.App.updateTypeWeight(this)">' +
        '</div>';
    });"""

new = """    var questionTypes = Converter.QUESTION_TYPES.map(function(t) {
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
    });"""

content = content.replace(old, new)

# 加lockTypeWeight函数
old_update = """  function updateTypeWeight(el) {
    var typeId = el.dataset.typeId;
    var val = parseInt(el.value) / 100;
    if (!state.examConfig.typeWeights) state.examConfig.typeWeights = {};
    state.examConfig.typeWeights[typeId] = val;
    Storage.set('exam_config', state.examConfig);
    // 更新显示
    var nameEl = el.closest('.type-config-item').querySelector('.type-config-weight');
    if (nameEl) nameEl.textContent = Math.round(val * 100) + '%';
  }"""

new_update = """  function updateTypeWeight(el) {
    var typeId = el.dataset.typeId;
    var val = Math.min(100, Math.max(0, parseInt(el.value) || 0)) / 100;
    if (!state.examConfig.typeWeights) state.examConfig.typeWeights = {};
    state.examConfig.typeWeights[typeId] = val;
    Storage.set('exam_config', state.examConfig);
    // 同步slider和数字框
    var slider = document.querySelector('input[type="range"][data-type-id="' + typeId + '"]');
    var num = document.querySelector('input[type="number"][data-type-id="' + typeId + '"]');
    if (slider && slider !== el) slider.value = Math.round(val * 100);
    if (num && num !== el) num.value = Math.round(val * 100);
  }

  function lockTypeWeight(el) {
    var typeId = el.dataset.typeLock;
    if (!state.examConfig.typeWeightsLocked) state.examConfig.typeWeightsLocked = {};
    state.examConfig.typeWeightsLocked[typeId] = el.checked;
    Storage.set('exam_config', state.examConfig);
    // 如果锁定了，重新计算未锁定的占比
    if (el.checked) {
      var lockedSum = 0;
      var lockedCount = 0;
      var allTypes = Converter.QUESTION_TYPES;
      allTypes.forEach(function(t) {
        if (state.examConfig.typeWeightsLocked[t.id]) {
          lockedSum += state.examConfig.typeWeights[t.id] || 0;
          lockedCount++;
        }
      });
      var remain = 1 - lockedSum;
      var unLockedCount = allTypes.length - lockedCount;
      if (unLockedCount > 0) {
        var each = remain / unLockedCount;
        allTypes.forEach(function(t) {
          if (!state.examConfig.typeWeightsLocked[t.id]) {
            state.examConfig.typeWeights[t.id] = each;
          }
        });
      }
      Storage.set('exam_config', state.examConfig);
      renderAdminConfig();
    }
  }"""

content = content.replace(old_update, new_update)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
