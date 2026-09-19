/**
 * 防作弊模块：设备指纹 + 切屏检测
 */
window.AntiCheat = (function() {

  // ========== 设备指纹 ==========
  function generateFingerprint() {
    var components = [];

    // User-Agent
    components.push(navigator.userAgent);

    // 屏幕分辨率
    components.push(screen.width + 'x' + screen.height + 'x' + screen.colorDepth);

    // 时区
    components.push(Intl.DateTimeFormat().resolvedOptions().timeZone);

    // 语言
    components.push(navigator.language);

    // 平台
    components.push(navigator.platform);

    // Canvas指纹
    try {
      var canvas = document.createElement('canvas');
      canvas.width = 200;
      canvas.height = 50;
      var ctx = canvas.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.fillText('AntiCheat Fingerprint', 2, 15);
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.fillText('AntiCheat Fingerprint', 4, 17);
      components.push(canvas.toDataURL());
    } catch (e) {
      components.push('canvas-error');
    }

    // WebGL指纹
    try {
      var gl = document.createElement('canvas').getContext('webgl');
      var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
      if (debugInfo) {
        components.push(gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL));
        components.push(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL));
      }
    } catch (e) {}

    // 字体列表（粗略）
    var fonts = [];
    var testFonts = ['Arial', 'Helvetica', 'Times', 'Courier', 'Monaco', 'Menlo', 'Verdana', 'Georgia'];
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    ctx.font = '72px monospace';
    var baseWidth = ctx.measureText('mmmmmmmmm').width;
    testFonts.forEach(function(f) {
      ctx.font = '72px ' + f;
      if (ctx.measureText('mmmmmmmmm').width !== baseWidth) fonts.push(f);
    });
    components.push(fonts.join(','));

    // 哈希（简单的字符串哈希）
    var str = components.join('|');
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
      var char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }

    // 转成32位十六进制
    var hex = (hash >>> 0).toString(16);
    // 补全为8位
    while (hex.length < 8) hex = '0' + hex;

    return 'fp_' + hex;
  }

  function getDeviceInfo() {
    var ua = navigator.userAgent;
    var device = '未知设备';

    // 简单判断手机型号
    if (/iPhone/i.test(ua)) {
      var match = ua.match(/iPhone\s*(\d+),(\d+)/);
      device = match ? 'iPhone ' + match[1] + ',' + match[2] : 'iPhone';
    } else if (/iPad/i.test(ua)) {
      device = 'iPad';
    } else if (/Android/i.test(ua)) {
      var androidMatch = ua.match(/Android\s*(\d+\.\d+)/);
      var modelMatch = ua.match(/;\s*([^;)]+?)\s+Build\//);
      var androidVer = androidMatch ? 'Android ' + androidMatch[1] : 'Android';
      var model = modelMatch ? modelMatch[1].trim() : '';
      device = model ? (model + ' (' + androidVer + ')') : androidVer;
    } else if (/Windows/i.test(ua)) {
      device = 'Windows PC';
    } else if (/Macintosh/i.test(ua)) {
      device = 'Mac';
    }

    return {
      fingerprint: generateFingerprint(),
      deviceModel: device,
      screen: screen.width + 'x' + screen.height,
      userAgent: ua.substring(0, 100)
    };
  }

  // ========== 切屏检测 ==========
  var visibilityCallbacks = [];
  var blurCount = 0;
  var isMonitoring = false;
  var onWarning = null;

  function startMonitoring(onWarn) {
    if (isMonitoring) return;
    isMonitoring = true;
    blurCount = 0;
    onWarning = onWarn;

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);
  }

  function stopMonitoring() {
    isMonitoring = false;
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    window.removeEventListener('blur', handleBlur);
  }

  function handleVisibilityChange() {
    if (document.hidden) {
      // 页面隐藏（切屏/切到其他App）
      blurCount++;
    } else {
      // 页面重新可见
      if (blurCount > 0 && onWarning) {
        onWarning(blurCount);
      }
    }
  }

  function handleBlur() {
    // 窗口失焦（点击地址栏、切换标签页等）
    blurCount++;
  }

  function getBlurCount() {
    return blurCount;
  }

  return {
    getDeviceInfo: getDeviceInfo,
    generateFingerprint: generateFingerprint,
    startMonitoring: startMonitoring,
    stopMonitoring: stopMonitoring,
    getBlurCount: getBlurCount
  };
})();
