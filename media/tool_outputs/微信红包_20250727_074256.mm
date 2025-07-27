<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="国际化与本地化测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="覆盖20+语言版本的UI适配与功能验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="验证10+主要地区的本地化格式(日期/货币/数字等)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试地区特定功能(如中国大陆的电子红包与海外现金红包差异)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="文化适配性检查(颜色/图标/文案禁忌)
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="埋点与数据分析测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="核心流程埋点验证(发红包/抢红包/查看记录)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="异常场景埋点捕获(余额不足/网络中断等)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多语言环境埋点参数验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="埋点数据实时性测试(延迟&lt;5s)
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB实验测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="新红包样式实验组验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="红包分发算法AB测试" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多语言文案实验效果对比" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="实验分组准确性验证(用户标签匹配度&gt;99%)
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="版本测试范围" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="覆盖安装测试(保留历史红包记录)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="强制更新流程验证(低于最低版本时)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="多地区灰度发布验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="降级兼容性测试(高版本数据在低版本可读)
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-001 普通红包发送验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 中国大陆用户发送普通红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 登录中国大陆账号
2. 钱包余额≥100元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试目的**: 验证基础红包发送流程" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**: 金额100元，红包个数5个，祝福语&quot;新年快乐&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入聊天窗口点击&quot;+&quot;→&quot;红包&quot;
2. 选择&quot;普通红包&quot;
3. 输入金额100元
4. 设置红包个数5
5. 输入祝福语&quot;新年快乐&quot;
6. 点击&quot;塞钱进红包&quot;
7. 完成支付密码验证" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 红包发送成功显示在聊天窗口
2. 钱包余额减少100元
3. 触发TRACK_REDPACKET_SEND埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: 功能测试,埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-002 零钱不足异常处理" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 余额不足时发送红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 钱包余额10元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试数据**: 金额100元" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 尝试发送100元红包
2. 查看系统提示" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 弹出&quot;余额不足&quot;提示框
2. 触发TRACK_REDPACKET_INSUFFICIENT_BALANCE埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: 异常测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-010 正常抢红包流程" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 群组内抢红包" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 收到未领取的群红包
2. 网络连接正常" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 点击聊天窗口中的红包
2. 点击&quot;开&quot;按钮
3. 查看领取结果" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示红包金额动画
2. 钱包余额增加对应金额
3. 聊天窗口显示领取记录
4. 触发TRACK_REDPACKET_OPEN埋点" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: 功能测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="RED-020 多语言环境下记录显示" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 切换语言后查看红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. 有历史收发记录
2. 切换至英语环境" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入&quot;我&quot;→&quot;钱包&quot;→&quot;红包记录&quot;
2. 查看记录列表" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 所有金额显示为&quot;¥100&quot;格式
2. 时间显示为&quot;MM/DD/YYYY&quot;格式
3. 状态标签显示英文&quot;Received/Sent&quot;" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: I18N测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="I18N-001 阿拉伯语RTL布局" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 阿拉伯语界面适配" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 系统语言设为阿拉伯语" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 打开红包发送页面
2. 检查UI元素排列" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 所有文本右对齐
2. 输入框光标从右侧开始
3. 按钮位置镜像翻转" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: I18N测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="TRACK-001 红包详情页曝光埋点" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 查看已领取红包详情" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 有已领取的红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 进入红包记录
2. 点击某条记录
3. 检查埋点日志" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 触发redpacket_detail_view事件
2. 包含参数: redpacket_id, sender_id, amount
3. 时间戳精度到毫秒" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 中" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: 埋点测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="AB-001 新红包皮肤实验组" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 实验组用户查看新皮肤" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**: 用户被分到实验组A" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 发送红包
2. 查看红包外观" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 显示春节主题皮肤
2. 触发ab_exposure埋点(experiment_id=2024_redpacket_skin)" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 低" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: AB测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
    <node TEXT="VERSION-001 覆盖安装数据迁移" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="测试场景**: 从v8.0.25升级到v8.0.26" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="前置条件**:
1. v8.0.25有10条红包记录
2. 执行覆盖安装" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试步骤**:
1. 安装新版本
2. 启动后检查红包记录" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="预期结果**:
1. 所有历史记录完整保留
2. 未领取红包仍可正常打开" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="重要程度**: 高" COLOR="#4682B4" STYLE="bullet"/>
      <node TEXT="测试类型**: 版本测试
" COLOR="#4682B4" STYLE="bullet"/>
    </node>
  </node>
</map>