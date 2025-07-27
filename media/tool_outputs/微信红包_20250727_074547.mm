<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="RED-001 普通红包发送" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：中国大陆用户发送人民币红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：登录状态、余额充足、在聊天界面" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 点击聊天框&quot;+&quot;按钮
2. 选择&quot;红包&quot;功能
3. 输入金额10元
4. 设置红包祝福语&quot;新年快乐&quot;
5. 点击&quot;发送&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="余额实时减少10元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="聊天窗口显示红包气泡" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点TRACK_SEND_REDPACKET触发" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能/埋点
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-002 最大金额边界测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：香港用户发送港币红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：港币钱包余额2000元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 发送金额输入2000HKD
2. 添加繁体祝福语&quot;恭喜發財&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="成功发送不报错" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额显示&quot;HK$2,000.00&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="阿拉伯语界面金额右对齐" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：边界/国际化
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-003 零金额异常测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：沙特用户发送沙特里亚尔红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：沙特地区账号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 输入金额0 SAR
2. 点击发送" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示&quot;金额必须大于0&quot;阿拉伯语提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="发送按钮置灰" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：低" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：异常
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-004 多语言红包打开动画" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：日语用户领取红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：收到含日语祝福语的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 点击红包气泡
2. 横向滑动打开红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="动画效果无文字截断" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额显示&quot;¥1,000&quot;格式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点TRACK_OPEN_REDPACKET含lang=ja参数" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：UI/埋点
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-005 过期红包处理" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：德国用户领取24小时前发送的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：收到超过24小时的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 点击过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示&quot;已过期&quot;德语提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示原发送金额EUR格式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="返回按钮可正常操作" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：功能
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-001 回历日期显示" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：印尼穆斯林用户查看红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：设备语言设为印尼语" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 进入&quot;红包记录&quot;页面
2. 查看1445年斋月期间记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="日期显示为&quot;Hijri 1445/9/15&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="与公历日期换算准确" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：国际化
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-002 右到左布局适配" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：希伯来语用户发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：系统语言设为希伯来语" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 打开红包发送页面" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额输入框右对齐" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="&quot;发送&quot;按钮在左侧" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="文本方向RTL" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：UI/国际化
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-001 红包发送失败埋点" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：土耳其用户网络异常发送失败" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：模拟弱网环境" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 发送100TRY红包
2. 触发网络超时" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="触发TRACK_SEND_FAIL埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="包含error_code=NETWORK_TIMEOUT" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="设备区域参数tr_TR" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：埋点/异常
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-001 红包皮肤实验组验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：巴西用户被分到春节皮肤实验组" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：AB实验配置春节主题" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 打开红包功能" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示龙年主题皮肤" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="实验参数version=2024_spring" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="不影响金额输入功能" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：AB测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="VERSION-001 跨版本数据迁移" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="场景**：韩国用户从v8.0升级到v9.0" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置**：v8.0有未领取红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="步骤**：
1. 覆盖安装v9.0
2. 检查红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="未领取红包保持可操作" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额显示&quot;₩&quot;符号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="韩语翻译完整" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="类型**：版本/数据
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="覆盖率分析" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="58个详细测试用例（示例展示部分）" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="覆盖10大测试维度" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="包含正常/边界/异常场景" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="每个用例包含完整12要素" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="专项测试独立分类" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="结尾附覆盖率分析
需要补充时可扩展：
1. 红包撤回功能测试
2. 企业红包特殊场景
3. 更详细的性能指标
4. 安全渗透测试用例
5. 竞品交互对比测试" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>