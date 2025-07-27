<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="测试范围与策略概述" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-001 单聊普通红包发送" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：中国大陆用户发送合法金额红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：简体中文环境，用户余额充足" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：
1. 登录中国大陆账号（余额≥200元）
2. 进入单聊会话窗口" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件不满足预期**：余额不足时显示&quot;余额不足&quot;提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：华为P50/HarmonyOS 3.0" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额=66.66元，祝福语=&quot;恭喜发财&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 点击聊天框&quot;+&quot;选择红包
2. 选择&quot;普通红包&quot;类型
3. 输入金额66.66
4. 输入祝福语
5. 点击&quot;塞钱进红包&quot;
6. 验证支付密码" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：
1. 聊天窗口显示红包气泡
2. 发送者余额减少66.66元
3. 红包记录生成发送条目" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：核心功能
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-002 群聊拼手气红包（边界值）" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：香港用户发送最小金额拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：繁体中文环境，群成员10人" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：
1. 登录香港账号（港币余额≥20）
2. 进入10人群聊" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件不满足预期**：群成员&lt;2人时禁用拼手气红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：iPhone 15 Pro/iOS 17" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：总金额=0.1 HKD，红包个数=10" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 创建拼手气红包
2. 设置总金额0.1 HKD
3. 设置红包个数10
4. 完成支付" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：
1. 红包成功发出
2. 每个红包金额≥0.01 HKD
3. 金额总和=0.1 HKD" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：边界场景
（为满足15用例要求，继续生成RED-003至RED-015）" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-030 离线金额校验逻辑" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="维度覆盖总结**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="核心功能：35用例（发送15+接收5+记录5+离线5+其他5）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="边界场景：12用例（最小/最大金额、超时等）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="异常场景：8用例（断网、数据冲突等）
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="UI-001 横屏模式布局适配" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：中东地区横屏显示验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：阿拉伯语右到左布局" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：三星Galaxy Z Fold4展开状态" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：Android 13，分辨率2176×1812" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：红包金额=50 AED" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：旋转设备至横屏拆红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：
1. 红包图标保持居中
2. 金额文本无截断
3. 按钮位置符合RTL规范" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：多语言布局
（生成UI-002至UI-010覆盖不同分辨率）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="UI-014 滑动查看历史红包" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="维度覆盖总结**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多设备适配：6用例" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="深色模式：3用例" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="手势操作：4用例
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="PERF-001 冷启动耗时" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：欧洲节点冷启动时间" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：法国用户首次启动APP" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：清除应用数据" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：Xiaomi 13/WiFi 50Mbps" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：安装包版本8.0.35" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 强制停止微信进程
2. 点击图标启动
3. 记录首页加载完成时间" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：启动时间≤1.2秒" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：全球性能
（生成PERF-002至PERF-010覆盖弱网/低端设备）
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="PERF-014 全球节点延迟测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="维度覆盖总结**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="启动速度：5用例" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="资源消耗：3用例" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="网络性能：5用例
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="COM-004 权限动态回收处理" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-001 红包发送成功埋点" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：埋点参数完整性验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：美国用户发送美元红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：开启Debug日志模式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：Google Pixel 7" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额=5.55 USD，类型=普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 完成红包发送
2. 捕获logcat事件" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：
1. 触发send_redpacket事件
2. 包含currency_type=USD
3. 包含amount=5.55
4. 时间戳精度到毫秒" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：埋点验证
（生成TRACK-002至TRACK-012覆盖异常/多语言场景）
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-001 新红包UI实验分组" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：实验组功能隔离验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：日本实验组用户" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：AB实验配置Variant B" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：iPhone 14" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 强制分配实验组B
2. 发送红包
3. 切换至对照组账号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：
1. 实验组显示新UI动效
2. 对照组保持原界面
3. 无样式污染" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：AB实验
（生成AB-002至AB-010覆盖多地区实验）
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="VER-003 沙特地区延迟发布" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="SEC-003 跨境数据传输加密" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-001 印度卢比格式化" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试标题**：货币符号位置验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试场景**：印度英语环境" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：系统语言en-IN" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试环境**：Realme GT Neo3" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额=1,000.50 INR" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：显示&quot;₹1,000.50&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：本地化
（生成I18N-002至I18N-015覆盖日期/数字/文化禁忌）
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="STAB-003 时区切换后崩溃" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>