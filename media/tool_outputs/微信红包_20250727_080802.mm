<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="FUN-001 普通红包创建验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：中国大陆用户创建普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：登录状态、钱包余额≥10元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额10元(正常)、0.01元(边界)、200元(边界)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 进入聊天窗口点击&quot;红包&quot;图标
2. 选择&quot;普通红包&quot;类型
3. 输入测试金额
4. 输入祝福语&quot;新年快乐&quot;
5. 点击支付完成创建" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="创建成功跳转至聊天窗口" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="聊天记录显示红包消息" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="钱包余额准确扣除" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点TRACK_Redpack_Create触发" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能测试/埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="FUN-002 拼手气红包金额验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：香港用户创建拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：港币钱包余额≥100HKD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：总金额100HKD(正常)、0.01HKD(异常)、500HKD(边界)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 选择&quot;拼手气红包&quot;
2. 输入总金额和红包个数(5个)
3. 使用香港身份证完成实名验证
4. 确认支付" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额≥1HKD时创建成功" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额&lt;1HKD提示&quot;最低金额1HKD&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="触发TRACK_Redpack_LuckyCreate埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能测试/国际化测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="FUN-003 跨时区红包领取" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：北京时间23:50发送红包，美西用户领取" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：发送方已创建24小时有效红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 发送方(UTC+8)23:50发送
2. 接收方(UTC-8)在本地时间7:30打开聊天
3. 点击领取红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示剩余有效期16小时20分钟" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="领取后双方聊天记录同步更新" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="时区转换计算正确" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能测试/国际化测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-001 阿拉伯语RTL布局" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：沙特阿拉伯用户使用阿拉伯语界面" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：系统语言设为ar-SA" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证点**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包创建界面右对齐" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额输入框从右向左输入" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="日历显示为Hijri历法" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：国际化测试/UI测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-002 日元金额格式化" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：日本用户发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：1000円、10,000円" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期显示**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额显示为&quot;¥1,000&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="小数部分自动隐藏" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="输入框支持全角数字" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：国际化测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-001 红包曝光埋点" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：红包消息在聊天窗口展示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证参数**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="redpack_type: normal/lucky" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="currency_type: CNY/HKD/JPY" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="is_expired: true/false" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="触发条件**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="聊天列表滚动到可视区域" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="首次打开包含红包的聊天" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-001 红包气泡样式实验" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="实验组**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="A组：传统红色气泡" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="B组：动态开启动画" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证指标**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="点击率差异" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="领取耗时" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="各地区表现一致性" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：AB测试/UI测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="VERSION-001 数据迁移测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：从v8.0.20升级到v8.1.0" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="未领取红包3个" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="过期红包2个" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包记录100条" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证点**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="所有红包状态保持正确" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="余额统计准确" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="本地记录完整迁移" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：版本测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="覆盖率分析" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="功能测试：92%覆盖（剩余8%为极端异常场景）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="国际化测试：95%覆盖（剩余5%为小众语言组合场景）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点测试：90%覆盖（剩余10%为低频错误路径）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="AB测试：100%覆盖当前实验方案" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="版本测试：88%覆盖（剩余12%为跨大版本迁移）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="功能测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="已覆盖：核心收发流程、金额校验、状态同步" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="未覆盖：银行系统级故障时的补偿流程
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="国际化测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="已覆盖：主流语言/地区格式、时区转换" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="未覆盖：希伯来语与阿拉伯语混合排版场景
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="埋点测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="已覆盖：关键路径埋点、参数传递" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="未覆盖：埋点服务不可用时的降级策略
```" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>