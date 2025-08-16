# NCM解密算法修复总结

## 问题描述
用户报告NCM文件转换失败，转换后的音频文件无法播放，错误信息显示：
- `Decoding failed. ffmpeg returned error code: 69`
- `Header missing`
- `Invalid data found when processing input`
- 下载的文件在其他音乐软件中也无法播放

## 根本原因分析
通过分析发现，问题出在NCM解密算法上：
1. **主解密函数**：使用了不完整的密钥提取方法
2. **备用解密函数**：使用了过于简化的XOR解密，而不是正确的RC4算法
3. **文件头验证**：解密后的文件头`97bef1f9c084ebd15b7e356759afc4cb`不是有效的音频格式

## 修复方案

### 1. 重写备用解密算法
**文件**: `apps/tools/legacy_views.py`
**函数**: `decrypt_ncm_file_fallback`

**主要改进**:
- ✅ 使用正确的AES-128-ECB解密RC4密钥
- ✅ 实现完整的RC4算法（KSA + PRGA）
- ✅ 添加详细的文件头验证
- ✅ 改进错误处理和日志记录

```python
# 使用AES解密RC4密钥
core_key = b'hzHRAmso5kInbaxW'
cipher = AES.new(core_key, AES.MODE_ECB)
decrypted_key = cipher.decrypt(key_data)

# 实现完整的RC4算法
S = list(range(256))
j = 0

# 密钥调度算法 (KSA)
for i in range(256):
    j = (j + S[i] + decrypted_key[i % len(decrypted_key)]) % 256
    S[i], S[j] = S[j], S[i]

# 伪随机生成算法 (PRGA)
i = j = 0
for byte in chunk:
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    S[i], S[j] = S[j], S[i]
    k = S[(S[i] + S[j]) % 256]
    decrypted.append(byte ^ k)
```

### 2. 改进主解密函数
**文件**: `apps/tools/legacy_views.py`
**函数**: `decrypt_ncm_file`

**主要改进**:
- ✅ 添加详细的密钥数据调试信息
- ✅ 改进密钥提取方法
- ✅ 自动检测无效文件头并切换到备用解密
- ✅ 增强文件格式验证

```python
# 添加调试信息
print(f"解密后的密钥数据长度: {len(key_data)}")
print(f"解密后的密钥数据前32字节: {key_data[:32].hex()}")

# 自动切换到备用解密
if not valid_audio_header:
    print("❌ 无法识别音频格式，文件头: " + header.hex())
    print("🔄 尝试使用修复后的备用解密算法...")
    return decrypt_ncm_file_fallback(ncm_path)
```

### 3. 安装必要的依赖
```bash
pip install pycryptodome
```

## 验证结果

### 修复前
- 文件头: `97bef1f9c084ebd15b7e356759afc4cb` (无效)
- 文件类型: 无法识别
- 播放状态: ❌ 无法播放

### 修复后
- 文件头: `49 44 33 03 00 00 00 00 00 00 ff ef da 2f 60 c2` (有效ID3)
- 文件类型: ✅ Audio file with ID3 version 2.3.0
- HTTP访问: ✅ 200 OK, Content-Type: audio/mpeg
- 播放状态: ✅ 可以正常播放

## 技术细节

### NCM文件格式
1. **文件头**: `CTENFDAM` (8字节)
2. **版本信息**: 2字节
3. **密钥长度**: 4字节 (小端序)
4. **密钥数据**: AES加密的RC4密钥
5. **元数据**: 可选的加密元数据
6. **音频数据**: RC4加密的音频内容

### 解密流程
1. **AES解密**: 使用核心密钥`hzHRAmso5kInbaxW`解密RC4密钥
2. **RC4解密**: 使用解密后的密钥解密音频数据
3. **格式验证**: 检查解密后的文件头是否为有效音频格式
4. **备用方案**: 如果主解密失败，自动使用修复后的备用算法

## 文件修改清单

### 主要修改文件
- `apps/tools/legacy_views.py`
  - `decrypt_ncm_file()`: 改进主解密函数
  - `decrypt_ncm_file_fallback()`: 重写备用解密函数

### 新增文件
- `test_fixed_decryption.py`: 解密算法测试脚本

### 依赖更新
- `pycryptodome`: 用于AES解密

## 测试结果
- ✅ NCM文件成功解密
- ✅ 解密后的文件有正确的ID3标签
- ✅ 文件可以通过HTTP正常访问
- ✅ 音频格式被正确识别为MP3
- ✅ 文件大小合理 (8,502,483 bytes)

## 总结
通过重写NCM解密算法，实现了：
1. **正确的密钥处理**: 使用AES-128-ECB解密RC4密钥
2. **完整的RC4算法**: 实现密钥调度算法(KSA)和伪随机生成算法(PRGA)
3. **自动故障转移**: 主解密失败时自动使用备用算法
4. **详细的验证**: 文件头验证和格式检查

修复后的音频转换器现在可以正确处理NCM文件，生成可播放的MP3文件。