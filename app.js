/**
 * CryptoSafe - app.js
 * 应用主入口：导航、初始化、事件绑定
 */

/* ================================================================
   标签页导航
   ================================================================ */
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;

    // 切换按钮状态
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // 切换面板
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById('tab-' + target);
    if (panel) panel.classList.add('active');

    // 进入 KMS 时刷新列表
    if (target === 'keymgr') kmsRender();
  });
});

/* ================================================================
   点击遮罩关闭弹窗
   ================================================================ */
document.getElementById('kms-modal').addEventListener('click', function(e) {
  if (e.target === this) kmsCloseModal();
});
document.getElementById('kms-detail-modal').addEventListener('click', function(e) {
  if (e.target === this) kmsCloseDetail();
});

/* ================================================================
   哈希实时计算（输入时触发）
   ================================================================ */
document.getElementById('hash-input').addEventListener('input', () => {
  const val = document.getElementById('hash-input').value;
  if (!val) {
    ['hash-md5','hash-sha1','hash-sha256','hash-sha512','hash-sm3'].forEach(id => {
      document.getElementById(id).textContent = '—';
    });
    return;
  }
  // 防抖
  clearTimeout(window._hashTimer);
  window._hashTimer = setTimeout(() => computeAllHash(), 300);
});

/* ================================================================
   Enter 快捷键触发计算
   ================================================================ */
document.getElementById('aes-plain').addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter') aesEncrypt();
});
document.getElementById('hmac-msg').addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter') computeHMAC();
});

/* ================================================================
   初始化
   ================================================================ */
window.addEventListener('DOMContentLoaded', () => {
  // 等待外部库加载完毕后初始化 KMS
  const waitForLibs = setInterval(() => {
    if (typeof smCrypto !== 'undefined' && typeof forge !== 'undefined' && typeof CryptoJS !== 'undefined') {
      clearInterval(waitForLibs);
      kmsLoad();
      kmsInitDemo();
      kmsRender();
      console.log('[CryptoSafe] 所有密码学库加载完成，系统就绪');
    }
  }, 100);

  // 超时提示
  setTimeout(() => {
    clearInterval(waitForLibs);
    if (typeof smCrypto === 'undefined' || typeof forge === 'undefined') {
      showToast('⚠️ 部分库加载超时，国密功能可能受限（请检查网络）', 5000);
    }
  }, 8000);
});
