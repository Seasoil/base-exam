with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改重置为平均的逻辑
old_reset = """  function resetTypeWeights() {
    state.examConfig.typeWeights = {};
    Storage.set('exam_config', state.examConfig);
    renderAdminConfig();
  }"""

new_reset = """  function resetTypeWeights() {
    var allTypes = Converter.QUESTION_TYPES;
    // 锁定的总和
    var lockedSum = 0;
    var lockedCount = 0;
    allTypes.forEach(function(t) {
      if (state.examConfig.typeWeightsLocked && state.examConfig.typeWeightsLocked[t.id]) {
        lockedSum += state.examConfig.typeWeights[t.id] || 0;
        lockedCount++;
      }
    });
    // 剩余分配给没锁定的
    var remain = 1 - lockedSum;
    var unLockedCount = allTypes.length - lockedCount;
    if (unLockedCount > 0) {
      var each = remain / unLockedCount;
      allTypes.forEach(function(t) {
        if (!state.examConfig.typeWeightsLocked || !state.examConfig.typeWeightsLocked[t.id]) {
          state.examConfig.typeWeights[t.id] = each;
        }
      });
    }
    Storage.set('exam_config', state.examConfig);
    renderAdminConfig();
  }"""

content = content.replace(old_reset, new_reset)

# 修改lockTypeWeight，确保总和100%
old_lock = """  function lockTypeWeight(el) {
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

new_lock = """  function lockTypeWeight(el) {
    var typeId = el.dataset.typeLock;
    if (!state.examConfig.typeWeightsLocked) state.examConfig.typeWeightsLocked = {};
    state.examConfig.typeWeightsLocked[typeId] = el.checked;
    // 锁定后，重新计算未锁定的占比，确保总和100%
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
  }"""

content = content.replace(old_lock, new_lock)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
