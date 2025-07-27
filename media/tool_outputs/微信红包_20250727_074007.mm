<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="TC001 发送固定金额红包" COLOR="#FF7F50" STYLE="fork">
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
4. 输入红包祝福语
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
    <node TEXT="TC002 发送最小金额红包(0.01元)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送最小金额红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC001步骤1-2
2. 输入金额0.01元
3. 完成后续发送流程
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示为0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC003 发送最大金额红包(200元)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送单红包最大金额" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC001步骤1-2
2. 输入金额200元
3. 完成后续发送流程
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 金额显示为200元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC004 发送拼手气红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC001步骤1-2
2. 选择&quot;拼手气红包&quot;
3. 输入总金额(如100元)和红包个数(如5个)
4. 完成后续发送流程
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 显示&quot;拼手气红包&quot;标识
3. 总金额和个数正确
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC005 拼手气红包最小金额(0.01元/个)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 发送极小金额拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC004步骤1-2
2. 输入总金额0.05元，个数5个
3. 完成发送
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功
2. 每个红包最小金额为0.01元
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC006 余额不足发送红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 钱包余额不足时发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 用户已登录
2. 钱包余额小于红包金额
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 尝试发送金额大于余额的红包
2. 完成发送流程
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 提示&quot;余额不足&quot;
2. 红包发送失败
3. 钱包余额不变
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC007 输入非法金额(字母/符号)" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 输入非数字金额" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC001
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC001步骤1-2
2. 在金额栏输入&quot;abc&quot;或&quot;!@#&quot;
3. 尝试继续操作
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 无法输入非数字字符
2. &quot;塞钱进红包&quot;按钮置灰
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC008 单人领取普通红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 正常领取普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到单人发送的红包
2. 红包未过期
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
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC009 领取拼手气红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 领取拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
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
2. 金额在合理范围内(0.01-剩余金额)
3. 钱包余额增加
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC010 重复领取红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试重复领取已领红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已成功领取某红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 再次点击已领取的红包
2. 尝试操作
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;已领取&quot;状态
2. 无法再次领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC011 领取过期红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 领取已过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 红包已超过24小时有效期
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击过期红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示&quot;红包已过期&quot;
2. 无法领取
3. 显示退款提示(如适用)
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC012 查看发出的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查询发送的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 已发送过红包
2. 进入钱包界面
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;钱包&quot;
2. 点击&quot;红包记录&quot;
3. 查看&quot;发出的红包&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有发出红包记录
2. 包含金额、时间、接收人等信息
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC013 查看收到的红包记录" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 查询收到的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 同TC012
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 同TC012步骤1-2
2. 查看&quot;收到的红包&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 正确显示所有收到红包记录
2. 包含金额、发送人、时间等信息
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC014 未领取红包自动退款" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 24小时后未领红包自动退款" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 发送的红包已超过24小时
2. 红包未被完全领取
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 等待24小时
2. 查看钱包余额和红包记录
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 未领金额自动退回
2. 钱包余额增加相应金额
3. 红包记录显示&quot;已退款&quot;
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC015 不同iOS版本红包功能" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 在iOS不同版本使用红包功能" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 设备安装不同iOS版本(12/13/14/15)
2. 微信版本相同
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 在各版本设备上执行TC001
2. 执行TC008
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 各版本功能正常
2. 界面显示正常
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC016 不同Android机型红包功能" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 在不同Android机型使用红包功能" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 准备多个品牌Android手机
2. 微信版本相同
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 在各设备上执行TC001
2. 执行TC008
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 各机型功能正常
2. 界面适配良好
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC017 高频率发送红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 短时间内连续发送多个红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 钱包余额充足
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 在1分钟内连续发送10个红包
2. 观察系统响应
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 所有红包发送成功
2. 无卡顿或崩溃
3. 钱包余额准确扣除
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC018 多人同时抢红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 群内多人同时抢红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 10人以上微信群
2. 发送拼手气红包
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 发送拼手气红包
2. 群成员同时点击领取
3. 观察领取结果
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 所有领取请求处理正常
2. 金额分配正确
3. 无并发问题
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC019 红包钓鱼链接检测" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 识别伪装成红包的钓鱼链接" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 收到可疑&quot;红包&quot;消息
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击可疑红包链接
2. 观察系统反应
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 安全警告提示
2. 不执行危险操作
3. 可能自动屏蔽
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TC020 红包金额篡改测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**: 尝试篡改红包金额" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 技术测试环境
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 使用工具拦截并修改红包金额数据包
2. 尝试发送
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 服务器端验证失败
2. 红包发送被拒绝
3. 可能触发安全机制
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高
```
以上测试用例覆盖了微信红包的主要功能场景，包括:
1. 发送红包(普通/拼手气)
2. 接收红包
3. 红包记录与退款
4. 兼容性测试
5. 性能测试
6. 安全测试
每个分类下都包含了正常场景、边界场景和异常场景的测试用例，确保功能完整性。测试步骤清晰明确，预期结果具体可验证，重要程度标识有助于测试优先级管理。" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>