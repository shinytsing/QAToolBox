<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="TC-001 发送固定金额红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户发送固定金额红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 用户已登录微信
2. 微信钱包有足够余额
3. 已进入与好友/群的聊天界面
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天界面&quot;+&quot;按钮
2. 选择&quot;红包&quot;功能
3. 输入红包金额(如100元)
4. 输入祝福语(可选)
5. 点击&quot;塞钱进红包&quot;
6. 输入支付密码完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功，显示在聊天记录中
2. 红包金额显示正确
3. 发送者钱包余额减少相应金额
4. 接收方收到红包通知
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-002 发送最小金额红包(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送金额为0.01元的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-6步同TC-001，金额输入0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示为0.01元
3. 余额精确扣除0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-003 发送最大金额红包(边界值)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送金额为200元的单个红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-6步同TC-001，金额输入200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示为200元
3. 余额扣除200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-004 发送超过限额红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试发送201元的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-4步同TC-001，金额输入201元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;单个红包金额不能超过200元&quot;
2. 无法进入支付页面
3. 钱包余额不变
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
1-4步同TC-001，金额输入大于余额的数值
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;余额不足&quot;
2. 无法进入支付页面
3. 提供充值入口
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
2. 选择&quot;红包&quot;功能
3. 选择&quot;拼手气红包&quot;
4. 输入总金额(如100元)和红包个数(如5个)
5. 输入祝福语
6. 完成支付
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功，显示&quot;拼手气红包&quot;标识
2. 总金额正确显示
3. 余额减少100元
4. 接收方看到拼手气红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-007 拼手气红包最小金额边界" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送总金额0.01元的拼手气红包(1个)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-4步同TC-006，总金额0.01元，个数1
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示0.01元
3. 余额减少0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-008 拼手气红包最大金额边界" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送200元拼手气红包(100个)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-4步同TC-006，总金额200元，个数100
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 每个红包最小金额为0.01元
3. 余额减少200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-009 拼手气红包个数超限(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试发送101个拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC-001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1-4步同TC-006，个数输入101
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 系统提示&quot;红包个数不能超过100个&quot;
2. 无法继续操作
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-010 拼手气红包金额分配验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 验证拼手气红包金额分配合理性" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 已发送拼手气红包(如100元5个)
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 5个不同用户领取红包
2. 记录每个红包金额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 5个红包金额总和为100元
2. 每个红包金额≥0.01元
3. 金额分配随机且合理
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-011 单人领取普通红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户领取普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到普通红包消息
2. 红包未过期
3. 红包未被领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天中的红包
2. 点击&quot;开&quot;按钮
3. 查看领取结果
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 成功领取红包
2. 显示领取金额
3. 钱包余额增加相应金额
4. 聊天记录显示&quot;已领取&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-012 领取拼手气红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 用户领取拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到拼手气红包
2. 红包未领完
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击拼手气红包
2. 点击&quot;开&quot;按钮
3. 查看领取金额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 成功领取随机金额红包
2. 金额在合理范围内
3. 钱包余额增加
4. 红包剩余个数/金额更新
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-013 红包领取顺序验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 验证多人领取拼手气红包的顺序" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 已发送100元10个的拼手气红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 10个用户依次领取红包
2. 记录领取顺序和金额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 先到先得，领完为止
2. 第11个用户无法领取
3. 总金额分配正确
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-014 领取已过期红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试领取过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 红包已超过24小时有效期
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击过期红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包已过期&quot;
2. 无法领取
3. 显示过期红包详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-015 重复领取红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试重复领取已领过的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 已成功领取该红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 再次点击已领取的红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;已领取&quot;状态
2. 显示领取金额和时间
3. 无法再次领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-016 领取已领完的红包(异常)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试领取已被领完的拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 拼手气红包已被全部领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击已被领完的红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包已领完&quot;
2. 可查看领取详情
3. 无法领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-017 查看发出的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查看已发送的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 已发送过红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;我&quot;-&quot;服务&quot;-&quot;钱包&quot;
2. 点击&quot;红包&quot;-&quot;发出的红包&quot;
3. 查看记录列表
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有发出的红包记录
2. 包含金额、时间、接收方信息
3. 可查看详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-018 查看收到的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查看已收到的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 已收到过红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;我&quot;-&quot;服务&quot;-&quot;钱包&quot;
2. 点击&quot;红包&quot;-&quot;收到的红包&quot;
3. 查看记录列表
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有收到的红包记录
2. 包含金额、时间、发送方信息
3. 可查看详情
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-019 红包记录筛选功能" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 按时间筛选红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 有多条红包记录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入红包记录页面
2. 点击筛选按钮
3. 选择特定时间段
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 只显示选定时间范围内的记录
2. 记录排序正确
3. 无记录时显示空状态
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 低
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-020 不同设备领取红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 在不同设备上领取红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 收到未领取红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 在iOS设备上点击红包但不领取
2. 换到Android设备尝试领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 可在不同设备间正常领取
2. 状态同步及时
3. 金额显示正确
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-021 不同微信版本红包兼容" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 新旧版本微信收发红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 发送方使用最新版，接收方使用旧版
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 新版发送红包
2. 旧版接收红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包可正常收发
2. 基础功能正常
3. 新特性在旧版有降级处理
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-022 高峰期红包发送性能" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 春节期间大量并发发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 模拟高并发场景
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 使用压测工具模拟1000+用户同时发红包
2. 监控服务器响应
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 成功率&gt;99.9%
2. 平均响应时间&lt;1s
3. 无数据丢失或错乱
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC-023 红包领取响应时间" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 测量红包领取响应时间" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 有未领取红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击红包开始计时
2. 完成领取停止计时
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 端到端响应时间&lt;500ms
2. 余额更新及时
3. 状态同步快速
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
```
(注: 实际测试中应根据需求补充更多边界值和异常场景用例，此处因篇幅限制仅展示部分典型用例)" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>