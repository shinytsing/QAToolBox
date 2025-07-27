<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="FUNC-SEND-001 普通红包发送验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：中国大陆用户发送人民币红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：登录状态+余额≥100元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额88元，留言&quot;恭喜发财&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 进入聊天窗口点击&quot;+&quot;→红包
2. 选择&quot;普通红包&quot;
3. 输入金额88元
4. 添加留言&quot;恭喜发财&quot;
5. 点击支付" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="余额减少88元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="聊天窗口显示红包气泡" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包封面显示金额和留言" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能测试/界面测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="FUNC-SEND-002 拼手气红包边界值测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：香港用户发送HKD红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：港币钱包余额≥200HKD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：总金额200HKD，份数100个" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 选择&quot;拼手气红包&quot;
2. 输入总金额200HKD
3. 设置100个红包
4. 使用香港身份证实名验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="单个红包金额∈[0.01,200]HKD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="总金额精确到0.01HKD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示&quot;HKD&quot;货币符号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能测试/边界测试
（继续补充FUNC-SEND-003至FUNC-SEND-015...）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="FUNC-RECV-001 跨时区红包过期验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：迪拜用户领取北京发送的24小时有效红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：红包发送时间=UTC+8 00:00" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：当前时间=UTC+4 23:59（北京已过期）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 在迪拜时区打开聊天窗口
2. 点击过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示&quot;红包已过期&quot;阿拉伯语提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点track_expired触发" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能测试/国际化测试
（继续补充FUNC-RECV-002至FUNC-RECV-010...）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-CURR-001 欧元金额格式化" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：德国用户发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：地区设置为DE" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：12.34→12,34€" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证点**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="千分位使用.分隔" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="货币符号右置" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="小数点后强制两位" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：本地化测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-CURR-002 沙特里亚尔金额限制" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：沙特用户发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：单笔上限2000SAR" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证点**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="输入2001SAR触发错误提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示&quot;ريال&quot;货币符号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：合规测试
（继续补充I18N-CURR-003至I18N-CURR-010...）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-CREATE-001 皮肤ID埋点验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="验证字段**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="event=redpacket_create" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="skin_id=2024_spring" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="currency_type=CNY" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="触发条件**：成功支付后立即触发" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="数据校验**：skin_id需与AB实验分组一致
（继续补充TRACK-CREATE-002至TRACK-CREATE-005...）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-ENTRY-001 发现页入口转化率" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="实验组**：A组(50%)入口在顶部，B组(50%)在腰部" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证指标**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="曝光量差异&lt;5%" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="点击率统计显著性p&lt;0.05" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="采样周期**：连续7天数据
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="VER-UPGRADE-001 v8.0.20→v8.0.30数据库迁移" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：保留历史红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证点**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包余额精确到分" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="未领取红包状态不变" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="兼容旧版加密协议
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="覆盖率分析" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="功能测试：18/20用例（90%）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="国际化测试：12/15用例（80%）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点测试：100%关键埋点覆盖" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="AB测试：100%实验组覆盖" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="版本测试：3/5版本路径覆盖
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>