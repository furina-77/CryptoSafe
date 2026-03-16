/**
 * CryptoSafe - crypto.js
 * 密码算法核心实现模块
 * 依赖：CryptoJS 4.x、node-forge 1.x、sm-crypto 0.3.x
 */

/* ================================================================
   工具函数
   ================================================================ */
function showResult(id, text, type = 'ok') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  el.className = 'result-box show' + (type === 'error' ? ' error' : type === 'warning' ? ' warning' : '');
}

function showToast(msg, duration = 2500) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.remove('hidden');
  t.classList.add('show');
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.classList.add('hidden'), 300); }, duration);
}

function randomHex(bytes) {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
}

function hexToBase64(hex) {
  const bytes = [];
  for (let i = 0; i < hex.length; i += 2) bytes.push(parseInt(hex.substr(i, 2), 16));
  return btoa(String.fromCharCode(...bytes));
}

function base64ToHex(b64) {
  const bin = atob(b64);
  return Array.from(bin).map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('');
}

function normalizeKey(keyStr, bits) {
  // 支持 Hex 和 Base64 输入，统一转成 CryptoJS WordArray
  let hex = '';
  if (/^[0-9a-fA-F]+$/.test(keyStr.trim())) {
    hex = keyStr.trim();
  } else {
    try { hex = base64ToHex(keyStr.trim()); } catch(e) { hex = ''; }
  }
  const needed = bits / 4; // hex chars
  if (hex.length < needed) hex = hex.padEnd(needed, '0');
  else if (hex.length > needed) hex = hex.substring(0, needed);
  return CryptoJS.enc.Hex.parse(hex);
}

function normalizeIV(ivStr) {
  let hex = '';
  if (/^[0-9a-fA-F]+$/.test(ivStr.trim())) {
    hex = ivStr.trim();
  } else {
    try { hex = base64ToHex(ivStr.trim()); } catch(e) { hex = ''; }
  }
  if (hex.length < 32) hex = hex.padEnd(32, '0');
  else if (hex.length > 32) hex = hex.substring(0, 32);
  return CryptoJS.enc.Hex.parse(hex);
}

/* ================================================================
   AES 模块
   ================================================================ */
function aesGenKey() {
  const len = parseInt(document.getElementById('aes-keylen').value || '256');
  const key = randomHex(len / 8);
  document.getElementById('aes-key').value = key;
  showToast('✅ 已生成 AES-' + len + ' 密钥');
}

function aesGenIV() {
  document.getElementById('aes-iv').value = randomHex(16);
  showToast('✅ 已生成随机 IV');
}

function aesEncrypt() {
  try {
    const plain = document.getElementById('aes-plain').value;
    if (!plain) { showResult('aes-cipher-result', '请输入明文', 'error'); return; }

    let keyStr = document.getElementById('aes-key').value.trim();
    const len = parseInt(document.getElementById('aes-keylen').value || '256');
    if (!keyStr) { keyStr = randomHex(len / 8); document.getElementById('aes-key').value = keyStr; }

    const mode = document.getElementById('aes-mode').value;
    let ivStr = document.getElementById('aes-iv').value.trim();
    if (!ivStr && mode !== 'ECB') { ivStr = randomHex(16); document.getElementById('aes-iv').value = ivStr; }

    const keyWA = normalizeKey(keyStr, len);
    const cfg = { mode: CryptoJS.mode[mode], padding: CryptoJS.pad.Pkcs7 };
    if (mode !== 'ECB') cfg.iv = normalizeIV(ivStr);

    const encrypted = CryptoJS.AES.encrypt(plain, keyWA, cfg);
    const result = encrypted.ciphertext.toString(CryptoJS.enc.Base64);
    showResult('aes-cipher-result',
      `🔒 加密成功\n\n密文 (Base64):\n${result}\n\n密钥 (Hex):\n${keyStr}\n${mode !== 'ECB' ? `\nIV (Hex):\n${ivStr}` : ''}`, 'ok');
    // 自动填充解密区
    document.getElementById('aes-cipher').value = result;
    document.getElementById('aes-dec-key').value = keyStr;
    document.getElementById('aes-dec-iv').value = ivStr;
    document.getElementById('aes-dec-mode').value = mode;
  } catch(e) {
    showResult('aes-cipher-result', '❌ 加密失败：' + e.message, 'error');
  }
}

function aesDecrypt() {
  try {
    const cipherB64 = document.getElementById('aes-cipher').value.trim();
    if (!cipherB64) { showResult('aes-plain-result', '请输入密文', 'error'); return; }

    const keyStr = document.getElementById('aes-dec-key').value.trim();
    if (!keyStr) { showResult('aes-plain-result', '请输入密钥', 'error'); return; }

    const mode = document.getElementById('aes-dec-mode').value;
    const ivStr = document.getElementById('aes-dec-iv').value.trim();

    // 自动检测密钥长度
    let keyLen = 256;
    if (/^[0-9a-fA-F]+$/.test(keyStr) && keyStr.length === 32) keyLen = 128;
    else if (/^[0-9a-fA-F]+$/.test(keyStr) && keyStr.length === 64) keyLen = 256;

    const keyWA = normalizeKey(keyStr, keyLen);
    const cipherWA = CryptoJS.lib.CipherParams.create({ ciphertext: CryptoJS.enc.Base64.parse(cipherB64) });
    const cfg = { mode: CryptoJS.mode[mode], padding: CryptoJS.pad.Pkcs7 };
    if (mode !== 'ECB' && ivStr) cfg.iv = normalizeIV(ivStr);

    const decrypted = CryptoJS.AES.decrypt(cipherWA, keyWA, cfg);
    const plain = decrypted.toString(CryptoJS.enc.Utf8);
    if (!plain) throw new Error('解密结果为空，请检查密钥/IV/模式是否匹配');
    showResult('aes-plain-result', '🔓 解密成功\n\n明文：\n' + plain, 'ok');
  } catch(e) {
    showResult('aes-plain-result', '❌ 解密失败：' + e.message, 'error');
  }
}

/* ================================================================
   RSA 模块（基于 node-forge）
   ================================================================ */
let _rsaKeyPair = null;

function rsaGenKey() {
  try {
    const len = parseInt(document.getElementById('rsa-keylen').value || '2048');
    showToast('⏳ 正在生成 RSA-' + len + ' 密钥对，请稍候...');
    setTimeout(() => {
      try {
        const kp = forge.pki.rsa.generateKeyPair({ bits: len, e: 0x10001 });
        _rsaKeyPair = kp;
        const pubPem  = forge.pki.publicKeyToPem(kp.publicKey);
        const priPem  = forge.pki.privateKeyToPem(kp.privateKey);
        document.getElementById('rsa-pubkey').value = pubPem;
        document.getElementById('rsa-prikey').value = priPem;
        document.getElementById('rsa-enc-pub').value  = pubPem;
        document.getElementById('sig-prikey').value   = priPem;
        document.getElementById('verify-pubkey').value = pubPem;
        document.getElementById('rsa-dec-pri').value  = priPem;
        showToast('✅ RSA-' + len + ' 密钥对生成成功');
      } catch(e) { showToast('❌ 密钥生成失败：' + e.message); }
    }, 50);
  } catch(e) { showToast('❌ ' + e.message); }
}

function rsaEncrypt() {
  try {
    const plain = document.getElementById('rsa-plain').value;
    if (!plain) { showResult('rsa-cipher-result', '请输入明文', 'error'); return; }
    const pubPem = document.getElementById('rsa-enc-pub').value.trim();
    if (!pubPem) { showResult('rsa-cipher-result', '请输入或生成公钥', 'error'); return; }

    const pub = forge.pki.publicKeyFromPem(pubPem);
    const enc = pub.encrypt(forge.util.encodeUtf8(plain), 'RSA-OAEP', { md: forge.md.sha256.create() });
    const b64 = forge.util.encode64(enc);
    showResult('rsa-cipher-result', '🔒 RSA-OAEP 加密成功\n\n密文 (Base64):\n' + b64, 'ok');
    document.getElementById('rsa-cipher').value = b64;
  } catch(e) {
    showResult('rsa-cipher-result', '❌ 加密失败：' + e.message, 'error');
  }
}

function rsaDecrypt() {
  try {
    const cipherB64 = document.getElementById('rsa-cipher').value.trim();
    if (!cipherB64) { showResult('rsa-plain-result', '请输入密文', 'error'); return; }
    const priPem = document.getElementById('rsa-dec-pri').value.trim();
    if (!priPem) { showResult('rsa-plain-result', '请输入私钥', 'error'); return; }

    const pri = forge.pki.privateKeyFromPem(priPem);
    const dec = pri.decrypt(forge.util.decode64(cipherB64), 'RSA-OAEP', { md: forge.md.sha256.create() });
    showResult('rsa-plain-result', '🔓 RSA 解密成功\n\n明文：\n' + forge.util.decodeUtf8(dec), 'ok');
  } catch(e) {
    showResult('rsa-plain-result', '❌ 解密失败：' + e.message, 'error');
  }
}

/* ================================================================
   RSA 数字签名模块
   ================================================================ */
function rsaSign() {
  try {
    const msg = document.getElementById('sig-msg').value;
    if (!msg) { showResult('sig-result', '请输入消息', 'error'); return; }
    const priPem = document.getElementById('sig-prikey').value.trim();
    if (!priPem) { showResult('sig-result', '请输入私钥', 'error'); return; }

    const pri = forge.pki.privateKeyFromPem(priPem);
    const md  = forge.md.sha256.create();
    md.update(msg, 'utf8');
    const sig = pri.sign(md);
    const sigB64 = forge.util.encode64(sig);
    showResult('sig-result', '✍️ RSA-SHA256 签名成功\n\n签名 (Base64):\n' + sigB64, 'ok');
    document.getElementById('verify-sig').value = sigB64;
  } catch(e) {
    showResult('sig-result', '❌ 签名失败：' + e.message, 'error');
  }
}

function rsaVerify() {
  try {
    const msg    = document.getElementById('sig-msg').value;
    const sigB64 = document.getElementById('verify-sig').value.trim();
    const pubPem = document.getElementById('verify-pubkey').value.trim();
    if (!msg || !sigB64 || !pubPem) { showResult('verify-result', '请填写消息、签名和公钥', 'error'); return; }

    const pub = forge.pki.publicKeyFromPem(pubPem);
    const md  = forge.md.sha256.create();
    md.update(msg, 'utf8');
    const valid = pub.verify(md.digest().bytes(), forge.util.decode64(sigB64));
    if (valid) {
      showResult('verify-result', '✅ 签名验证通过！\n消息未被篡改，来源可信。', 'ok');
    } else {
      showResult('verify-result', '❌ 签名验证失败！\n消息可能已被篡改或签名不匹配。', 'error');
    }
  } catch(e) {
    showResult('verify-result', '❌ 验证失败：' + e.message, 'error');
  }
}

/* ================================================================
   SM4 模块
   ================================================================ */
const sm4 = smCrypto.sm4;

function sm4GenKey() {
  document.getElementById('sm4-key').value = randomHex(16);
  showToast('✅ 已生成 SM4 密钥');
}
function sm4GenIV() {
  document.getElementById('sm4-iv').value = randomHex(16);
  showToast('✅ 已生成随机 IV');
}

function sm4Encrypt() {
  try {
    const plain = document.getElementById('sm4-plain').value;
    if (!plain) { showResult('sm4-result', '请输入明文', 'error'); return; }
    let key = document.getElementById('sm4-key').value.trim();
    if (!key) { key = randomHex(16); document.getElementById('sm4-key').value = key; }
    const mode = document.getElementById('sm4-mode').value;
    let iv = document.getElementById('sm4-iv').value.trim();
    if (!iv && mode === 'CBC') { iv = randomHex(16); document.getElementById('sm4-iv').value = iv; }

    const opt = { mode: mode.toLowerCase(), padding: 'pkcs#7', output: 'array' };
    if (mode === 'CBC') opt.iv = iv;

    const cipherArr = sm4.encrypt(plain, key, opt);
    const cipherHex = Array.from(cipherArr).map(b => b.toString(16).padStart(2,'0')).join('');
    const cipherB64 = hexToBase64(cipherHex);

    showResult('sm4-result',
      `🔒 SM4-${mode} 加密成功\n\n密文 (Hex):\n${cipherHex}\n\n密文 (Base64):\n${cipherB64}\n\n密钥: ${key}${mode==='CBC'?'\n\nIV: '+iv:''}`, 'ok');
  } catch(e) {
    showResult('sm4-result', '❌ SM4 加密失败：' + e.message, 'error');
  }
}

function sm4Decrypt() {
  try {
    const cipherText = document.getElementById('sm4-plain').value.trim();
    if (!cipherText) { showResult('sm4-result', '请在上方输入框填入密文（Hex）', 'error'); return; }
    const key = document.getElementById('sm4-key').value.trim();
    if (!key) { showResult('sm4-result', '请输入密钥', 'error'); return; }
    const mode = document.getElementById('sm4-mode').value;
    const iv = document.getElementById('sm4-iv').value.trim();

    const opt = { mode: mode.toLowerCase(), padding: 'pkcs#7', output: 'utf8' };
    if (mode === 'CBC' && iv) opt.iv = iv;

    const plain = sm4.decrypt(cipherText, key, opt);
    showResult('sm4-result', '🔓 SM4 解密成功\n\n明文：\n' + plain, 'ok');
  } catch(e) {
    showResult('sm4-result', '❌ SM4 解密失败：' + e.message, 'error');
  }
}

/* ================================================================
   SM2 模块
   ================================================================ */
const sm2 = smCrypto.sm2;
let _sm2KeyPair = null;

function sm2GenKey() {
  const kp = sm2.generateKeyPairHex();
  _sm2KeyPair = kp;
  document.getElementById('sm2-pubkey').value = kp.publicKey;
  document.getElementById('sm2-prikey').value = kp.privateKey;
  document.getElementById('sm2-sig-pubkey').value = kp.publicKey;
  document.getElementById('sm2-sig-prikey').value = kp.privateKey;
  showToast('✅ SM2 密钥对生成成功');
}

function sm2SigGenKey() {
  const kp = sm2.generateKeyPairHex();
  _sm2KeyPair = kp;
  document.getElementById('sm2-sig-pubkey').value = kp.publicKey;
  document.getElementById('sm2-sig-prikey').value = kp.privateKey;
  showToast('✅ SM2 密钥对生成成功');
}

function sm2Encrypt() {
  try {
    const plain = document.getElementById('sm2-plain').value;
    if (!plain) { showResult('sm2-result', '请输入明文', 'error'); return; }
    const pubKey = document.getElementById('sm2-pubkey').value.trim();
    if (!pubKey) { showResult('sm2-result', '请先生成或输入 SM2 公钥', 'error'); return; }

    const enc = sm2.doEncrypt(plain, pubKey, 1); // cipherMode 1 = C1C3C2
    showResult('sm2-result', '🔒 SM2 加密成功 (C1C3C2)\n\n密文 (Hex):\n' + enc, 'ok');
  } catch(e) {
    showResult('sm2-result', '❌ SM2 加密失败：' + e.message, 'error');
  }
}

function sm2Decrypt() {
  try {
    const cipherHex = document.getElementById('sm2-plain').value.trim();
    if (!cipherHex) { showResult('sm2-result', '请在上方输入框填入密文（Hex）', 'error'); return; }
    const priKey = document.getElementById('sm2-prikey').value.trim();
    if (!priKey) { showResult('sm2-result', '请输入私钥', 'error'); return; }

    const plain = sm2.doDecrypt(cipherHex, priKey, 1);
    showResult('sm2-result', '🔓 SM2 解密成功\n\n明文：\n' + plain, 'ok');
  } catch(e) {
    showResult('sm2-result', '❌ SM2 解密失败：' + e.message, 'error');
  }
}

/* ================================================================
   SM3 哈希
   ================================================================ */
const sm3 = smCrypto.sm3;

function sm3Hash() {
  const input = document.getElementById('sm3-input').value;
  if (!input) { showResult('sm3-result', '请输入数据', 'error'); return; }
  try {
    const hash = sm3(input);
    showResult('sm3-result', 'SM3 哈希值:\n' + hash + '\n\n（256位 = 64位十六进制）', 'ok');
  } catch(e) {
    showResult('sm3-result', '❌ SM3 计算失败：' + e.message, 'error');
  }
}

/* ================================================================
   SM2 签名模块
   ================================================================ */
function sm2Sign() {
  try {
    const msg    = document.getElementById('sm2-sig-msg').value;
    const priKey = document.getElementById('sm2-sig-prikey').value.trim();
    const pubKey = document.getElementById('sm2-sig-pubkey').value.trim();
    if (!msg) { showResult('sm2-sig-result', '请输入消息', 'error'); return; }
    if (!priKey) { showResult('sm2-sig-result', '请输入或生成 SM2 私钥', 'error'); return; }

    const msgHex = Array.from(new TextEncoder().encode(msg))
      .map(b => b.toString(16).padStart(2, '0')).join('');
    const sig = sm2.doSignature(msgHex, priKey, { hash: true, der: true });
    showResult('sm2-sig-result', '✍️ SM2 签名成功\n\n签名 (DER/Hex):\n' + sig, 'ok');

    // 存入验签区（复用消息输入框查找）
    window._lastSm2Sig = sig;
  } catch(e) {
    showResult('sm2-sig-result', '❌ SM2 签名失败：' + e.message, 'error');
  }
}

function sm2Verify() {
  try {
    const msg    = document.getElementById('sm2-sig-msg').value;
    const pubKey = document.getElementById('sm2-sig-pubkey').value.trim();
    const sig    = window._lastSm2Sig || '';
    if (!msg || !pubKey || !sig) {
      showResult('sm2-sig-result', '请先完成签名，然后再验签', 'warning'); return;
    }
    const msgHex = Array.from(new TextEncoder().encode(msg))
      .map(b => b.toString(16).padStart(2, '0')).join('');
    const valid = sm2.doVerifySignature(msgHex, sig, pubKey, { hash: true, der: true });
    if (valid) {
      showResult('sm2-sig-result', '✅ SM2 签名验证通过！\n消息完整，来源可信。', 'ok');
    } else {
      showResult('sm2-sig-result', '❌ SM2 签名验证失败！', 'error');
    }
  } catch(e) {
    showResult('sm2-sig-result', '❌ SM2 验签失败：' + e.message, 'error');
  }
}

/* ================================================================
   哈希模块
   ================================================================ */
function wordArrayToHex(wa) {
  return wa.toString(CryptoJS.enc.Hex);
}

async function computeAllHash() {
  const input = document.getElementById('hash-input').value;
  if (!input) { showToast('请输入数据'); return; }

  document.getElementById('hash-md5').textContent    = wordArrayToHex(CryptoJS.MD5(input));
  document.getElementById('hash-sha1').textContent   = wordArrayToHex(CryptoJS.SHA1(input));
  document.getElementById('hash-sha256').textContent = wordArrayToHex(CryptoJS.SHA256(input));
  document.getElementById('hash-sha512').textContent = wordArrayToHex(CryptoJS.SHA512(input));
  document.getElementById('hash-sm3').textContent    = sm3(input);
  showToast('✅ 哈希计算完成');
}

async function hashFile() {
  const file = document.getElementById('hash-file').files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (e) => {
    const data = e.target.result;
    const wa = CryptoJS.lib.WordArray.create(data);
    document.getElementById('hash-md5').textContent    = wordArrayToHex(CryptoJS.MD5(wa));
    document.getElementById('hash-sha1').textContent   = wordArrayToHex(CryptoJS.SHA1(wa));
    document.getElementById('hash-sha256').textContent = wordArrayToHex(CryptoJS.SHA256(wa));
    document.getElementById('hash-sha512').textContent = wordArrayToHex(CryptoJS.SHA512(wa));
    showToast(`✅ 文件 "${file.name}" 哈希计算完成`);
  };
  reader.readAsArrayBuffer(file);
}

function copyHash(id) {
  const val = document.getElementById(id).textContent;
  if (val && val !== '—') {
    navigator.clipboard.writeText(val).then(() => showToast('已复制到剪贴板'));
  }
}

function hmacGenKey() {
  document.getElementById('hmac-key').value = randomHex(32);
}

async function computeHMAC() {
  const msg  = document.getElementById('hmac-msg').value;
  const key  = document.getElementById('hmac-key').value.trim();
  const algo = document.getElementById('hmac-algo').value;
  if (!msg) { showResult('hmac-result', '请输入消息', 'error'); return; }
  if (!key) { showResult('hmac-result', '请输入密钥', 'error'); return; }
  try {
    let hmac;
    if (algo === 'SHA-256') hmac = CryptoJS.HmacSHA256(msg, key);
    else if (algo === 'SHA-512') hmac = CryptoJS.HmacSHA512(msg, key);
    else hmac = CryptoJS.HmacSHA1(msg, key);
    showResult('hmac-result', `HMAC-${algo.replace('SHA-','')}:\n${wordArrayToHex(hmac)}\n\n(Base64): ${hmac.toString(CryptoJS.enc.Base64)}`, 'ok');
  } catch(e) {
    showResult('hmac-result', '❌ HMAC 计算失败：' + e.message, 'error');
  }
}

function showHashComparison() {
  const input = document.getElementById('collision-input').value;
  const tbody = document.getElementById('collision-table');
  if (!input) { tbody.innerHTML = ''; return; }
  const rows = [
    { algo: 'MD5',     hash: wordArrayToHex(CryptoJS.MD5(input)),    sec: 'broken', label: '已攻破' },
    { algo: 'SHA-1',   hash: wordArrayToHex(CryptoJS.SHA1(input)),   sec: 'weak',   label: '不推荐' },
    { algo: 'SHA-256', hash: wordArrayToHex(CryptoJS.SHA256(input)), sec: 'ok',     label: '安全' },
    { algo: 'SHA-512', hash: wordArrayToHex(CryptoJS.SHA512(input)), sec: 'ok',     label: '安全' },
    { algo: 'SM3',     hash: sm3(input),                              sec: 'ok',     label: '安全' },
  ];
  tbody.innerHTML = rows.map(r =>
    `<div class="col-row">
      <span class="col-algo">${r.algo}</span>
      <span class="col-hash">${r.hash}</span>
      <span class="col-security sec-${r.sec}">${r.label}</span>
    </div>`
  ).join('');
}
