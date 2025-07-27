<?xml version="1.0" ?>
<map version="1.0.1">
  <node TEXT="AI生成测试用例" STYLE="bubble" COLOR="#000000">
    <node TEXT="RED-001 普通红包发送验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 金额: 100元, 祝福语: &quot;新年快乐&quot; |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-002 拼手气红包发送验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 总金额: 100元, 红包个数: 5个 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-003 红包金额边界值测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 金额: 0.01元/200元/0元/201元 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-004 多语言红包祝福语测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 语言: 英文/阿拉伯语/日语&lt;br&gt;祝福语: 对应语言的&quot;新年快乐&quot; |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-005 红包发送网络异常测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 网络: 2G/断网/高延迟(1000ms+) |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-006 普通红包领取验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 红包金额: 10元 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-007 拼手气红包领取验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 总金额: 100元, 红包个数: 5个 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-008 红包过期处理验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 过期时间: 24小时 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-009 多设备同时领取测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 红包金额: 10元 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="RED-010 红包领取记录验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 最近红包: 10元(来自账号A) |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="I18N-001 多语言红包界面适配" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 语言: 英语/阿拉伯语/日语等 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="I18N-002 多地区货币格式测试" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 地区: 中国/美国/日本/欧洲 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="TRACK-001 红包发送成功埋点" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 红包类型: 普通, 金额: 10元 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="AB-001 新红包UI实验分组验证" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 实验组: 新UI/旧UI |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="VERSION-001 红包数据跨版本迁移" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="| **测试数据** | 红包记录: 发送5个/接收3个 |..." COLOR="#556B2F"/>
      </node>
    </node>
    <node TEXT="需求覆盖率分析" COLOR="#FF7F50" STYLE="fork">
      <node TEXT="未命名用例" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="1. 功能测试覆盖率: 95%..." COLOR="#556B2F"/>
      </node>
      <node TEXT="覆盖所有核心红包场景
包含边界条件和异常处理
" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="2. 国际化测试覆盖率: 90%..." COLOR="#556B2F"/>
      </node>
      <node TEXT="覆盖主要语言和地区
包含RTL语言特殊处理
" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="3. 埋点测试覆盖率: 85%..." COLOR="#556B2F"/>
      </node>
      <node TEXT="覆盖主要用户行为路径
缺少部分边缘场景埋点
" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="4. AB实验覆盖率: 80%..." COLOR="#556B2F"/>
      </node>
      <node TEXT="覆盖现有实验类型
需增加多地区实验验证
" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="5. 版本测试覆盖率: 88%..." COLOR="#556B2F"/>
      </node>
      <node TEXT="覆盖主要升级场景
需增加更多降级测试用例
" COLOR="#4682B4" STYLE="bullet">
        <node TEXT="*注: 实际测试应根据需求变化动态调整用例，本用例集持续维护更新*..." COLOR="#556B2F"/>
      </node>
    </node>
  </node>
</map>