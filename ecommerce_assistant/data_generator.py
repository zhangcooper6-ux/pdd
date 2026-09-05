"""
全域电商模拟经营数据生成器
生成贴合中国主流消费品在天猫、京东、抖音三平台的近30天经营明细数据
包括商品级曝光、访客、加购、订单、GMV、退款、广告花费、成本等
"""

import os
import random
import pandas as pd
import numpy as np

def generate_omnichannel_dataset(output_path: str = "d:/pddyy/ecommerce_assistant/data/sample_omnichannel_data.csv") -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)
    
    skus = [
        {"sku_id": "SKU_001", "sku_name": "核心旗舰Pro款", "category": "核心主品", "base_price": 399, "cogs_ratio": 0.35},
        {"sku_id": "SKU_002", "sku_name": "经典畅销标准版", "category": "核心主品", "base_price": 249, "cogs_ratio": 0.38},
        {"sku_id": "SKU_003", "sku_name": "性价比入门引流款", "category": "引流放量", "base_price": 99, "cogs_ratio": 0.52},
        {"sku_id": "SKU_004", "sku_name": "联名高配礼盒装", "category": "礼赠定制", "base_price": 599, "cogs_ratio": 0.30},
        {"sku_id": "SKU_005", "sku_name": "便携迷你尝鲜款", "category": "引流放量", "base_price": 69, "cogs_ratio": 0.55},
        {"sku_id": "SKU_006", "sku_name": "耗材替换配件包", "category": "配件连带", "base_price": 49, "cogs_ratio": 0.25},
        {"sku_id": "SKU_007", "sku_name": "升级迭代新品A", "category": "新品潜力", "base_price": 329, "cogs_ratio": 0.40},
        {"sku_id": "SKU_008", "sku_name": "长尾定制特别版", "category": "长尾储备", "base_price": 459, "cogs_ratio": 0.42},
    ]
    
    channels = ["天猫", "京东", "抖音", "拼多多"]
    records = []
    
    # 模拟近30天聚合或SKU日粒度明细
    for sku in skus:
        for ch in channels:
            # 基础差异设定
            if ch == "天猫":
                # 货架搜索与成熟会员，高加购，退款适中，转化稳
                impressions = int(np.random.normal(120000, 15000))
                ctr = np.random.uniform(0.045, 0.065)
                visitors = int(impressions * ctr)
                cart_rate = np.random.uniform(0.12, 0.18)
                cart_uv = int(visitors * cart_rate)
                cvr = np.random.uniform(0.032, 0.048)
                paid_buyers = int(visitors * cvr)
                paid_orders = int(paid_buyers * np.random.uniform(1.02, 1.06))
                paid_units = int(paid_orders * np.random.uniform(1.1, 1.25))
                price = sku["base_price"] * np.random.uniform(0.92, 0.98)
                gmv = round(paid_units * price, 2)
                refund_rate = np.random.uniform(0.09, 0.14)
                if sku["sku_id"] == "SKU_005":
                    refund_rate = 0.28
                refund_amount = round(gmv * refund_rate, 2)
                ad_spend = round(gmv / np.random.uniform(3.2, 4.2), 2)
                repeat_rate = np.random.uniform(0.16, 0.24)
                
            elif ch == "京东":
                # 高客单，京东仓履约，退款低，客单最高，转化最高
                impressions = int(np.random.normal(85000, 10000))
                ctr = np.random.uniform(0.038, 0.052)
                visitors = int(impressions * ctr)
                cart_rate = np.random.uniform(0.08, 0.12)
                cart_uv = int(visitors * cart_rate)
                cvr = np.random.uniform(0.042, 0.058)
                paid_buyers = int(visitors * cvr)
                paid_orders = int(paid_buyers * np.random.uniform(1.01, 1.04))
                paid_units = int(paid_orders * np.random.uniform(1.05, 1.15))
                price = sku["base_price"] * np.random.uniform(0.96, 1.02)
                gmv = round(paid_units * price, 2)
                refund_rate = np.random.uniform(0.05, 0.08)
                refund_amount = round(gmv * refund_rate, 2)
                ad_spend = round(gmv / np.random.uniform(3.6, 4.8), 2)
                repeat_rate = np.random.uniform(0.14, 0.20)
                
            elif ch == "抖音":
                # 兴趣内容脉冲，巨大曝光，点击率偏低，冲动下单，退款率高，投产比受千川影响
                impressions = int(np.random.normal(320000, 40000))
                ctr = np.random.uniform(0.025, 0.038)
                visitors = int(impressions * ctr)
                cart_rate = np.random.uniform(0.05, 0.09)
                cart_uv = int(visitors * cart_rate)
                cvr = np.random.uniform(0.022, 0.035)
                paid_buyers = int(visitors * cvr)
                paid_orders = int(paid_buyers * np.random.uniform(1.0, 1.03))
                paid_units = int(paid_orders * np.random.uniform(1.05, 1.18))
                price = sku["base_price"] * np.random.uniform(0.85, 0.92)
                gmv = round(paid_units * price, 2)
                refund_rate = np.random.uniform(0.24, 0.33)
                if sku["sku_id"] == "SKU_003":
                    refund_rate = 0.38
                refund_amount = round(gmv * refund_rate, 2)
                ad_spend = round(gmv / np.random.uniform(2.1, 2.7), 2)
                repeat_rate = np.random.uniform(0.06, 0.11)
                
            else: # 拼多多
                # 社交裂变与极致性价比，高点击高转化，单客单价较低，拼团走量快，退款中等(含极速退款)
                impressions = int(np.random.normal(210000, 25000))
                ctr = np.random.uniform(0.048, 0.072) # 主图醒目低价标签带来高CTR
                visitors = int(impressions * ctr)
                cart_rate = np.random.uniform(0.06, 0.10) # 拼团为主，收藏略低直接发起拼单
                cart_uv = int(visitors * cart_rate)
                cvr = np.random.uniform(0.045, 0.065) # 拼单转化门槛低，转化率较高
                paid_buyers = int(visitors * cvr)
                paid_orders = int(paid_buyers * np.random.uniform(1.02, 1.05))
                paid_units = int(paid_orders * np.random.uniform(1.2, 1.45)) # 拼单多买、多件装
                price = sku["base_price"] * np.random.uniform(0.78, 0.86) # 极致拼团低价
                gmv = round(paid_units * price, 2)
                # 退款率约 13% - 19% (仅退款及极速售后)
                refund_rate = np.random.uniform(0.12, 0.18)
                if sku["sku_id"] == "SKU_007": # 模拟拼多多新品测试
                    refund_rate = 0.22
                refund_amount = round(gmv * refund_rate, 2)
                # 全站推广与多多进宝，投产比适中偏高
                ad_spend = round(gmv / np.random.uniform(3.4, 4.4), 2)
                repeat_rate = np.random.uniform(0.12, 0.18)
                
            repeat_buyers = int(paid_buyers * repeat_rate)
            cogs = round(paid_units * (sku["base_price"] * sku["cogs_ratio"]), 2)
            
            # 确定价格带
            if sku["base_price"] < 100:
                price_band = "¥0-99 (大众亲民)"
            elif sku["base_price"] <= 300:
                price_band = "¥100-300 (中端主力)"
            elif sku["base_price"] <= 500:
                price_band = "¥301-500 (进阶轻奢)"
            else:
                price_band = "¥500+ (高端礼赠)"
                
            records.append({
                "channel": ch,
                "sku_id": sku["sku_id"],
                "sku_name": sku["sku_name"],
                "category": sku["category"],
                "price_band": price_band,
                "impressions": impressions,
                "visitors": visitors,
                "product_views": int(visitors * np.random.uniform(1.3, 1.8)),
                "cart_uv": cart_uv,
                "paid_orders": paid_orders,
                "paid_buyers": paid_buyers,
                "paid_units": paid_units,
                "gmv": gmv,
                "refund_amount": refund_amount,
                "ad_spend": ad_spend,
                "cogs": cogs,
                "repeat_buyers": repeat_buyers
            })
            
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    # 同时导出一份带说明的Excel模板，方便用户直接对照上传
    excel_path = output_path.replace(".csv", ".xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="四平台经营明细", index=False)
        # 写入一个指标说明Sheet
        dict_data = [
            {"字段名": "channel", "说明": "渠道名称，如：天猫、京东、抖音、拼多多"},
            {"字段名": "sku_id", "说明": "商品唯一编码"},
            {"字段名": "sku_name", "说明": "商品名称"},
            {"字段名": "category", "说明": "商品分类或货盘标签"},
            {"字段名": "price_band", "说明": "价格区间标签"},
            {"字段名": "impressions", "说明": "曝光PV量"},
            {"字段名": "visitors", "说明": "访客UV量 (进店/进商详人数)"},
            {"字段名": "product_views", "说明": "商品浏览量PV"},
            {"字段名": "cart_uv", "说明": "加购与收藏UV"},
            {"字段名": "paid_orders", "说明": "支付订单数"},
            {"字段名": "paid_buyers", "说明": "支付买家数UV"},
            {"字段名": "paid_units", "说明": "成交件数"},
            {"字段名": "gmv", "说明": "拍下/支付总销售额(元)"},
            {"字段名": "refund_amount", "说明": "退款退货金额(元)"},
            {"字段名": "ad_spend", "说明": "付费商业化投放花费(元)"},
            {"字段名": "cogs", "说明": "商品物料与生产直接成本(元)"},
            {"字段名": "repeat_buyers", "说明": "本周期内复购买家数"}
        ]
        pd.DataFrame(dict_data).to_excel(writer, sheet_name="数据字典与填报规范", index=False)
        
    print(f"✅ 成功生成全域经营模拟数据集与Excel模板: {output_path} / {excel_path}")
    return df

if __name__ == "__main__":
    generate_omnichannel_dataset()
