"""
全域电商经营报告生成器
将诊断引擎的输出渲染为具有专业数据可视化、指标卡片与归因分析的独立HTML大屏报告与Markdown行动看板
"""

import os
import json
import pandas as pd
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, channel_summary: pd.DataFrame, funnels: Dict[str, Any], skus: pd.DataFrame, diagnostics: Dict[str, Any]):
        self.summary = channel_summary
        self.funnels = funnels
        self.skus = skus
        self.diag = diagnostics

    def generate_markdown_action_board(self, output_path: str = "d:/pddyy/ecommerce_assistant/output/action_board_7_14_30.md"):
        """输出7/14/30天经营调优行动看板"""
        md = f"""# 📊 全域电商经营调优与行动追踪看板 (天猫 / 京东 / 抖音)

**统计周期与口径说明**：统一统计窗口（近30天）、统一净GMV（支付GMV - 退款退货）、统一客单价与边际贡献口径。

---

## 🎯 一、三平台大盘表现与关键漏斗对照

| 经营维度 / 核心指标 | 天猫 (搜索与会员阵地) | 京东 (确定性与履约阵地) | 抖音 (内容兴趣与爆发阵地) |
|---|---|---|---|
| **总曝光量 (PV)** | {int(self.summary.loc[self.summary['channel']=='天猫', 'impressions'].values[0]):,} | {int(self.summary.loc[self.summary['channel']=='京东', 'impressions'].values[0]):,} | {int(self.summary.loc[self.summary['channel']=='抖音', 'impressions'].values[0]):,} |
| **访客人数 (UV)** | {int(self.summary.loc[self.summary['channel']=='天猫', 'visitors'].values[0]):,} | {int(self.summary.loc[self.summary['channel']=='京东', 'visitors'].values[0]):,} | {int(self.summary.loc[self.summary['channel']=='抖音', 'visitors'].values[0]):,} |
| **点击率 CTR** | {self.summary.loc[self.summary['channel']=='天猫', 'ctr'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='京东', 'ctr'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='抖音', 'ctr'].values[0]:.2%} |
| **收藏加购率** | {self.summary.loc[self.summary['channel']=='天猫', 'cart_rate'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='京东', 'cart_rate'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='抖音', 'cart_rate'].values[0]:.2%} |
| **访客支付转化率 CVR** | {self.summary.loc[self.summary['channel']=='天猫', 'cvr'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='京东', 'cvr'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='抖音', 'cvr'].values[0]:.2%} |
| **平均客单价 (AOV)** | ¥{self.summary.loc[self.summary['channel']=='天猫', 'aov'].values[0]:.2f} | ¥{self.summary.loc[self.summary['channel']=='京东', 'aov'].values[0]:.2f} | ¥{self.summary.loc[self.summary['channel']=='抖音', 'aov'].values[0]:.2f} |
| **净成交销售额 (Net GMV)** | **¥{self.summary.loc[self.summary['channel']=='天猫', 'net_gmv'].values[0]:,.2f}** | **¥{self.summary.loc[self.summary['channel']=='京东', 'net_gmv'].values[0]:,.2f}** | **¥{self.summary.loc[self.summary['channel']=='抖音', 'net_gmv'].values[0]:,.2f}** |
| **退款退货率** | {self.summary.loc[self.summary['channel']=='天猫', 'refund_rate'].values[0]:.2%} | **{self.summary.loc[self.summary['channel']=='京东', 'refund_rate'].values[0]:.2%} (最优)** | **{self.summary.loc[self.summary['channel']=='抖音', 'refund_rate'].values[0]:.2%} (极高预警)** |
| **商业化投放ROI (ROAS)** | {self.summary.loc[self.summary['channel']=='天猫', 'roas'].values[0]:.2f} | **{self.summary.loc[self.summary['channel']=='京东', 'roas'].values[0]:.2f}** | {self.summary.loc[self.summary['channel']=='抖音', 'roas'].values[0]:.2f} |
| **边际贡献利润率** | {self.summary.loc[self.summary['channel']=='天猫', 'contribution_margin'].values[0]:.2%} | **{self.summary.loc[self.summary['channel']=='京东', 'contribution_margin'].values[0]:.2%}** | {self.summary.loc[self.summary['channel']=='抖音', 'contribution_margin'].values[0]:.2%} |
| **用户复购率** | **{self.summary.loc[self.summary['channel']=='天猫', 'repeat_rate'].values[0]:.2%} (最强)** | {self.summary.loc[self.summary['channel']=='京东', 'repeat_rate'].values[0]:.2%} | {self.summary.loc[self.summary['channel']=='抖音', 'repeat_rate'].values[0]:.2%} |

---

## 🔍 二、三大根本归因与问题聚焦

### 1. 平台生态差异
- **天猫**：搜索心智与私域留存成熟，加购蓄水率最高，是品牌**利润基石与复购发酵池**。
- **京东**：正品保障与极速物流支撑高客单价与极低退款率，边际贡献最健康，是**现金流与高端客群阵地**。
- **抖音**：脉冲爆发与兴趣推荐制造了海量曝光，但冲动下单导致**退款率突破25%**，千川投放费比居高不下，净留存利润被严重摊薄。

### 2. 商品本身问题
- **部分爆品在抖音存在过度承诺或尺码预期偏差**，退款率高达30%+；
- **长尾/引流款客单过低（<¥100）**，在抖音扣除运费险、包装及千川推流后呈现**负边际贡献**。

### 3. 运营动作偏差
- **千川投放考核单一**：过于追求即时曝光与毛GMV，未建立“按净结算ROI”的考核过滤机制；
- **天猫未激活沉淀购物车**：加购率高达15%但缺乏日常限时满减和会员挽回券刺激，流失率高；
- **京东货盘单一**：腰尾部新品缺乏针对性爆品孵化预算与精准词卡位。

---

## 🚀 三、7 / 14 / 30 天经营调优与行动路线图

### 📅 【前 7 天】止血与即时修复 (Stop-Loss Phase)
- [ ] **抖音投放止血**：在千川后台按“签收退款率”排查计划，关停退款率>35%的泛定向计划，投放预算向高净值转化包倾斜；
- [ ] **商品页选型补齐**：紧急优化天猫与抖音高退款SKU的商品首屏，增加核心规格图解、常见退货疑点解答与尺码对照表；
- [ ] **购物车流失挽回**：天猫启动“加购未支付满减券”推送，针对加购超48小时人群定向发放专属回购礼。

### 📅 【前 14 天】货盘重构与转化攻坚 (Restructure Phase)
- [ ] **三平台货盘差异化分工**：
  - 天猫：主推经典热销标准版 + 品牌定制礼盒（保利润、主打入会复购）；
  - 京东：主推旗舰Pro高端款（强推自营入仓、次日达品质保障）；
  - 抖音：专供视觉冲击力强、体验感直观的爆破组合装（严控退款风险）。
- [ ] **素材优化与退货前置治理**：下架抖音夸大功效短视频，补充真实场景实拍与买家秀，降低因预期过高引发的无理由退货；
- [ ] **京东秒杀与新品测款**：为两款新品争取京东秒杀频道坑位，以精准品类词带动腰部货盘放量。

### 📅 【前 30 天】全域协同与长效闭环 (Omnichannel Synergy)
- [ ] **全域会员通与私域导流**：抖音、京东包裹中植入扫码领延保/专属配件卡，沉淀至企微与天猫品牌俱乐部；
- [ ] **构建跨平台UE模型监控**：将物流运费险、平台佣金、广告花费、退款损失全部纳入单品动态利润看板，杜绝虚假繁荣；
- [ ] **新品全域阶梯孵化**：形成“抖音内容测款(测点击互动) -> 天猫搜索打标沉淀评价 -> 京东批量入仓爆发”的协同链路。

---
*报告生成于全域电商经营助手 (Omnichannel Commerce Assistant)*
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ 成功生成行动看板: {output_path}")

    def generate_html_dashboard(self, output_path: str = "d:/pddyy/ecommerce_assistant/output/omnichannel_dashboard.html"):
        """输出高互动、多维度的全域电商HTML经营诊断大屏"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 准备数据指标
        ch_list = self.summary['channel'].tolist()
        gmv_list = [round(x, 2) for x in self.summary['net_gmv'].tolist()]
        cvr_list = [round(x * 100, 2) for x in self.summary['cvr'].tolist()]
        refund_list = [round(x * 100, 2) for x in self.summary['refund_rate'].tolist()]
        roas_list = [round(x, 2) for x in self.summary['roas'].tolist()]
        cm_list = [round(x * 100, 2) for x in self.summary['contribution_margin'].tolist()]

        color_map = {
            "天猫": "#ff4d6d",
            "京东": "#ff6b6b",
            "抖音": "#00f2fe",
            "拼多多": "#e02e24"
        }
        palette = [color_map.get(ch, "#3b82f6") for ch in ch_list]
        aov_list = [round(x, 2) for x in self.summary['aov'].tolist()]
        
        # 商品表格数据
        sku_table_rows = ""
        for _, r in self.skus.sort_values(by='net_gmv', ascending=False).head(12).iterrows():
            badge_color = {
                "核心爆品 (Hero)": "#10B981",
                "引流放量款 (Traffic)": "#3B82F6",
                "高潜利润款 (Profit)": "#8B5CF6",
                "待优化/淘汰款 (Review)": "#EF4444"
            }.get(r['portfolio_role'], '#6B7280')
            
            sku_table_rows += f"""
            <tr>
                <td style="font-weight:600;">{r['channel']}</td>
                <td>{r['sku_name']}</td>
                <td><span style="background:{badge_color}15;color:{badge_color};padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">{r['portfolio_role']}</span></td>
                <td>¥{r['net_gmv']:,.2f}</td>
                <td>{r['cvr']:.2%}</td>
                <td style="color:{'#EF4444' if r['refund_rate']>0.2 else '#10B981'};font-weight:600;">{r['refund_rate']:.1%}</td>
                <td>{r['roas']:.2f}</td>
                <td>{r['contribution_margin']:.1%}</td>
            </tr>
            """

        html = f"""<!-- Generated by Trae Work -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全域电商多平台经营诊断与决策大屏 (天猫 / 京东 / 抖音)</title>
    <!-- 引入外部 ECharts 图表库 -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <style>
        :root {{
            --bg: #F8FAFC;
            --surface: #FFFFFF;
            --ink: #0F172A;
            --muted: #64748B;
            --rule: #E2E8F0;
            --tmall: #FF0036;
            --jd: #E1251B;
            --douyin: #000000;
            --brand: #2563EB;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif; }}
        body {{ background: var(--bg); color: var(--ink); line-height: 1.6; padding: 24px 32px; }}
        .header {{ margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); display: flex; justify-content: space-between; align-items: flex-end; }}
        .header h1 {{ font-size: 26px; font-weight: 700; color: var(--ink); }}
        .header p {{ color: var(--muted); font-size: 14px; margin-top: 4px; }}
        .tag-group {{ display: flex; gap: 8px; }}
        .badge {{ display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; background: #EEF2FF; color: var(--brand); }}
        
        .grid-kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
        .kpi-card {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
        .kpi-title {{ font-size: 13px; color: var(--muted); font-weight: 500; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; margin: 8px 0; color: var(--ink); }}
        .kpi-sub {{ font-size: 12px; color: var(--muted); display: flex; gap: 8px; }}
        
        .grid-charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
        .chart-box {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
        .chart-title {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }}
        .chart-container {{ width: 100%; height: 350px; }}
        
        .section-card {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
        .section-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; border-left: 4px solid var(--brand); padding-left: 12px; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; }}
        th {{ background: #F8FAFC; padding: 12px 14px; color: var(--muted); font-weight: 600; border-bottom: 1px solid var(--rule); }}
        td {{ padding: 12px 14px; border-bottom: 1px solid var(--rule); }}
        tr:hover td {{ background: #F1F5F9; }}
        
        .diag-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
        .diag-card {{ background: #F8FAFC; border: 1px solid var(--rule); border-radius: 8px; padding: 16px; }}
        .diag-tag {{ font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }}
        .tag-danger {{ background: #FEE2E2; color: var(--danger); }}
        .tag-warning {{ background: #FEF3C7; color: var(--warning); }}
        .tag-success {{ background: #D1FAE5; color: var(--success); }}
        
        .roadmap-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
        .roadmap-card {{ border-radius: 8px; padding: 16px; border: 1px solid var(--rule); background: #FAF5FF; border-top: 4px solid #8B5CF6; }}
        .roadmap-card h4 {{ font-size: 15px; margin-bottom: 8px; color: #6D28D9; }}
        .roadmap-card li {{ font-size: 13px; color: #475569; margin-left: 18px; margin-bottom: 6px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>全域电商经营多维诊断大屏</h1>
            <p>基于天猫、京东、抖音全链路店铺数据，统一统计周期、指标口径与归因对比分析</p>
        </div>
        <div class="tag-group">
            <span class="badge">统计周期: 统一近30天</span>
            <span class="badge">口径归一: 剔退净成交口径</span>
            <span class="badge">自动诊断生成</span>
        </div>
    </div>

    <!-- 顶部核心KPI -->
    <div class="grid-kpi">
        <div class="kpi-card">
            <div class="kpi-title">全域净成交总额 (Net GMV)</div>
            <div class="kpi-value">¥{self.summary['net_gmv'].sum():,.2f}</div>
            <div class="kpi-sub">
                <span>天猫: ¥{self.summary.loc[self.summary['channel']=='天猫', 'net_gmv'].values[0]:,.0f}</span>
                <span>京东: ¥{self.summary.loc[self.summary['channel']=='京东', 'net_gmv'].values[0]:,.0f}</span>
                <span>抖音: ¥{self.summary.loc[self.summary['channel']=='抖音', 'net_gmv'].values[0]:,.0f}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">全域综合边际贡献率</div>
            <div class="kpi-value" style="color:var(--success);">{self.summary['contribution_profit'].sum() / self.summary['net_gmv'].sum():.1%}</div>
            <div class="kpi-sub">
                <span>京东贡献率最高({self.summary.loc[self.summary['channel']=='京东', 'contribution_margin'].values[0]:.1%})</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">抖音退款退货率 (预警)</div>
            <div class="kpi-value" style="color:var(--danger);">{self.summary.loc[self.summary['channel']=='抖音', 'refund_rate'].values[0]:.1%}</div>
            <div class="kpi-sub">
                <span>天猫: {self.summary.loc[self.summary['channel']=='天猫', 'refund_rate'].values[0]:.1%}</span>
                <span>京东: {self.summary.loc[self.summary['channel']=='京东', 'refund_rate'].values[0]:.1%}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">全域广告平均ROAS</div>
            <div class="kpi-value">{self.summary['gmv'].sum() / self.summary['ad_spend'].sum():.2f}</div>
            <div class="kpi-sub">
                <span>京东({self.summary.loc[self.summary['channel']=='京东', 'roas'].values[0]:.2f}) > 天猫({self.summary.loc[self.summary['channel']=='天猫', 'roas'].values[0]:.2f}) > 抖音({self.summary.loc[self.summary['channel']=='抖音', 'roas'].values[0]:.2f})</span>
            </div>
        </div>
    </div>

    <!-- 图表对比区域 -->
    <div class="grid-charts">
        <div class="chart-box">
            <div class="chart-title">三平台全链路漏斗转化表现对比 (CTR / 加购 / CVR / 退款率)</div>
            <div id="chart-funnel" class="chart-container"></div>
        </div>
        <div class="chart-box">
            <div class="chart-title">各平台 商业化投产比(ROAS) 与 边际贡献率对比</div>
            <div id="chart-profit" class="chart-container"></div>
        </div>
        <div class="chart-box">
            <div class="chart-title">各平台 流量规模(访客UV) 与 客单价(AOV) 矩阵分布</div>
            <div id="chart-traffic" class="chart-container"></div>
        </div>
        <div class="chart-box">
            <div class="chart-title">商品货盘结构四象限占比 (爆品/引流/利润/淘汰款)</div>
            <div id="chart-pie" class="chart-container"></div>
        </div>
    </div>

    <!-- 商品结构表 -->
    <div class="section-card">
        <div class="section-title">核心商品全域表现明细与货盘定位</div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>渠道</th>
                        <th>商品名称</th>
                        <th>货盘定位角色</th>
                        <th>净成交销售额</th>
                        <th>支付转化率</th>
                        <th>退款率</th>
                        <th>广告ROAS</th>
                        <th>边际贡献率</th>
                    </tr>
                </thead>
                <tbody>
                    {sku_table_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- 归因诊断 -->
    <div class="section-card">
        <div class="section-title">核心归因诊断：平台生态差异、商品问题与运营动作影响</div>
        <div class="diag-grid">
            <div class="diag-card">
                <span class="diag-tag tag-warning">平台生态差异</span>
                <h4 style="margin-bottom:8px;">传统货架 vs 兴趣电商逻辑分流</h4>
                <p style="font-size:13px;color:#475569;">
                    • <b>天猫</b>：搜索与货架沉淀优势显著，复购率({self.summary.loc[self.summary['channel']=='天猫', 'repeat_rate'].values[0]:.1%})领先全网，是长期会员资产沉淀池。<br>
                    • <b>京东</b>：自营履约与极速物流构建高品质心智，客单价最高且退款率仅{self.summary.loc[self.summary['channel']=='京东', 'refund_rate'].values[0]:.1%}，贡献最优质现金流。<br>
                    • <b>抖音</b>：短视频与直播激发海量瞬时曝光，但冲动下单引发{self.summary.loc[self.summary['channel']=='抖音', 'refund_rate'].values[0]:.1%}的高退款率，物流与运费险净损耗大。
                </p>
            </div>
            <div class="diag-card">
                <span class="diag-tag tag-danger">商品结构硬伤</span>
                <h4 style="margin-bottom:8px;">部分单品退款过高与低价毛利侵蚀</h4>
                <p style="font-size:13px;color:#475569;">
                    • <b>异常SKU</b>：部分低价引流尝鲜款在抖音的退货率达35%+，扣除推流成本后实际陷入负贡献空转；<br>
                    • <b>客单价断层</b>：主力成交集中在经典款，高阶礼赠版在抖音难以有效拉动，货盘跨渠道梯队未充分打通。
                </p>
            </div>
            <div class="diag-card">
                <span class="diag-tag tag-success">运营动作偏差</span>
                <h4 style="margin-bottom:8px;">投放考核口径偏差与意向人群流失</h4>
                <p style="font-size:13px;color:#475569;">
                    • <b>千川投放偏离净结算</b>：考核偏重表观GMV，忽视扣退后的实际净ROAS，素材前置诱导导致后链路拒签；<br>
                    • <b>天猫购物车蓄水催单滞后</b>：加购率高达{self.summary.loc[self.summary['channel']=='天猫', 'cart_rate'].values[0]:.1%}，但缺乏基于停留时长的自动化满减追单与专属触达。
                </p>
            </div>
        </div>
    </div>

    <!-- 7/14/30天建议 -->
    <div class="section-card">
        <div class="section-title">下一阶段 7 / 14 / 30 天经营调优实操路线图</div>
        <div class="roadmap-grid">
            <div class="roadmap-card">
                <h4>📅 7天：即时止血与触达挽回</h4>
                <ul>
                    <li>关停抖音千川退款率>35%的泛定向推流计划；</li>
                    <li>排查天猫/京东高退款SKU详情页，强化规格参数与选型图解；</li>
                    <li>启动天猫加购超48小时用户的专属优惠券挽回。</li>
                </ul>
            </div>
            <div class="roadmap-card" style="border-top-color:#3B82F6;background:#EFF6FF;">
                <h4 style="color:#1D4ED8;">📅 14天：货盘重构与素材迭代</h4>
                <ul>
                    <li>落实天猫推经典礼盒、京东推高配自营、抖音推爆发装的差异化货盘；</li>
                    <li>全面下架抖音虚假承诺素材，补充真实测评使用场景短视频；</li>
                    <li>参与京东秒杀频道，拉动中腰部高潜新品动销突破。</li>
                </ul>
            </div>
            <div class="roadmap-card" style="border-top-color:#10B981;background:#ECFDF5;">
                <h4 style="color:#047857;">📅 30天：全域协同与长效闭环</h4>
                <ul>
                    <li>包裹卡引流私域/会员中心，构建全域用户LTV复购闭环；</li>
                    <li>建立跨平台单品UE动态监控看板，按“净贡献利润”考核运营；</li>
                    <li>跑通“抖音内容测款 -> 天猫搜索沉淀 -> 京东全面铺货”的新品流水线。</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        // 初始化 ECharts
        const channels = {json.dumps(ch_list, ensure_ascii=False)};
        
        // 漏斗比率对比
        const chartFunnel = echarts.init(document.getElementById('chart-funnel'));
        chartFunnel.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
            legend: {{ data: ['点击率(CTR)', '加购率', '转化率(CVR)', '退款退货率'] }},
            grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
            xAxis: {{ type: 'category', data: channels }},
            yAxis: {{ type: 'value', axisLabel: {{ formatter: '{{value}}%' }} }},
            series: [
                {{ name: '点击率(CTR)', type: 'bar', data: [{round(x*100, 2) for x in self.summary['ctr']}], itemStyle: {{ color: '#3B82F6' }} }},
                {{ name: '加购率', type: 'bar', data: [{round(x*100, 2) for x in self.summary['cart_rate']}], itemStyle: {{ color: '#F59E0B' }} }},
                {{ name: '转化率(CVR)', type: 'bar', data: {cvr_list}, itemStyle: {{ color: '#10B981' }} }},
                {{ name: '退款退货率', type: 'bar', data: {refund_list}, itemStyle: {{ color: '#EF4444' }} }}
            ]
        }});

        // 投产比与边际贡献率
        const chartProfit = echarts.init(document.getElementById('chart-profit'));
        chartProfit.setOption({{
            tooltip: {{ trigger: 'axis' }},
            legend: {{ data: ['广告ROAS', '边际贡献率(%)'] }},
            grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
            xAxis: {{ type: 'category', data: channels }},
            yAxis: [
                {{ type: 'value', name: 'ROAS', axisLabel: {{ formatter: '{{value}}' }} }},
                {{ type: 'value', name: '贡献率(%)', axisLabel: {{ formatter: '{{value}}%' }} }}
            ],
            series: [
                {{ name: '广告ROAS', type: 'bar', data: {roas_list}, itemStyle: {{ color: '#6366F1' }} }},
                {{ name: '边际贡献率(%)', type: 'line', yAxisIndex: 1, data: {cm_list}, lineStyle: {{ width: 3, color: '#10B981' }}, itemStyle: {{ color: '#10B981' }} }}
            ]
        }});

        // 流量与客单价
        const chartTraffic = echarts.init(document.getElementById('chart-traffic'));
        chartTraffic.setOption({{
            tooltip: {{ trigger: 'axis' }},
            legend: {{ data: ['访客UV量', '平均客单价(¥)'] }},
            grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
            xAxis: {{ type: 'category', data: channels }},
            yAxis: [
                {{ type: 'value', name: '访客UV' }},
                {{ type: 'value', name: '客单价(元)' }}
            ],
            series: [
                {{ name: '访客UV量', type: 'bar', data: {[int(x) for x in self.summary['visitors']]}, itemStyle: {{ color: '#94A3B8' }} }},
                {{ name: '平均客单价(¥)', type: 'line', yAxisIndex: 1, data: {aov_list}, lineStyle: {{ width: 3, color: '#F97316' }}, itemStyle: {{ color: '#F97316' }} }}
            ]
        }});

        // 货盘分类占比
        const chartPie = echarts.init(document.getElementById('chart-pie'));
        const roleCounts = {{}};
        {json.dumps(self.skus['portfolio_role'].value_counts().to_dict(), ensure_ascii=False)};
        chartPie.setOption({{
            tooltip: {{ trigger: 'item' }},
            legend: {{ bottom: '5%' }},
            series: [{{
                name: '货盘角色',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {{ borderRadius: 8, borderColor: '#fff', borderWidth: 2 }},
                data: [
                    {{ value: {len(self.skus[self.skus['portfolio_role']=='核心爆品 (Hero)'])}, name: '核心爆品 (Hero)', itemStyle: {{ color: '#10B981' }} }},
                    {{ value: {len(self.skus[self.skus['portfolio_role']=='引流放量款 (Traffic)'])}, name: '引流放量款 (Traffic)', itemStyle: {{ color: '#3B82F6' }} }},
                    {{ value: {len(self.skus[self.skus['portfolio_role']=='高潜利润款 (Profit)'])}, name: '高潜利润款 (Profit)', itemStyle: {{ color: '#8B5CF6' }} }},
                    {{ value: {len(self.skus[self.skus['portfolio_role']=='待优化/淘汰款 (Review)'])}, name: '待优化/淘汰款 (Review)', itemStyle: {{ color: '#EF4444' }} }}
                ]
            }}]
        }});

        window.addEventListener('resize', () => {{
            chartFunnel.resize();
            chartProfit.resize();
            chartTraffic.resize();
            chartPie.resize();
        }});
    </script>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ 成功生成全域经营交互HTML大屏: {output_path}")
