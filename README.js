/**
 * CryptoSafe - README
 * 轻量级密码安全服务平台
 *
 * 功能模块：
 *   1. 对称加密   - AES-128/256（CBC/ECB/CTR）
 *   2. 非对称加密 - RSA-2048（OAEP）
 *   3. 国密算法   - SM2 / SM4 / SM3
 *   4. 数字签名   - RSA-SHA256 / SM2-SM3
 *   5. 密钥管理   - KMS 密钥全生命周期
 *   6. 哈希摘要   - MD5 / SHA-1 / SHA-256 / SHA-512 / SM3 / HMAC
 *
 * 使用方式：
 *   直接用浏览器打开 index.html 即可（无需服务器）
 *   推荐使用 Chrome / Edge 最新版
 *
 * 依赖库（CDN）：
 *   - CryptoJS 4.2.0   (AES / SHA / HMAC)
 *   - node-forge 1.3.1 (RSA / PEM)
 *   - sm-crypto 0.3.13 (SM2 / SM3 / SM4)
 *
 * 项目结构：
 *   index.html  - 主界面
 *   style.css   - 全局样式（深色主题）
 *   crypto.js   - 密码算法核心实现
 *   keymgr.js   - 密钥管理系统
 *   app.js      - 应用入口与导航
 */
