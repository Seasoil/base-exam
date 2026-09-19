with open('css/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

old = """.sheet-item.answered { background: var(--success-light); color: #059669; }
.sheet-item.unanswered { background: var(--gray-100); color: var(--gray-500); }"""

new = """.sheet-item.answered { background: var(--success-light); color: #059669; }
.sheet-item.wrong { background: #fee2e2; color: #dc2626; }
.sheet-item.unanswered { background: var(--gray-100); color: var(--gray-500); }

/* 解析框 */
.analysis-box {
  margin-top: 16px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid;
}
.analysis-box.correct {
  background: #f0fdf4;
  border-color: #bbf7d0;
}
.analysis-box.wrong {
  background: #fef2f2;
  border-color: #fecaca;
}
.analysis-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}
.analysis-box.correct .analysis-title {
  color: #16a34a;
}
.analysis-box.wrong .analysis-title {
  color: #dc2626;
}
.analysis-item {
  font-size: 14px;
  margin-bottom: 8px;
  color: var(--gray-700);
}
.your-answer {
  font-weight: 600;
  color: #dc2626;
}
.right-answer {
  font-weight: 600;
  color: #16a34a;
}
.analysis-explain {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 13px;
  color: var(--gray-600);
  line-height: 1.6;
}"""

content = content.replace(old, new)

with open('css/style.css', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
