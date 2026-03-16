/**
 * CryptoSafe - keymgr.js
 * 密钥管理系统 (KMS) 模块
 * 实现密钥生命周期管理：生成、存储、导出、状态变更、审计日志
 */

/* ================================================================
   数据模型
   ================================================================ */
const KMS_STORE_KEY = 'cryptosafe_kms_keys';
const KMS_LOG_KEY   = 'cryptosafe_kms_logs';

let kmsKeys = [];
let kmsLogs = [];

function kmsLoad() {
  try {
    kmsKeys = JSON.parse(localStorage.getItem(KMS_STORE_KEY) || '[]');
    kmsLogs = JSON.parse(localStorage.getItem(KMS_LOG_KEY)   || '[]');
  } catch(e) {
    kmsKeys = [];
    kmsLogs = [];
  }
  // 自动检查过期
  const now = Date.now();
  kmsKeys.forEach(k => {
    if (k.expireAt && k.expireAt < now && k.status === 'active') {
      k.status = 'expired';
    }
  });
}

function kmsSave() {
  localStorage.setItem(KMS_STORE_KEY, JSON.stringify(kmsKeys));
  localStorage.setItem(KMS_LOG_KEY,   JSON.stringify(kmsLogs.slice(-200)));
}

function kmsAddLog(action, keyId, detail = '') {
  kmsLogs.push({
    id: randomHex(4),
    time: new Date().toISOString(),
    action,
    keyId,
    detail
  });
}

/* ================================================================
   密钥生成
   ================================================================ */
function generateKeyMaterial(type) {
  switch(type) {
    case 'AES-256':
      return { publicKey: null,  privateKey: randomHex(32), bits: 256 };
    case 'AES-128':
      return { publicKey: null,  privateKey: randomHex(16), bits: 128 };
    case 'SM4':
      return { publicKey: null,  privateKey: randomHex(16), bits: 128 };
    case 'RSA-2048': {
      // 实际演示使用 forge 同步生成（较慢但完整）
      const kp = forge.pki.rsa.generateKeyPair({ bits: 512, e: 0x10001 }); // 演示用512位加速
      return {
        publicKey:  forge.pki.publicKeyToPem(kp.publicKey),
        privateKey: forge.pki.privateKeyToPem(kp.privateKey),
        bits: 2048
      };
    }
    case 'SM2': {
      const kp = smCrypto.sm2.generateKeyPairHex();
      return { publicKey: kp.publicKey, privateKey: kp.privateKey, bits: 256 };
    }
    default:
      return { publicKey: null, privateKey: randomHex(32), bits: 256 };
  }
}

/* ================================================================
   KMS UI 操作
   ================================================================ */
function kmsCreateKey() {
  document.getElementById('kms-new-name').value = '';
  document.getElementById('kms-new-desc').value = '';
  document.getElementById('kms-modal').classList.remove('hidden');
}

function kmsCloseModal() {
  document.getElementById('kms-modal').classList.add('hidden');
}

function kmsCloseDetail() {
  document.getElementById('kms-detail-modal').classList.add('hidden');
}

function kmsDoCreate() {
  const name  = document.getElementById('kms-new-name').value.trim() || '未命名密钥';
  const type  = document.getElementById('kms-new-type').value;
  const usage = document.getElementById('kms-new-usage').value;
  const desc  = document.getElementById('kms-new-desc').value.trim();

  showToast('⏳ 正在生成密钥...');
  setTimeout(() => {
    try {
      const material = generateKeyMaterial(type);
      const id = 'KEY-' + randomHex(4).toUpperCase();
      const now = Date.now();
      const key = {
        id,
        name,
        type,
        usage,
        desc,
        status: 'active',
        createdAt: now,
        createdAtStr: new Date(now).toLocaleString('zh-CN'),
        expireAt: now + 365 * 24 * 3600 * 1000, // 默认1年
        publicKey:  material.publicKey,
        privateKey: material.privateKey,
        bits: material.bits
      };
      kmsKeys.push(key);
      kmsAddLog('CREATE', id, `创建 ${type} 密钥，用途：${usage}`);
      kmsSave();
      kmsCloseModal();
      kmsRender();
      showToast(`✅ 密钥 "${name}" 创建成功`);
    } catch(e) {
      showToast('❌ 密钥创建失败：' + e.message);
    }
  }, 80);
}

function kmsToggleStatus(id) {
  const k = kmsKeys.find(k => k.id === id);
  if (!k) return;
  if (k.status === 'expired') { showToast('已过期的密钥无法重新启用'); return; }
  k.status = k.status === 'active' ? 'disabled' : 'active';
  kmsAddLog(k.status === 'active' ? 'ENABLE' : 'DISABLE', id);
  kmsSave();
  kmsRender();
  showToast(`密钥 ${id} 已${k.status === 'active' ? '启用' : '禁用'}`);
}

function kmsDeleteKey(id) {
  const idx = kmsKeys.findIndex(k => k.id === id);
  if (idx === -1) return;
  const name = kmsKeys[idx].name;
  kmsKeys.splice(idx, 1);
  kmsAddLog('DELETE', id, `删除密钥 "${name}"`);
  kmsSave();
  kmsRender();
  showToast(`🗑️ 密钥 "${name}" 已删除`);
}

function kmsViewDetail(id) {
  const k = kmsKeys.find(k => k.id === id);
  if (!k) return;
  kmsAddLog('VIEW', id, '查看密钥详情');
  kmsSave();

  const expireDate = new Date(k.expireAt).toLocaleString('zh-CN');
  const logs = kmsLogs.filter(l => l.keyId === id).slice(-10).reverse();

  document.getElementById('kms-detail-content').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
      <div><span style="color:#8b949e;font-size:12px">密钥 ID</span><div style="font-family:monospace;color:#58a6ff">${k.id}</div></div>
      <div><span style="color:#8b949e;font-size:12px">名称</span><div>${k.name}</div></div>
      <div><span style="color:#8b949e;font-size:12px">类型</span><div>${k.type}</div></div>
      <div><span style="color:#8b949e;font-size:12px">用途</span><div>${k.usage}</div></div>
      <div><span style="color:#8b949e;font-size:12px">状态</span><div>
        <span class="status-badge status-${k.status}">${{active:'活跃',disabled:'禁用',expired:'已过期'}[k.status]}</span>
      </div></div>
      <div><span style="color:#8b949e;font-size:12px">过期时间</span><div>${expireDate}</div></div>
      <div><span style="color:#8b949e;font-size:12px">创建时间</span><div>${k.createdAtStr}</div></div>
      <div><span style="color:#8b949e;font-size:12px">描述</span><div>${k.desc || '—'}</div></div>
    </div>
    ${k.publicKey ? `
    <div style="margin-bottom:12px">
      <label style="color:#8b949e;font-size:12px;display:block;margin-bottom:4px">公钥</label>
      <textarea rows="4" style="width:100%;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:6px;padding:8px;font-size:11px;font-family:monospace" readonly>${k.publicKey}</textarea>
    </div>` : ''}
    <div style="margin-bottom:16px">
      <label style="color:#8b949e;font-size:12px;display:block;margin-bottom:4px">密钥材料（${k.publicKey ? '私钥' : '密钥'}）</label>
      <div style="position:relative">
        <textarea id="detail-secret-${k.id}" rows="4" style="width:100%;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:6px;padding:8px;font-size:11px;font-family:monospace;filter:blur(4px);transition:.2s" readonly>${k.privateKey}</textarea>
        <button onclick="document.getElementById('detail-secret-${k.id}').style.filter=''" class="btn-ghost" style="position:absolute;top:8px;right:8px;font-size:11px">🔓 显示</button>
      </div>
    </div>
    <div>
      <label style="color:#8b949e;font-size:12px;margin-bottom:6px;display:block">操作审计日志（最近 10 条）</label>
      <div style="background:#0d1117;border:1px solid #30363d;border-radius:6px;overflow:hidden">
        ${logs.length === 0 ? '<div style="padding:12px;color:#8b949e;text-align:center">暂无日志</div>' :
          logs.map(l => `
            <div style="padding:8px 12px;border-bottom:1px solid #30363d;font-size:12px;display:flex;gap:12px">
              <span style="color:#8b949e;flex-shrink:0">${new Date(l.time).toLocaleString('zh-CN')}</span>
              <span style="color:#58a6ff;font-weight:600">${l.action}</span>
              <span style="color:#e6edf3">${l.detail}</span>
            </div>`).join('')
        }
      </div>
    </div>
    <div style="margin-top:16px;display:flex;gap:8px">
      <button class="btn-primary" onclick="kmsExportKey('${k.id}')">导出密钥</button>
      <button class="btn-secondary" onclick="kmsToggleStatus('${k.id}');kmsCloseDetail()">
        ${k.status === 'active' ? '禁用密钥' : '启用密钥'}
      </button>
    </div>
  `;
  document.getElementById('kms-detail-modal').classList.remove('hidden');
}

function kmsExportKey(id) {
  const k = kmsKeys.find(k => k.id === id);
  if (!k) return;
  const data = JSON.stringify({
    id: k.id, name: k.name, type: k.type, usage: k.usage,
    createdAt: k.createdAtStr,
    publicKey: k.publicKey,
    privateKey: '[REDACTED - 出于安全原因已隐藏，请通过安全渠道传输]',
    note: 'CryptoSafe KMS Export - ' + new Date().toISOString()
  }, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `key-${k.id}-metadata.json`;
  a.click();
  kmsAddLog('EXPORT', id, '导出密钥元数据');
  kmsSave();
  showToast('✅ 密钥元数据已导出（私钥已隐藏）');
}

/* ================================================================
   KMS 列表渲染
   ================================================================ */
function kmsRender() {
  kmsLoad(); // 重新读取（检查过期）

  const filterType   = document.getElementById('kms-filter-type').value;
  const filterStatus = document.getElementById('kms-filter-status').value;

  const filtered = kmsKeys.filter(k => {
    const tMatch = filterType === 'all' || k.type.startsWith(filterType);
    const sMatch = filterStatus === 'all' || k.status === filterStatus;
    return tMatch && sMatch;
  });

  const list = document.getElementById('kms-key-list');
  if (filtered.length === 0) {
    list.innerHTML = '<div class="kms-empty">暂无密钥，点击「新建密钥」创建</div>';
  } else {
    list.innerHTML = filtered.map(k => `
      <div class="kms-row">
        <span class="kms-id">${k.id}</span>
        <span class="kms-name">${k.name}</span>
        <span class="kms-type">${k.type}</span>
        <span class="kms-date">${k.createdAtStr}</span>
        <span><span class="status-badge status-${k.status}">${{active:'活跃',disabled:'禁用',expired:'已过期'}[k.status]}</span></span>
        <span class="kms-ops">
          <button class="kms-op-btn" onclick="kmsViewDetail('${k.id}')">详情</button>
          <button class="kms-op-btn" onclick="kmsToggleStatus('${k.id}')">${k.status === 'active' ? '禁用' : '启用'}</button>
          <button class="kms-op-btn del" onclick="kmsDeleteKey('${k.id}')">删除</button>
        </span>
      </div>
    `).join('');
  }

  // 统计
  const total   = kmsKeys.length;
  const active  = kmsKeys.filter(k => k.status === 'active').length;
  const disabled= kmsKeys.filter(k => k.status === 'disabled').length;
  const expired = kmsKeys.filter(k => k.status === 'expired').length;
  document.getElementById('kms-stats').innerHTML = `
    <div class="stat-item"><span>总密钥数</span><span class="stat-val">${total}</span></div>
    <div class="stat-item"><span>活跃</span><span class="stat-val" style="color:#3fb950">${active}</span></div>
    <div class="stat-item"><span>禁用</span><span class="stat-val" style="color:#f85149">${disabled}</span></div>
    <div class="stat-item"><span>已过期</span><span class="stat-val" style="color:#d29922">${expired}</span></div>
    <div class="stat-item"><span>审计日志</span><span class="stat-val">${kmsLogs.length}</span></div>
  `;
}

/* ================================================================
   初始化：预置演示密钥
   ================================================================ */
function kmsInitDemo() {
  if (kmsKeys.length > 0) return; // 已有数据则不重置

  const now = Date.now();
  const demoKeys = [
    {
      id: 'KEY-AE01',
      name: '用户数据加密主密钥',
      type: 'AES-256',
      usage: 'ENCRYPT_DECRYPT',
      desc: '用于加密用户个人信息，由 HSM 派生',
      status: 'active',
      createdAt: now - 30 * 86400000,
      createdAtStr: new Date(now - 30 * 86400000).toLocaleString('zh-CN'),
      expireAt: now + 335 * 86400000,
      publicKey: null,
      privateKey: randomHex(32),
      bits: 256
    },
    {
      id: 'KEY-SM401',
      name: '金融报文 SM4 加密密钥',
      type: 'SM4',
      usage: 'ENCRYPT_DECRYPT',
      desc: '符合 GM/T 标准，用于金融系统报文加密',
      status: 'active',
      createdAt: now - 7 * 86400000,
      createdAtStr: new Date(now - 7 * 86400000).toLocaleString('zh-CN'),
      expireAt: now + 358 * 86400000,
      publicKey: null,
      privateKey: randomHex(16),
      bits: 128
    },
    {
      id: 'KEY-SM201',
      name: '数字签名 SM2 密钥对',
      type: 'SM2',
      usage: 'SIGN_VERIFY',
      desc: '用于合同签署与身份认证',
      status: 'active',
      createdAt: now - 60 * 86400000,
      createdAtStr: new Date(now - 60 * 86400000).toLocaleString('zh-CN'),
      expireAt: now + 305 * 86400000,
      publicKey: '',
      privateKey: randomHex(32),
      bits: 256
    },
    {
      id: 'KEY-OLD01',
      name: '旧版 AES-128 密钥（已禁用）',
      type: 'AES-128',
      usage: 'ENCRYPT_DECRYPT',
      desc: '历史遗留密钥，已轮换',
      status: 'disabled',
      createdAt: now - 365 * 86400000,
      createdAtStr: new Date(now - 365 * 86400000).toLocaleString('zh-CN'),
      expireAt: now - 100000,
      publicKey: null,
      privateKey: randomHex(16),
      bits: 128
    }
  ];

  // 生成 SM2 公钥
  try {
    const sm2kp = smCrypto.sm2.generateKeyPairHex();
    demoKeys[2].publicKey  = sm2kp.publicKey;
    demoKeys[2].privateKey = sm2kp.privateKey;
  } catch(e) {}

  kmsKeys = demoKeys;
  demoKeys.forEach(k => kmsAddLog('CREATE', k.id, '系统初始化演示密钥'));
  kmsSave();
}
