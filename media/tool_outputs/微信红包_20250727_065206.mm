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
3. 选择&quot;普通红包&quot;类型
4. 输入红包金额(如100元)
5. 输入祝福语
6. 点击&quot;塞钱进红包&quot;
7. 输入支付密码完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功，显示在聊天记录中
2. 红包金额显示正确
3. 钱包余额相应减少
4. 接收方收到红包提醒
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-002 发送最小金额红包(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送0.01元红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-6步同TC-001
7. 输入金额0.01元
8. 完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示为0.01元
3. 余额减少0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-003 发送最大金额红包(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送200元红包(单红包上限)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-6步同TC-001
7. 输入金额200元
8. 完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示为200元
3. 余额减少200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-004 发送超过限额红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试发送201元红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-6步同TC-001
7. 输入金额201元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;单个红包金额不能超过200元&quot;提示
2. 无法进入支付页面
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-005 发送红包余额不足(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 钱包余额不足时发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 用户已登录
2. 钱包余额小于红包金额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-6步同TC-001
7. 输入金额大于余额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;余额不足&quot;提示
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
1. 点击&quot;+&quot;→&quot;红包&quot;
2. 选择&quot;拼手气红包&quot;
3. 输入总金额(如100元)
4. 设置红包个数(如5个)
5. 输入祝福语
6. 完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 显示&quot;拼手气红包&quot;标识
3. 总金额正确
4. 接收方看到&quot;拼手气红包&quot;提示
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-007 拼手气红包最小金额(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送0.01元/个的拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-5步同TC-006
6. 设置总金额0.05元，个数5个
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 每个红包最小金额为0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-008 拼手气红包最大个数(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送100个拼手气红包(上限)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-5步同TC-006
6. 设置个数100个
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 可被100人领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-009 超过最大红包个数(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试发送101个红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-5步同TC-006
6. 尝试设置101个
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包个数不能超过100个&quot;提示
2. 无法完成设置
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-010 拼手气红包金额不足(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 总金额不足以分配最小红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-5步同TC-006
6. 设置总金额0.04元，个数5个
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;单个红包金额不能低于0.01元&quot;提示
2. 无法完成设置
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-011 领取普通红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户领取普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到普通红包
2. 红包未过期
3. 红包未被领完
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天中的红包
2. 点击&quot;开&quot;按钮
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示领取金额
2. 钱包余额增加相应金额
3. 聊天记录显示&quot;已领取&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-012 领取拼手气红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户领取拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到拼手气红包
2. 红包未过期
3. 红包未被领完
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击拼手气红包
2. 点击&quot;开&quot;按钮
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示随机分配金额
2. 金额在合理范围内(总金额/个数)
3. 钱包余额增加
4. 显示手气排名(如适用)
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-013 最后一个红包领取" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 领取最后一个红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 红包剩余最后一个
2. 当前用户未领取过
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击红包
2. 点击&quot;开&quot;按钮
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 领取剩余全部金额
2. 红包状态变为&quot;已领完&quot;
3. 显示&quot;手气最佳&quot;(如适用)
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-014 重复领取红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试重复领取已领过的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已领取过该红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 再次点击已领取的红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;已领取&quot;状态
2. 不再显示&quot;开&quot;按钮
3. 显示领取金额和详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-015 领取过期红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试领取过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 红包已超过24小时有效期
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击过期红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包已过期&quot;提示
2. 显示退款信息(如适用)
3. 无法领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-016 领取已领完红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试领取已被领完的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 红包已被其他用户领完
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击已领完的红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包已领完&quot;状态
2. 显示领取详情
3. 无法再次领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-017 查看发出的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查看已发出的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已发送过红包
2. 进入钱包-红包记录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;我&quot;-&quot;服务&quot;-&quot;钱包&quot;
2. 点击&quot;红包记录&quot;
3. 选择&quot;发出的红包&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有发出的红包
2. 包含金额、时间、领取状态等信息
3. 可点击查看详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-018 查看收到的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查看已收到的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已收到红包
2. 进入钱包-红包记录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC-017步骤1-2
2. 选择&quot;收到的红包&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有收到的红包
2. 包含金额、发送人、时间等信息
3. 可点击查看详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-019 过期红包自动退款" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 红包过期未领完自动退款" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 发送的红包已超过24小时
2. 红包未被完全领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 等待红包过期
2. 查看钱包余额
3. 查看红包记录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 未领取金额自动退回
2. 余额相应增加
3. 红包记录显示&quot;已退款&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-020 退款金额验证(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 验证最小金额退款" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 发送0.01元红包未领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 等待红包过期
2. 查看钱包余额变化
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 0.01元正确退回
2. 余额增加0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 低
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-021 iOS系统兼容性" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: iOS设备红包功能验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 使用iOS设备
2. 微信版本为最新
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 执行TC-001发送红包
2. 执行TC-011领取红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 功能与Android一致
2. UI适配正常
3. 无闪退等异常
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-022 Android不同版本兼容性" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测试Android 8-13版本" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 使用不同Android版本设备
2. 微信版本相同
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 在各版本设备上执行核心红包功能
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 各版本功能正常
2. 无兼容性问题
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-023 高并发抢红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 多人同时抢红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备100人测试群
2. 发送拼手气红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 发送100元/100个红包
2. 组织100人同时点击领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统响应正常
2. 金额分配正确
3. 无并发错误
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-024 大量红包记录加载" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 加载1000条红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 账户有大量红包记录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入红包记录页面
2. 滑动加载更多
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 记录加载流畅
2. 无卡顿或崩溃
3. 数据显示完整
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
```
(注: 实际测试中应根据需求补充更多边界值和异常场景测试用例，此处为示例性展示主要测试场景)" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>