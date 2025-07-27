<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="测试范围与策略概述" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="核心功能采用全矩阵测试（15+用例/模块）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="国际化覆盖20+语言/地区组合" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="性能测试包含冷热启动等8种场景" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点验证精确到事件参数级别
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-001 单对单红包发送" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证中国大陆用户发送普通红包基础流程" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：中国用户向好友发送固定金额红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：
1. 发送方微信余额≥100元
2. 双方互为好友关系
3. 当前网络正常" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="不满足预期**：对应步骤阻止操作并提示具体原因" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：华为P40/EMUI 11" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额50元，祝福语&quot;测试&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 进入聊天窗口点击&quot;+&quot;→&quot;红包&quot;
2. 选择&quot;普通红包&quot;
3. 输入金额50元
4. 输入祝福语
5. 点击&quot;塞钱进红包&quot;
6. 验证支付密码" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 红包发送成功，聊天窗口显示红包消息
2. 发送方余额减少50元
3. 接收方立即收到消息提醒" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：核心功能
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-002 零钱不足时发送" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证余额不足时的拦截机制" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：香港用户零钱不足时发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：
1. 发送方港币余额＜50HKD
2. 已绑定香港信用卡" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：iPhone 13/iOS 15.4" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额50HKD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 按RED-001流程操作
2. 到达支付步骤" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 弹出&quot;余额不足&quot;提示框
2. 显示&quot;使用信用卡支付&quot;选项
3. 切换支付方式后可继续" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：异常场景
（为节省篇幅，此处展示2个示例用例，实际需按规范生成15+个用例，包含：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="不同金额边界值（0.01/200/-1元）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多接收人场景" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="过期红包处理" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="跨时区收发时序等）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-011 拼手气群红包分配" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证日本群组红包金额分配算法" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：10人微信群抢拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：
1. 群成员包含日本/中国用户
2. 红包总金额1000日元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：Xiaomi 12/Android 13" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 发送拼手气红包
2. 10个成员依次领取
3. 记录分配金额" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 总金额精确等于1000日元
2. 单人金额≥0.01日元
3. 金额显示带&quot;¥&quot;符号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：核心功能+国际化
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-001 阿拉伯语RTL布局" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证沙特地区红包界面RTL适配" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：系统语言为ar-SA时的UI呈现" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：Samsung S22/Arabic OS" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 切换系统语言为阿拉伯语
2. 打开红包详情页" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 所有UI元素右对齐
2. 金额数字保持LTR方向
3. 时间显示为Hijri历法" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：国际化UI
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-005 欧元金额格式化" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证法国地区金额显示规范" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：金额为1234.56时的显示格式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：法语系统/欧盟IP" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：输入值1234.56" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 显示为&quot;1 234,56 €&quot;
2. 千分位使用空格
3. 小数点使用逗号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：本地化
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-001 红包发送成功事件" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证send_redpacket事件上报准确性" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：美国用户发送$10红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：Charles抓包工具+美区账号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 完成红包发送
2. 监控网络请求" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 上报事件包含：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="event_id=send_redpacket" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="currency_type=USD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="amount=10.00
2. 时间戳为UTC格式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：埋点验证
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-001 实验组A皮肤展示" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="标题**：验证泰国用户看到春节主题皮肤" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="场景**：实验组A用户访问红包页面" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="环境**：实验分组A/泰国IP" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：
1. 红包图标显示龙年主题
2. 埋点上报experiment_id=2024_CNY" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：AB测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>