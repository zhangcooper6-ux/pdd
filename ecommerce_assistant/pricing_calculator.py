"""
电商多模式智能算价与投产反算引擎 (精准对齐用户 Excel 算价表定义)
支持自定义折扣 (如 0.7、0.5 等) 与优惠券面额，精准计算每单毛利、广告花费、广告后净利润及净利润率。
"""

from typing import Dict, Any, List, Optional

class EcommercePricingCalculator:
    
    @staticmethod
    def calculate_single_sku(
        sku_name: str,
        sku_qty: int,
        unit_cost: float,
        selling_price: float,
        express_fee: float = 1.8,
        material_fee: float = 0.1,
        labor_fee: float = 0.25,
        refund_rate: float = 0.15,
        insurance_fee: float = 0.0,
        platform_commission_rate: float = 0.006, # 拼多多 0.6% 扣点
        coupon_amount: float = 2.0,              # 自定义优惠券 (元)
        discount_rate: float = 0.7,               # 自定义折扣 (如 0.7 表示7折)
        actual_roas: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        单 SKU 极速精算 (严格遵循 Excel 《Sheet1》《核算》《其他》 公式)
        """
        # 1. 商品总成本
        goods_cost = round(unit_cost * sku_qty, 2)
        
        # 2. 基础毛利 (未扣除退货损耗前: 售价 - 快递 - 商品总成本 - 耗材 - 人工 - 运费险)
        profit_before_refund = round(selling_price - express_fee - goods_cost - material_fee - labor_fee - insurance_fee, 2)
        
        # 3. 实际每单毛利 (扣除预期退款损耗与平台技术服务费扣点)
        refund_loss = round(selling_price * refund_rate, 4)
        commission_fee = round(selling_price * platform_commission_rate, 4)
        profit_after_refund = round(profit_before_refund - refund_loss - commission_fee, 4)
        
        # 毛利率 (毛利 / 售价)
        margin_rate = round(profit_after_refund / selling_price, 4) if selling_price > 0 else 0.0
        
        # 4. 理论无退款保本 ROAS (按未扣退款前基础毛利计算)
        raw_breakeven_roas = round(selling_price / profit_before_refund, 4) if profit_before_refund > 0 else 99.0
        
        # 5. 包含退款损耗的真实保本 ROAS / 保本 ROI (行业标准公式: 保本 ROI = 1 / 毛利率 = 售价 / 实际每单毛利)
        # 在此 ROAS 下，每单广告花费正好等于实际毛利，净利润为 0 (保本平衡点)
        breakeven_roas = round(selling_price / profit_after_refund, 4) if profit_after_refund > 0 else 99.0
        net_roas = breakeven_roas
        
        # 6. 拖价/售后目标 ROAS (ROAS / 0.8 -> * 1.05 -> * 1.3)
        roas_after_service = round(breakeven_roas / 0.8, 2)
        optimal_roas = round(roas_after_service * 1.05 * 1.3, 2)
        
        # 7. 用户自定义投产比与广告花费 / 净利润测算
        target_roas = actual_roas if (actual_roas and actual_roas > 0) else net_roas
        ad_cost_per_order = round(selling_price / target_roas, 2) if target_roas > 0 else 0.0
        
        # 广告后每单净利润 = 实际每单毛利 - 每单广告成本
        profit_after_ad = round(profit_after_refund - ad_cost_per_order, 2)
        net_margin_rate = round(profit_after_ad / selling_price, 4) if selling_price > 0 else 0.0
        
        # 8. 虚高原价与折扣券反算 (支持用户自定义优惠券 coupon_amount 与折扣 discount_rate)
        # Excel 公式: 虚高原价 = (售价 + 优惠券) / 折扣; 反算售价 = 虚高原价 * 折扣 - 优惠券; 总优惠 = 虚高原价 - 反算售价
        valid_discount = discount_rate if (0 < discount_rate <= 1.0) else 0.7
        inflated_original_price = round((selling_price + coupon_amount) / valid_discount, 2)
        reflow_price = round(inflated_original_price * valid_discount - coupon_amount, 2)
        total_discount_display = round(inflated_original_price - reflow_price, 2)
        
        return {
            "sku_name": sku_name,
            "sku_qty": sku_qty,
            "unit_cost": unit_cost,
            "goods_cost": goods_cost,
            "selling_price": selling_price,
            "express_fee": express_fee,
            "material_fee": material_fee,
            "labor_fee": labor_fee,
            "refund_rate": refund_rate,
            "refund_loss": refund_loss,
            "insurance_fee": insurance_fee,
            "commission_fee": commission_fee,
            "profit_before_refund": profit_before_refund,
            "profit_after_refund": profit_after_refund,
            "margin_rate": margin_rate,
            "raw_breakeven_roas": raw_breakeven_roas,
            "breakeven_roas": breakeven_roas,
            "net_roas": net_roas,
            "roas_after_service": roas_after_service,
            "optimal_roas": optimal_roas,
            "target_roas": target_roas,
            "ad_cost_per_order": ad_cost_per_order,
            "profit_after_ad": profit_after_ad,
            "net_margin_rate": net_margin_rate,
            "coupon_amount": coupon_amount,
            "discount_rate": valid_discount,
            "inflated_original_price": inflated_original_price,
            "reflow_price": reflow_price,
            "total_discount_display": total_discount_display
        }

    @classmethod
    def batch_calculate(
        cls,
        skus_input: List[Dict[str, Any]],
        common_express: float = 1.8,
        common_material: float = 0.1,
        common_labor: float = 0.25,
        common_refund_rate: float = 0.15,
        common_insurance: float = 0.0,
        common_commission_rate: float = 0.006,
        target_roas: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        批量算价与组合订单日/月度利润模拟
        """
        calculated_skus = []
        total_daily_orders = 0
        total_daily_revenue = 0.0
        total_daily_gross_profit = 0.0
        total_daily_ad_spend = 0.0
        total_daily_net_profit = 0.0

        for item in skus_input:
            daily_orders = item.get("daily_orders", 100)
            res = cls.calculate_single_sku(
                sku_name=item.get("sku_name", "常规规格"),
                sku_qty=int(item.get("sku_qty", 1)),
                unit_cost=float(item.get("unit_cost", 1.0)),
                selling_price=float(item.get("selling_price", 9.9)),
                express_fee=float(item.get("express_fee", common_express)),
                material_fee=float(item.get("material_fee", common_material)),
                labor_fee=float(item.get("labor_fee", common_labor)),
                refund_rate=float(item.get("refund_rate", common_refund_rate)),
                insurance_fee=float(item.get("insurance_fee", common_insurance)),
                platform_commission_rate=float(item.get("platform_commission_rate", common_commission_rate)),
                coupon_amount=float(item.get("coupon_amount", 2.0)),
                discount_rate=float(item.get("discount_rate", 0.7)),
                actual_roas=target_roas or item.get("actual_roas")
            )
            
            day_rev = round(res["selling_price"] * daily_orders, 2)
            day_gross = round(res["profit_after_refund"] * daily_orders, 2)
            day_ad = round(res["ad_cost_per_order"] * daily_orders, 2)
            day_net = round(res["profit_after_ad"] * daily_orders, 2)
            
            res["daily_orders"] = daily_orders
            res["daily_revenue"] = day_rev
            res["daily_gross_profit"] = day_gross
            res["daily_ad_spend"] = day_ad
            res["daily_net_profit"] = day_net
            
            calculated_skus.append(res)
            
            total_daily_orders += daily_orders
            total_daily_revenue += day_rev
            total_daily_gross_profit += day_gross
            total_daily_ad_spend += day_ad
            total_daily_net_profit += day_net

        return {
            "skus": calculated_skus,
            "summary": {
                "total_daily_orders": total_daily_orders,
                "total_daily_revenue": round(total_daily_revenue, 2),
                "total_daily_gross_profit": round(total_daily_gross_profit, 2),
                "total_daily_ad_spend": round(total_daily_ad_spend, 2),
                "total_daily_net_profit": round(total_daily_net_profit, 2),
                "monthly_net_profit_est": round(total_daily_net_profit * 30, 2),
                "overall_roas": round(total_daily_revenue / total_daily_ad_spend, 2) if total_daily_ad_spend > 0 else 0.0,
                "overall_net_margin": round(total_daily_net_profit / total_daily_revenue, 4) if total_daily_revenue > 0 else 0.0
            }
        }
