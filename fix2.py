with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old = """(function() {
  'use strict';"""

new = """(function() {
  'use strict';
  // 硬编码云端配置
  if (window.Cloud) {
    Cloud.setConfig({ url: 'https://uazwtblpwayqlpczczai.supabase.co', anonKey: 'sb_publishable_nx-6oXW-Dn6WcfQ-41-tWA_Utj6hMCs' });
  }"""

content = content.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
