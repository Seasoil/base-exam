/**
 * 进制转换核心工具类（H5版）
 * 支持 2/8/10/16 进制之间的相互转换
 */
window.Converter = (function() {

  // 题型定义
  var QUESTION_TYPES = [
    { id: 'bin2dec', name: '二进制 → 十进制', fromBase: 2, toBase: 10, padLength: 0, uppercase: false, questionTemplate: '二进制数 {value} 转换为十进制是？' },
    { id: 'dec2bin4', name: '十进制 → 四位二进制', fromBase: 10, toBase: 2, padLength: 4, uppercase: false, questionTemplate: '十进制数 {value} 转换为四位二进制是？（不足四位补前导零）' },
    { id: 'bin2oct', name: '二进制 → 八进制', fromBase: 2, toBase: 8, padLength: 0, uppercase: false, questionTemplate: '二进制数 {value} 转换为八进制是？' },
    { id: 'bin2hex', name: '二进制 → 十六进制', fromBase: 2, toBase: 16, padLength: 0, uppercase: true, questionTemplate: '二进制数 {value} 转换为十六进制是？（字母大写）' },
    { id: 'dec2oct', name: '十进制 → 八进制', fromBase: 10, toBase: 8, padLength: 0, uppercase: false, questionTemplate: '十进制数 {value} 转换为八进制是？' },
    { id: 'dec2hex', name: '十进制 → 十六进制', fromBase: 10, toBase: 16, padLength: 0, uppercase: true, questionTemplate: '十进制数 {value} 转换为十六进制是？（字母大写）' },
    { id: 'oct2dec', name: '八进制 → 十进制', fromBase: 8, toBase: 10, padLength: 0, uppercase: false, questionTemplate: '八进制数 {value} 转换为十进制是？' },
    { id: 'oct2bin', name: '八进制 → 二进制', fromBase: 8, toBase: 2, padLength: 0, uppercase: false, questionTemplate: '八进制数 {value} 转换为二进制是？' },
    { id: 'hex2dec', name: '十六进制 → 十进制', fromBase: 16, toBase: 10, padLength: 0, uppercase: false, questionTemplate: '十六进制数 {value} 转换为十进制是？' },
    { id: 'hex2bin', name: '十六进制 → 二进制', fromBase: 16, toBase: 2, padLength: 0, uppercase: false, questionTemplate: '十六进制数 {value} 转换为二进制是？' },
    { id: 'dec2bin', name: '十进制 → 二进制', fromBase: 10, toBase: 2, padLength: 0, uppercase: false, questionTemplate: '十进制数 {value} 转换为二进制是？' }
  ];

  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function decToBase(dec, targetBase, uppercase) {
    uppercase = uppercase !== false;
    var result = dec.toString(targetBase);
    if (targetBase === 16 && uppercase) result = result.toUpperCase();
    return result;
  }

  function generateQuestion(type, config) {
    config = config || {};
    var maxDec = 15;

    var sourceValue;
    if (type.fromBase === 10) {
      sourceValue = String(randomInt(0, maxDec));
    } else if (type.fromBase === 2) {
      sourceValue = decToBase(randomInt(0, 15), 2);
    } else if (type.fromBase === 8) {
      sourceValue = decToBase(randomInt(0, maxDec), 8);
    } else if (type.fromBase === 16) {
      sourceValue = decToBase(randomInt(0, maxDec), 16, true);
    }

    var answer = parseInt(sourceValue, type.fromBase).toString(type.toBase);
    if (type.toBase === 16 && type.uppercase) answer = answer.toUpperCase();
    if (type.padLength > 0 && answer.length < type.padLength) {
      answer = answer.padStart(type.padLength, '0');
    }

    return {
      id: 'q_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
      typeId: type.id,
      typeName: type.name,
      question: type.questionTemplate.replace('{value}', sourceValue),
      sourceValue: sourceValue,
      answer: answer,
      fromBase: type.fromBase,
      toBase: type.toBase,
      padLength: type.padLength,
      uppercase: type.uppercase
    };
  }

  function generatePaper(total, config) {
    total = total || 100;
    config = config || {};
    var typeWeights = config.typeWeights || {};
    var questions = [];
    var usedKeys = {};
    var typeCount = QUESTION_TYPES.length;
    var defaultWeight = 1 / typeCount;
    var weights = [];
    var weightSum = 0;
    for (var i = 0; i < QUESTION_TYPES.length; i++) {
      var w = typeWeights[QUESTION_TYPES[i].id] != null ? typeWeights[QUESTION_TYPES[i].id] : defaultWeight;
      weights.push(w);
      weightSum += w;
    }
    var counts = [];
    var assigned = 0;
    for (var j = 0; j < weights.length; j++) {
      var c = Math.floor((weights[j] / weightSum) * total);
      counts.push(c);
      assigned += c;
    }
    var idx = 0;
    while (assigned < total && idx < counts.length) {
      counts[idx]++;
      assigned++;
      idx++;
    }

    for (var k = 0; k < QUESTION_TYPES.length; k++) {
      var type = QUESTION_TYPES[k];
      var count = counts[k];
      var attempts = 0, generated = 0;
      while (generated < count && attempts < count * 10) {
        var q = generateQuestion(type, config);
        var key = q.typeId + '_' + q.sourceValue;
        if (!usedKeys[key]) {
          usedKeys[key] = true;
          questions.push(q);
          generated++;
        }
        attempts++;
      }
      while (generated < count) {
        questions.push(generateQuestion(type, config));
        generated++;
      }
    }

    for (var m = questions.length - 1; m > 0; m--) {
      var n = Math.floor(Math.random() * (m + 1));
      var tmp = questions[m];
      questions[m] = questions[n];
      questions[n] = tmp;
    }

    return {
      paperId: 'paper_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
      questions: questions.slice(0, total),
      generateTime: Date.now()
    };
  }

  function checkAnswer(question, userAnswer) {
    if (userAnswer === null || userAnswer === undefined) return false;
    var normalized = String(userAnswer).trim();
    if (question.toBase === 16) normalized = normalized.toUpperCase();
    return normalized === question.answer;
  }

  function generateExplanation(question, userAnswer) {
    var sourceValue = question.sourceValue;
    var answer = question.answer;
    var fromBase = question.fromBase;
    var toBase = question.toBase;
    var typeName = question.typeName;
    var baseName = { 2: '二进制', 8: '八进制', 10: '十进制', 16: '十六进制' };
    var explanation = '【题型】' + typeName + '\n';
    explanation += '【题目】' + question.question + '\n';
    explanation += '【你的答案】' + (userAnswer || '(未作答)') + '\n';
    explanation += '【正确答案】' + answer + '\n';
    explanation += '【解析】\n';
    var decValue = parseInt(sourceValue, fromBase);

    if (fromBase !== 10) {
      var digits = String(sourceValue).split('').reverse();
      var expansion = '';
      var sum = 0;
      for (var i = 0; i < digits.length; i++) {
        var d = parseInt(digits[i], fromBase);
        if (d > 0) expansion += d + '×' + fromBase + '^' + i + ' + ';
        sum += d * Math.pow(fromBase, i);
      }
      expansion = expansion.replace(/ \+ $/, '');
      explanation += '1. ' + baseName[fromBase] + '(' + sourceValue + ') → 十进制：\n';
      explanation += '   按位权展开：' + expansion + ' = ' + sum + '\n';
    }

    if (toBase !== 10) {
      explanation += '2. 十进制(' + decValue + ') → ' + baseName[toBase] + '：\n';
      explanation += '   除' + toBase + '取余法，逆序排列余数：\n';
      var n2 = decValue;
      var remainders = [];
      if (n2 === 0) remainders.push(0);
      else while (n2 > 0) { remainders.push(n2 % toBase); n2 = Math.floor(n2 / toBase); }
      var remStr = remainders.reverse().map(function(r) {
        if (toBase === 16 && r >= 10) return String.fromCharCode(55 + r);
        return r;
      }).join('');
      explanation += '   余数序列（逆序）：' + remStr + '\n';
      if (question.padLength > 0) explanation += '   要求' + question.padLength + '位，不足补前导零：' + answer + '\n';
    }

    explanation += '\n最终结果：' + sourceValue + '(' + baseName[fromBase] + ') = ' + answer + '(' + baseName[toBase] + ')';
    return explanation;
  }

  return {
    QUESTION_TYPES: QUESTION_TYPES,
    generatePaper: generatePaper,
    generateQuestion: generateQuestion,
    checkAnswer: checkAnswer,
    generateExplanation: generateExplanation,
    decToBase: decToBase,
    randomInt: randomInt
  };
})();
