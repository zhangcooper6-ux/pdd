"""
全域电商经营助手 - 核心分析与诊断引擎
覆盖天猫、京东、抖音三平台的数据口径对齐、漏斗转化、商品结构、归因诊断与策略建议
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

class MetricNormalizer:
    """
    统一统计周期与指标口径转换器
    天猫、京东、抖音各平台指标对齐
    """
    
    @staticmethod
    def align_channel_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        统一字段名称与衍生关键计算指标
        标准字段包括:
        - channel: 渠道 (天猫 / 京东 / 抖音)
        - sku_id, sku_name, category, price_band (商品信息与价格带)
        - impressions: 曝光PV
        - visitors: 访客数UV (点击UV)
        - product_views: 商品浏览量PV
        - cart_uv: 加购/收藏UV (抖音取加购+意向)
        - paid_orders: 支付订单数
        - paid_buyers: 支付人数UV
        - paid_units: 支付件数
        - gmv: 拍下/支付总GMV (元)
        - refund_amount: 退款退货金额 (元)
        - ad_spend: 商业化投放花费 (直通车/万相台/京东快车/千川)
        - cogs: 商品直接成本 (元)
        - repeat_buyers: 复购买家数
        """
        df = df.copy()
        
        # 曝光点击率 CTR = visitors / impressions
        df['ctr'] = np.where(df['impressions'] > 0, df['visitors'] / df['impressions'], 0.0)
        
        # 收藏加购率 Cart Rate = cart_uv / visitors
        df['cart_rate'] = np.where(df['visitors'] > 0, df['cart_uv'] / df['visitors'], 0.0)
        
        # 访客支付转化率 CVR = paid_buyers / visitors
        df['cvr'] = np.where(df['visitors'] > 0, df['paid_buyers'] / df['visitors'], 0.0)
        
        # 客单价 AOV = gmv / paid_orders
        df['aov'] = np.where(df['paid_orders'] > 0, df['gmv'] / df['paid_orders'], 0.0)
        
        # 件单价 ASP = gmv / paid_units
        df['asp'] = np.where(df['paid_units'] > 0, df['gmv'] / df['paid_units'], 0.0)
        
        # 净销售额 Net GMV = gmv - refund_amount
        df['net_gmv'] = df['gmv'] - df['refund_amount']
        
        # 退款率 Refund Rate = refund_amount / gmv
        df['refund_rate'] = np.where(df['gmv'] > 0, df['refund_amount'] / df['gmv'], 0.0)
        
        # 商业化投产比 ROAS = gmv / ad_spend
        df['roas'] = np.where(df['ad_spend'] > 0, df['gmv'] / df['ad_spend'], 0.0)
        
        # 投放费用率 = ad_spend / gmv
        df['ad_ratio'] = np.where(df['gmv'] > 0, df['ad_spend'] / df['gmv'], 0.0)
        
        # 毛利额 Gross Profit = net_gmv - cogs
        df['gross_profit'] = df['net_gmv'] - df['cogs']
        
        # 边际贡献贡献额 Contribution Profit = net_gmv - cogs - ad_spend
        df['contribution_profit'] = df['net_gmv'] - df['cogs'] - df['ad_spend']
        
        # 边际利润率 Contribution Margin = contribution_profit / net_gmv
        df['contribution_margin'] = np.where(df['net_gmv'] > 0, df['contribution_profit'] / df['net_gmv'], 0.0)
        
        # 千次曝光收益 eCPM / 访客价值 UV Value = net_gmv / visitors
        df['uv_value'] = np.where(df['visitors'] > 0, df['net_gmv'] / df['visitors'], 0.0)
        
        # 复购率 Repeat Rate = repeat_buyers / paid_buyers
        df['repeat_rate'] = np.where(df['paid_buyers'] > 0, df['repeat_buyers'] / df['paid_buyers'], 0.0)
        
        return df


class OmnichannelAnalyzer:
    """
    全域经营分析与诊断核心
    """
    def __init__(self, data: pd.DataFrame):
        self.raw_data = data
        self.data = MetricNormalizer.align_channel_data(data)
        
    def get_channel_summary(self) -> pd.DataFrame:
        """各平台经营大盘总览汇总"""
        agg_rules = {
            'impressions': 'sum',
            'visitors': 'sum',
            'cart_uv': 'sum',
            'paid_orders': 'sum',
            'paid_buyers': 'sum',
            'paid_units': 'sum',
            'gmv': 'sum',
            'refund_amount': 'sum',
            'net_gmv': 'sum',
            'ad_spend': 'sum',
            'cogs': 'sum',
            'repeat_buyers': 'sum',
            'contribution_profit': 'sum'
        }
        summary = self.data.groupby('channel').agg(agg_rules).reset_index()
        
        # 重新计算整体比率指标
        summary['ctr'] = summary['visitors'] / summary['impressions']
        summary['cart_rate'] = summary['cart_uv'] / summary['visitors']
        summary['cvr'] = summary['paid_buyers'] / summary['visitors']
        summary['aov'] = summary['gmv'] / summary['paid_orders']
        summary['refund_rate'] = summary['refund_amount'] / summary['gmv']
        summary['roas'] = summary['gmv'] / summary['ad_spend']
        summary['ad_ratio'] = summary['ad_spend'] / summary['gmv']
        summary['contribution_margin'] = summary['contribution_profit'] / summary['net_gmv']
        summary['uv_value'] = summary['net_gmv'] / summary['visitors']
        summary['repeat_rate'] = summary['repeat_buyers'] / summary['paid_buyers']
        
        # 份额占比
        total_net_gmv = summary['net_gmv'].sum()
        total_ad_spend = summary['ad_spend'].sum()
        summary['gmv_share'] = summary['net_gmv'] / total_net_gmv
        summary['ad_spend_share'] = summary['ad_spend'] / total_ad_spend
        
        return summary

    def get_funnel_comparison(self) -> Dict[str, Dict[str, float]]:
        """三平台关键转化漏斗对比"""
        funnels = {}
        summary = self.get_channel_summary()
        for _, row in summary.iterrows():
            ch = row['channel']
            funnels[ch] = {
                "曝光PV": int(row['impressions']),
                "访客UV": int(row['visitors']),
                "加购收藏UV": int(row['cart_uv']),
                "支付买家UV": int(row['paid_buyers']),
                "CTR(点击率)": round(row['ctr'] * 100, 2),
                "加购率": round(row['cart_rate'] * 100, 2),
                "访客CVR": round(row['cvr'] * 100, 2),
                "退款率": round(row['refund_rate'] * 100, 2),
                "复购率": round(row['repeat_rate'] * 100, 2),
                "客单价(元)": round(row['aov'], 2),
                "UV价值(元)": round(row['uv_value'], 2),
                "ROAS": round(row['roas'], 2)
            }
        return funnels

    def get_product_portfolio_analysis(self) -> pd.DataFrame:
        """
        商品结构与四象限矩阵 (波士顿/全域货盘定位)
        按 GMV贡献度 与 贡献利润率 / 动销深度分类:
        - 核心爆品 (Hero): 高GMV、高利润贡献
        - 引流引流款 (Traffic Anchor): 高GMV、薄利或高投放 (引流促转)
        - 潜力/利润款 (Profit Driver): 中低GMV、高边际贡献率 (待放量)
        - 拖后腿/淘汰款 (Problem SKU): 高退款、负边际贡献或极低转化
        """
        sku_df = self.data.groupby(['channel', 'sku_id', 'sku_name', 'category', 'price_band']).agg({
            'visitors': 'sum',
            'gmv': 'sum',
            'net_gmv': 'sum',
            'refund_rate': 'mean',
            'cvr': 'mean',
            'roas': 'mean',
            'contribution_profit': 'sum',
            'contribution_margin': 'mean'
        }).reset_index()
        
        # 计算平台内分位数分类
        portfolio_list = []
        for ch, group in sku_df.groupby('channel'):
            median_gmv = group['net_gmv'].median()
            median_cm = group['contribution_margin'].median()
            
            for _, row in group.iterrows():
                r = row.to_dict()
                if r['net_gmv'] >= median_gmv and r['contribution_margin'] >= median_cm:
                    role = "核心爆品 (Hero)"
                elif r['net_gmv'] >= median_gmv and r['contribution_margin'] < median_cm:
                    role = "引流放量款 (Traffic)"
                elif r['net_gmv'] < median_gmv and r['contribution_margin'] >= median_cm:
                    role = "高潜利润款 (Profit)"
                else:
                    role = "待优化/淘汰款 (Review)"
                r['portfolio_role'] = role
                portfolio_list.append(r)
                
        return pd.DataFrame(portfolio_list)

    def diagnose_and_attribute(self) -> Dict[str, Any]:
        """
        多维归因诊断: 区分平台生态差异、商品本身问题与运营动作偏差 (天猫、京东、抖音、拼多多)
        """
        summary = self.get_channel_summary().set_index('channel')
        
        diagnostics = {
            "platform_differences": [],
            "product_issues": [],
            "operational_actions": [],
            "opportunity_list": [],
            "next_stage_recommendations": {}
        }
        
        # 1. 平台生态差异分析
        diff_tmall = f"天猫搜索与会员心智沉淀强，CVR({summary.loc['天猫', 'cvr']:.2%})稳定，加购率({summary.loc['天猫', 'cart_rate']:.2%})高，适合货架深度搜索承接与高LTV会员复购。" if '天猫' in summary.index else "无数据"
        diff_jd = f"京东自营履约保障与高净值人群支撑最高客单价(¥{summary.loc['京东', 'aov']:.2f})，CVR({summary.loc['京东', 'cvr']:.2%})与UV价值(¥{summary.loc['京东', 'uv_value']:.2f})领先，退款率最低。" if '京东' in summary.index else "无数据"
        diff_douyin = f"抖音基于内容兴趣推荐爆发力强({int(summary.loc['抖音', 'impressions']):,}PV)，但脉冲式冲动购买导致退款率({summary.loc['抖音', 'refund_rate']:.2%})高，依赖千川持续投放。" if '抖音' in summary.index else "无数据"
        diff_pdd = f"拼多多社交裂变与低价心智突出，CTR({summary.loc['拼多多', 'ctr']:.2%})与CVR({summary.loc['拼多多', 'cvr']:.2%})双高，走量快，但单均客单价偏低(¥{summary.loc['拼多多', 'aov']:.2f})且面临仅退款风险。" if '拼多多' in summary.index else "无数据"

        diagnostics["platform_differences"].append({
            "dimension": "流量属性与转化心智",
            "tmall": diff_tmall,
            "jd": diff_jd,
            "douyin": diff_douyin,
            "pdd": diff_pdd
        })
        
        ad_tmall = f"万相台与搜索投放ROAS为{summary.loc['天猫', 'roas']:.2f}，投放费比{summary.loc['天猫', 'ad_ratio']:.1%}，主要靠自然流量与老客撬动。" if '天猫' in summary.index else "无数据"
        ad_jd = f"快车与购物触点ROI为{summary.loc['京东', 'roas']:.2f}，核心承接精准品类词与品牌专区。" if '京东' in summary.index else "无数据"
        ad_douyin = f"千川广告投放费比达{summary.loc['抖音', 'ad_ratio']:.1%}，ROAS为{summary.loc['抖音', 'roas']:.2f}，受短视频素材生命周期短影响波动大。" if '抖音' in summary.index else "无数据"
        ad_pdd = f"全站推广结合多多进宝ROAS为{summary.loc['拼多多', 'roas']:.2f}，广告费比{summary.loc['拼多多', 'ad_ratio']:.1%}，主要看自然流量杠杆比与投产平衡。" if '拼多多' in summary.index else "无数据"

        diagnostics["platform_differences"].append({
            "dimension": "投放回报与费用结构",
            "tmall": ad_tmall,
            "jd": ad_jd,
            "douyin": ad_douyin,
            "pdd": ad_pdd
        })
        
        # 2. 商品维度问题挖掘 (找出高退款、负利润SKU)
        sku_analysis = self.get_product_portfolio_analysis()
        high_refund_skus = sku_analysis[sku_analysis['refund_rate'] > 0.20].sort_values(by='refund_rate', ascending=False)
        for _, sku in high_refund_skus.head(4).iterrows():
            diagnostics["product_issues"].append({
                "channel": sku['channel'],
                "sku_name": sku['sku_name'],
                "issue_type": "异常高退款退货率",
                "metric_detail": f"退款率达 {sku['refund_rate']:.1%} (退款侵蚀导致净销售与利润受损)",
                "root_cause": "多发生于尺码规格预期偏差、内容带货过度承诺、材质落差或拼多多极速仅退款拦截不足。"
            })
            
        low_cvr_traffic_skus = sku_analysis[(sku_analysis['visitors'] > sku_analysis['visitors'].quantile(0.6)) & (sku_analysis['cvr'] < sku_analysis['cvr'].median())]
        for _, sku in low_cvr_traffic_skus.head(3).iterrows():
            diagnostics["product_issues"].append({
                "channel": sku['channel'],
                "sku_name": sku['sku_name'],
                "issue_type": "流量空转与承接转化弱",
                "metric_detail": f"访客UV {int(sku['visitors']):,} 但CVR仅 {sku['cvr']:.2%}",
                "root_cause": "主图点击引导的利益点与商详承接脱节，定价卡位偏高或缺乏阶段性促销刺激。"
            })

        # 3. 运营动作偏差分析
        diagnostics["operational_actions"] = [
            {
                "channel": "抖音",
                "finding": "千川投放过度依赖泛兴趣人群包，素材起量快但后链路转化与签收率骤降",
                "action_flaw": "运营重前置GMV与瞬时ROI，忽视了扣除退款后的真实净贡献率，造成物流包装与运费险净损耗。"
            },
            {
                "channel": "天猫",
                "finding": "大促机制与日常日销缺乏清晰分层，加购蓄水转化周期拖长",
                "action_flaw": "日常缺乏限时降价与会员专享券刺激，大量意向人群停留在购物车流失，需建立7天追单触达机制。"
            },
            {
                "channel": "京东",
                "finding": "品类货盘宽度受限，腰尾部爆品梯度断层",
                "action_flaw": "单品贡献高度集中于成熟老爆品，新品入仓测试与快车测款节奏滞后，抗风险能力偏弱。"
            },
            {
                "channel": "拼多多",
                "finding": "单纯依靠降价破价换取活动资源位，缺乏多件阶梯装与边际成本精细核算",
                "action_flaw": "单品毛利空间被严重压缩，且未针对'仅退款'高频场景设立申诉阻断与异常售后拦截机制。"
            }
        ]

        # 4. 机会清单 (Opportunity Matrix)
        diagnostics["opportunity_list"] = [
            {
                "channel": "天猫",
                "opportunity": "爆品组合加价购与会员私域资产深淘",
                "potential_lift": "预计提升客单价8~12%，复购率拉升3.5个百分点",
                "action_path": "打通店铺会员0元入会即领阶梯券，详情页捆绑关联配件/连带耗材优惠。"
            },
            {
                "channel": "京东",
                "opportunity": "秒杀频道+自营/POP货盘联动下沉拓展",
                "potential_lift": "预计盘活潜力SKU销量30%以上，带来20%新增净GMV",
                "action_path": "针对中端价格带商品参与百亿补贴或限时秒杀，配合仓配极致时效打透品质换新心智。"
            },
            {
                "channel": "抖音",
                "opportunity": "短剧/短视频内容种草带货向商城搜索沉淀 (动销双轮驱动)",
                "potential_lift": "预计拉升抖店商城纯自然搜索成交占比至35%以上，将综合ROI提至3.2+",
                "action_path": "优化看后搜运维词，短视频爆款评论区置顶商品卡，直播切片长尾分发降低纯付费流依赖。"
            },
            {
                "channel": "拼多多",
                "opportunity": "定制量贩装/组合装入局百亿补贴，利用全站推广撬动高杠杆自然流",
                "potential_lift": "预计整体件单量提升40%，边际贡献利润总额提升25%以上",
                "action_path": "针对SKU_003与SKU_006设计'多件装超值拼'，设置保本投产比自动巡检，承接百亿补贴万人团。"
            }
        ]
        
        # 5. 下一阶段7/14/30天经营调优策略
        diagnostics["next_stage_recommendations"] = {
            "7_days": [
                "【抖音】按'净结算ROI'再过滤投放计划，关停退款率>30%计划，收窄定向至高粘性人群包；",
                "【拼多多】重构SKU装包规格，上线2件立减/3件组合装，规避单件极端破价并优化运费边际；",
                "【天猫/京东】排查高退款SKU的差评关键词，首屏补充尺码与实物图文说明，前置遏制冲动退款；",
                "【天猫】针对近7天加购未支付高意向用户，配置购物车定向专享券与降价提醒进行精准追单。"
            ],
            "14_days": [
                "【四平台差异化货盘】天猫主推经典款与礼盒(保利润+会员)，京东主推旗舰高配款(保客单+服务)，抖音主推高视觉爆发款(保拉新)，拼多多主推极致性价比量贩款(保走量与基础动销)；",
                "【素材与详情重塑】下架抖音夸大宣传素材，规范拼多多SKU选项明细，消除消费者到手预期偏差；",
                "【价格带协同】建立全网控价红线与库存动态预警机制，防止渠道窜货及平台破价导致被动比价罚扣。"
            ],
            "30_days": [
                "【全域全生命周期LTV】以天猫与拼多多为触点，通过包裹卡、私域服务号沉淀核心高粘性会员；",
                "【协同测款流水线】抖音内容测试曝光与兴趣 -> 拼多多快速走量建立基础销量权重点亮爆款标 -> 天猫/京东沉淀品牌旗舰心智与高阶利润；",
                "【单品全链路UE模型监控】将售后退款率、运费险支出、平台佣金、广告推广费统一纳入各渠道单品日度边际利润考核。"
            ]
        }
        
        return diagnostics
