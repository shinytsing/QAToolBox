<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="TC-001 发送固定金额红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户发送固定金额红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 用户已登录微信
2. 微信钱包有足够余额
3. 已进入单聊/群聊界面
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天界面&quot;+&quot;按钮
2. 选择&quot;红包&quot;功能
3. 输入红包金额(如10元)
4. 输入祝福语(可选)
5. 点击&quot;塞钱进红包&quot;
6. 输入支付密码完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功，显示在聊天记录中
2. 红包金额和祝福语正确显示
3. 钱包余额相应减少
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-002 发送最小金额红包(0.01元)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送最小金额红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 按TC-001步骤操作
2. 输入金额0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 钱包余额减少0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-003 发送最大金额红包(200元)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送单个红包最大金额" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 按TC-001步骤操作
2. 输入金额200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 钱包余额减少200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-004 发送超过最大金额红包(200.01元)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试发送超过限额的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 按TC-001步骤操作
2. 输入金额200.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;单个红包金额不能超过200元&quot;
2. 无法进入支付环节
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-005 发送红包余额不足" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 钱包余额不足时发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 用户已登录
2. 钱包余额小于红包金额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 按TC-001步骤操作
2. 输入金额大于钱包余额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;余额不足&quot;
2. 提供充值入口
3. 无法完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-006 发送拼手气红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天界面&quot;+&quot;按钮
2. 选择&quot;红包&quot;→&quot;拼手气红包&quot;
3. 输入总金额(如100元)
4. 设置红包个数(如10个)
5. 输入祝福语
6. 完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 显示&quot;拼手气红包&quot;标识
3. 总金额正确扣除
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-007 拼手气红包最小金额分配" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试拼手气红包最小分配金额" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 发送拼手气红包
2. 设置总金额0.1元，个数10个
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;单个红包金额不能低于0.01元&quot;
2. 无法发送
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-008 拼手气红包最大个数限制" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试拼手气红包最大个数" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 发送拼手气红包
2. 尝试设置个数超过100
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;红包个数不能超过100&quot;
2. 无法发送
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-009 接收普通红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户接收普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到他人发送的红包
2. 用户已登录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天界面中的红包
2. 点击&quot;开&quot;按钮
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示红包金额
2. 金额计入钱包余额
3. 聊天记录显示&quot;已领取&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-010 接收拼手气红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户接收拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-009
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击拼手气红包
2. 点击&quot;开&quot;按钮
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示随机分配金额
2. 金额计入钱包
3. 可查看领取详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-011 领取已过期红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试领取过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到红包已超过24小时
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击过期红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包已过期&quot;
2. 无法领取
3. 显示&quot;已过期&quot;状态
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-012 重复领取红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试重复领取同一红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已成功领取过该红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 再次点击已领取的红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;已领取&quot;状态
2. 显示领取金额
3. 无法再次领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-013 查看发出的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查询已发送的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已发送过红包
2. 进入钱包界面
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;钱包&quot;
2. 点击&quot;红包记录&quot;
3. 选择&quot;发出的红包&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有发出的红包
2. 包含金额、时间、接收人信息
3. 可查看领取详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-014 查看收到的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查询已收到的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-013
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;红包记录&quot;
2. 选择&quot;收到的红包&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有收到的红包
2. 包含金额、发送人、时间信息
3. 可按时间筛选
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-015 不同设备型号测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 在不同设备上测试红包功能" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备iOS和Android多款设备
2. 微信版本相同
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 在各设备上执行TC-001
2. 在各设备上执行TC-009
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 各设备功能表现一致
2. UI适配正常
3. 无兼容性问题
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-016 不同微信版本测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试新旧版本兼容性" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备不同微信版本设备
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 旧版本发送红包
2. 新版本接收红包
3. 反之亦然
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 跨版本红包收发正常
2. 无兼容性问题
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-017 红包防刷测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试红包防刷机制" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备多个测试账号
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 短时间内连续发送大量红包
2. 同一账号频繁领取红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统检测异常行为
2. 可能触发风控限制
3. 提示操作频繁
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-018 支付密码错误测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试支付密码错误处理" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 进入红包支付环节
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 连续输入错误支付密码(3次)
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 第三次错误后锁定支付功能
2. 提示&quot;支付密码错误次数过多&quot;
3. 需通过身份验证解锁
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-019 高峰期红包性能" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 模拟高峰期红包操作" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备压力测试环境
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 模拟大量用户同时收发红包
2. 监控服务器响应
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 平均响应时间&lt;1s
2. 无超时失败
3. 服务器资源占用正常
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-020 红包领取速度测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试红包领取响应速度" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备网络环境监控工具
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 发送红包
2. 立即点击领取
3. 记录响应时间
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 领取操作完成时间&lt;500ms
2. 金额实时到账
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
```
这个测试用例文档包含了微信红包功能的全面测试覆盖，包括：
1. 发送红包(普通和拼手气)
2. 接收红包
3. 红包记录查询
4. 兼容性测试
5. 安全性测试
6. 性能测试
每个分类下都包含了正常场景、边界场景和异常场景的测试用例，共计20个详细测试用例。测试步骤清晰明确，预期结果具体可验证，重要程度标识合理。可根据实际需要进一步扩展或调整。" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>