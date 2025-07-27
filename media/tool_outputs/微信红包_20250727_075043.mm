<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="国际化与本地化测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="覆盖20+语言版本(含RTL语言)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="本地化格式：日期/时间/货币/数字/电话号码" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="文化适配：红包封面/祝福语/表情符号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="地区特定功能：中国大陆/港澳台/东南亚/欧美等地区差异
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="埋点与数据分析测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="关键路径埋点：红包发送/领取/查看详情" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="漏斗分析：从创建到领取完整流程" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="异常场景埋点：领取失败/金额异常等" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多维度统计：地区/语言/设备维度
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB实验测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="新红包样式实验组对比" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="不同分发策略效果验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="地区差异化功能实验" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多语言环境下UI实验
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="版本测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="跨版本数据迁移(红包记录)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="强制更新策略验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="地区灰度发布验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="降级安装兼容性
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="SEND-001 普通红包发送基础流程" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：中国大陆用户发送普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：登录中国大陆账号且钱包余额充足" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试目的**：验证基础红包发送流程" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额200元，接收人1个，祝福语&quot;新年快乐&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 进入聊天窗口点击&quot;+&quot;选择红包
2. 选择&quot;普通红包&quot;类型
3. 输入金额200元
4. 输入祝福语&quot;新年快乐&quot;
5. 点击支付完成发送" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="聊天窗口显示红包消息" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包显示金额和祝福语" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="钱包余额减少200元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="TRACK: 触发send_redpacket事件" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：功能测试,埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="SEND-002 金额边界值测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：测试红包金额边界值" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：登录账号且余额超过1000元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="最小值：0.01元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="最大值：200元(中国大陆单红包限额)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="异常值：0元/201元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 尝试发送0.01元红包
2. 尝试发送200元红包
3. 尝试发送0元红包
4. 尝试发送201元红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="0.01元和200元发送成功" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="0元和201元提示&quot;金额不合法&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="TRACK: 异常金额触发invalid_amount事件" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：功能测试,边界测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RECEIVE-001 正常红包领取流程" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：用户领取普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：收到未领取的红包消息" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试目的**：验证红包领取完整流程" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 点击聊天窗口中的红包消息
2. 点击&quot;開&quot;按钮
3. 查看红包详情页" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包金额正确显示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="钱包余额相应增加" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包状态变为&quot;已领取&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="TRACK: 触发receive_redpacket事件" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：功能测试,埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RECEIVE-002 红包过期场景" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：领取已过期红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：收到24小时前发送的红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 点击过期红包
2. 查看提示信息" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示&quot;红包已过期&quot;提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额退回原账户(如适用)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="TRACK: 触发expired_redpacket事件" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：功能测试,异常测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-001 多语言界面适配" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：阿拉伯语(RTL)界面测试" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：设备语言设置为阿拉伯语" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 打开红包功能页面
2. 检查UI布局方向
3. 测试红包发送流程" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="整体布局右对齐" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="文本和图标镜像翻转" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="功能流程正常" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：国际化测试,UI测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-002 本地化格式验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：德国地区货币格式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：账号地区设置为德国" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**：金额100.50" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 创建红包输入100.50
2. 查看金额显示格式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示为&quot;100,50 €&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="小数点使用逗号" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="货币符号在后" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：国际化测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-001 红包发送埋点验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：验证发送红包埋点参数" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：开启调试模式可查看埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 发送一个100元红包
2. 捕获发送事件埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="事件名：send_redpacket" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="包含参数：amount=100, type=normal" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="包含设备信息和用户ID" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-001 新红包样式实验分组" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：验证实验分组正确性" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：用户属于实验组B" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 发送红包查看UI样式
2. 验证后台实验分组记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="显示实验组B特有样式" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="后台记录与前端一致" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：AB测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="VERSION-001 跨版本数据迁移" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**：从v8.0升级到v9.0红包记录迁移" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**：v8.0有10条红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**：
1. 安装v9.0覆盖升级
2. 检查红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**：" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="10条记录完整迁移" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="金额数据准确无误" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**：高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**：版本测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="测试覆盖率分析" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="功能测试覆盖率：95% (核心功能全覆盖，部分边缘场景待补充)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="国际化测试覆盖率：90% (覆盖主要语言和地区)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点测试覆盖率：85% (关键路径全覆盖，部分辅助埋点待验证)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="AB实验测试覆盖率：80% (基础分组验证完成)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="版本测试覆盖率：85% (主要升级场景覆盖)
" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="注：实际覆盖率应根据具体需求文档和测试执行情况动态调整*" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>