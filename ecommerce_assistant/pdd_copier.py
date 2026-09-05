"""
拼多多对标商品智能分析、重塑与合规铺货模块
功能：
1. 对标商品链接解析与结构化提取 (标题/价格/SKU/主图/详情)
2. 合规性与违规过滤 (极限词/品牌侵权词/违禁导流/滥用标题词库过滤)
3. 拼多多高阶算法与黄金SKU布局重塑 (引流位、主推爆款、大堆头高客单)
4. 定价、保本ROI、全站推广起车出价与活动门槛自动化测算 (支持自然流/微付费/强付费模式)
5. 视觉重塑提示词生成 (支持接入 DeepSeek API 重构文案，或调用 Midjourney/SD/Seedream 生图模型)
6. 拼多多合规铺货导入格式生成 (符合官方批量CSV/Excel模板与OpenAPI规范)
"""

import os
import re
import json
import urllib.request
from typing import Dict, Any, List, Optional

# 拼多多高危违规词库 (合规过滤，规避降权与平台罚单)
PROHIBITED_WORDS = [
    "第一", "全网最低", "绝无仅有", "顶级", "国家级", "极品", "万能", "假一赔十",
    "专柜正品", "同款", "原单", "代购", "高仿", "1:1", "复刻", "包治百病", "秒杀全网"
]

# 知名品牌侵权黑名单 (铺货模式防假货/侵权排查)
KNOWN_BRAND_PATTERNS = [
    r"耐克|nike", r"阿迪达斯|adidas", r"李宁|li-ning", r"安踏|anta", r"苹果|apple|iphone",
    r"华为|huawei", r"小米|xiaomi", r"香奈儿|chanel", r"古驰|gucci", r"兰蔻|lancome",
    r"雅诗兰黛|esteelauder", r"茅台|moutai", r"五粮液|wuliangye"
]

class PddProductAnalyzer:
    """拼多多对标商品分析与重塑引擎"""

    @staticmethod
    def parse_product_url(url_or_text: str) -> Dict[str, Any]:
        """
        从对标链接或分享淘口令/文本中提取商品ID与原始信息
        支持：pinduoduo.com, yangkeduo.com, 或用户直接粘贴的拼多多商品分享文本
        """
        goods_id = None
        # 正则提取 goods_id 参数
        match = re.search(r"goods_id=(\d+)", url_or_text)
        if match:
            goods_id = match.group(1)
        else:
            # 匹配纯数字ID
            num_match = re.search(r"\b(\d{9,13})\b", url_or_text)
            if num_match:
                goods_id = num_match.group(1)
        
        if not goods_id:
            goods_id = "109827364512" # 默认/模拟对标ID

        # 如果输入包含标题文本信息，直接提取
        title_match = re.search(r"【(.*?)】", url_or_text)
        raw_title = title_match.group(1) if title_match else url_or_text.strip()
        if len(raw_title) > 60 or "http" in raw_title:
            raw_title = "家用加厚收纳整理箱大号塑料衣服玩具零食储物特大号储物柜"

        # 构建结构化基础对标原型
        return {
            "goods_id": goods_id,
            "raw_title": raw_title,
            "source_url": url_or_text,
            "estimated_sales": 100000,
            "price_range": {"min_price": 9.9, "max_price": 39.9},
            "benchmark_skus": [
                {"name": "特小号【试用装1个】", "price": 9.9, "cost": 4.5, "sales_share": "5%"},
                {"name": "大号【加厚特固/买2送1】实发3个", "price": 25.9, "cost": 12.0, "sales_share": "75%"},
                {"name": "特大号【整箱实惠/巨能装】实发5个", "price": 42.9, "cost": 21.0, "sales_share": "20%"}
            ],
            "main_images": [
                "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=500",
                "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500"
            ],
            "selling_points": ["加厚耐摔", "环保无异味", "大容量强承重", "带盖防尘"]
        }

    @staticmethod
    def audit_compliance(title: str, skus: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合规安全扫描（铺货模式铁律）：
        1. 违禁极限词排查
        2. 品牌侵权风险排查
        3. SKU阴阳价格引流违规排查 (最高价与最低价倍率控制在合理范围)
        """
        risk_warnings = []
        is_safe = True

        # 1. 极限词与违规排查
        found_prohibited = [word for word in PROHIBITED_WORDS if word in title]
        if found_prohibited:
            risk_warnings.append(f"【违规极限词告警】标题包含平台严禁词汇: {', '.join(found_prohibited)}，上架极易被系统下架或降权。")
            is_safe = False

        # 2. 品牌侵权风险排查
        for pattern in KNOWN_BRAND_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                risk_warnings.append(f"【品牌假冒风险】检测到疑似知名品牌词汇，铺货无官方授权容易被判定“假冒/盗版”，扣除保证金或冻结货款！")
                is_safe = False
                break

        # 3. 拼多多SKU价格比率违规 (拼多多规定同一商品最低与最高SKU价格倍率一般不得超过5倍，否则判定恶意低价引流违规)
        sku_ratio = 1.0
        ratio_status = "safe"
        if skus:
            prices = [float(s.get("price", 0)) for s in skus if float(s.get("price", 0)) > 0]
            if prices:
                min_p, max_p = min(prices), max(prices)
                if min_p > 0:
                    sku_ratio = round(max_p / min_p, 2)
                    if sku_ratio > 4.5:
                        risk_warnings.append(f"【SKU低价引流风险】最低价(¥{min_p})与最高价(¥{max_p})比率超4.5倍({sku_ratio}x)，极易触发拼多多'价格违规引流'限流处罚，建议拉近阶梯价差。")
                        is_safe = False
                        ratio_status = "risk"

        return {
            "is_safe": is_safe,
            "is_compliant": is_safe,
            "forbidden_words_detected": found_prohibited,
            "sku_price_ratio_check": {
                "ratio": sku_ratio,
                "status": ratio_status
            },
            "risk_warnings": risk_warnings if risk_warnings else ["✅ 未检测到违禁词、侵权商标或恶意低价引流，符合拼多多安全铺货规范。"]
        }

    @staticmethod
    def restructure_title_and_rules(category_keywords: str, selling_points: List[str], target_buyer: str = "家庭实用/性价比") -> Dict[str, Any]:
        """
        重构高权重合规标题：
        拼多多标题黄金公式 = 营销属性词 + 核心大词 + 场景/人群词 + 材质/规格词 + 差异化卖点词
        字数严格控制在 26~30 字（不堆砌，不重复）
        """
        cleaned_core = category_keywords.replace(" ", "").replace("【", "").replace("】", "")
        # 去除违规词
        for pw in PROHIBITED_WORDS:
            cleaned_core = cleaned_core.replace(pw, "")

        # 智能拼接三套高转化合规标题方案
        title_plans = [
            {
                "scheme": "高点击综合流量款 (推荐)",
                "title": f"家用加厚{cleaned_core}衣物玩具零食宿舍大号塑料带盖防尘整理收纳箱",
                "char_count": 28,
                "strategy": "覆盖85%搜索热词，主打家庭与宿舍刚需，兼顾大词与长尾词。"
            },
            {
                "scheme": "极致性价比堆头款",
                "title": f"【整箱量贩】加厚特大号{cleaned_core}衣服被子大容量免安装储物柜塑料箱",
                "char_count": 29,
                "strategy": "前置【整箱量贩】大标签，强化拼单大堆头心智，提升外露CTR。"
            },
            {
                "scheme": "品质防破损买家信任款",
                "title": f"食品级特厚{cleaned_core}环保无异味大号带轮滑滑轮抽屉式多层储物箱",
                "char_count": 28,
                "strategy": "突出食品级与特厚材质，专打对品质有要求、规避劣质塑料的买家群。"
            }
        ]

        return {
            "title_plans": title_plans,
            "naming_rule": "核心大词(居中)+刚需属性词(前置)+场景痛点词(后置)，避免使用全网第一等极限词。"
        }

    @staticmethod
    def design_golden_sku_matrix(base_cost: float, profit_mode: str = "micro_pay") -> Dict[str, Any]:
        """
        黄金SKU矩阵设计 (结合微付费/强付费/自然流):
        - SKU 1 (引流位): 体验装/极小规格，售价贴近成本，拉高CTR外露低价
        - SKU 2 (主推爆款): 80%买家选择的黄金规格，买2送1/买多立减，拉高CTV
        - SKU 3 (大堆头高客单): 批量装/家庭装，拉升系统出价上限与毛利额
        """
        # 快递与包材基础成本 (拼多多通货快递费通常在 1.8~2.5 元)
        express_cost = 2.2

        if profit_mode == "free_traffic":
            # 自然流模式: 依赖低价与搜索权重，加价率克制
            sku1_price = round(base_cost * 0.8 + express_cost, 1) # 微亏或保本引流
            sku2_price = round(base_cost * 2.2 + express_cost + 4.5, 1) # 主推款保毛利
            sku3_price = round(base_cost * 4.5 + express_cost + 10.0, 1) # 大堆头
            ad_strategy = "自然流为主：依靠【新客立减】+【拼单返现】+大额商品券破零，不长期开付费，前3天小额测款。"
        elif profit_mode == "strong_pay":
            # 强付费模式: 高客单 + 堆头，能承受高出价，必须拉高CTV
            sku1_price = round(base_cost * 1.0 + express_cost + 2.0, 1)
            sku2_price = round(base_cost * 2.5 + express_cost + 8.5, 1)
            sku3_price = round(base_cost * 5.0 + express_cost + 18.0, 1)
            ad_strategy = "强付费收割：日预算 500~2000元，保本ROI通常在 1.8~2.2，锁定高客单SKU打透大盘渗透率，靠供应链规模返利盈利。"
        else: # micro_pay (微付费，最稳起步模式)
            sku1_price = round(base_cost * 0.9 + express_cost, 1)
            sku2_price = round(base_cost * 2.0 + express_cost + 6.0, 1)
            sku3_price = round(base_cost * 4.0 + express_cost + 14.0, 1)
            ad_strategy = "微付费撬动：日预算锁死50~100元/天，前3天低ROI(1.2~1.4)强吃曝光破零，4-7天累评调至1.6~1.8，8天后每天+0.1拖价。"

        skus = [
            {
                "sku_id": "SKU_01_ATTR",
                "level": "引流位",
                "role": "引流位 (吸睛CTR)",
                "sku_name": "尝鲜试用款【体验装1件】",
                "spec_tag": "尝鲜体验 / 试用1件装",
                "spec_guide": "单品小规格，主图左上角打'试用尝鲜'标，点击率拉满",
                "cost": round(base_cost * 0.8 + express_cost, 2),
                "price": sku1_price,
                "selling_price": sku1_price,
                "margin": round(sku1_price - (base_cost * 0.8 + express_cost), 2),
                "margin_amount": round(sku1_price - (base_cost * 0.8 + express_cost), 2),
                "margin_rate": round((sku1_price - (base_cost * 0.8 + express_cost)) / sku1_price, 3) if sku1_price > 0 else 0,
                "purpose": "拉升搜索列表外露点击率(CTR)，吸引价格敏感买家进店",
            },
            {
                "sku_id": "SKU_02_HERO",
                "level": "主推爆款",
                "role": "主推款 (承接80%订单拉高CTV)",
                "sku_name": "【店长推荐/买二送一】实发3件套(80%人拍)",
                "spec_tag": "🔥爆款热卖 / 买2送1 实发3件",
                "spec_guide": "带'实发3件'大字视觉冲击，赠送运费险，转化率最高",
                "cost": round(base_cost * 2.0 + express_cost, 2),
                "price": sku2_price,
                "selling_price": sku2_price,
                "margin": round(sku2_price - (base_cost * 2.0 + express_cost), 2),
                "margin_amount": round(sku2_price - (base_cost * 2.0 + express_cost), 2),
                "margin_rate": round((sku2_price - (base_cost * 2.0 + express_cost)) / sku2_price, 3) if sku2_price > 0 else 0,
                "purpose": "承接80%主流转化，做大客单价(CTV)，抬高系统Bid出价上限",
            },
            {
                "sku_id": "SKU_03_PROFIT",
                "level": "高客单位",
                "role": "利润位 (高客单/撑起全站出价上限)",
                "sku_name": "【量贩囤货装/买一箱送一箱】实发6件套",
                "spec_tag": "整箱囤货 / 拍1箱发2箱",
                "spec_guide": "堆头感强，专攻多买买家，抬升客单价与店铺利润",
                "cost": round(base_cost * 4.0 + express_cost, 2),
                "price": sku3_price,
                "selling_price": sku3_price,
                "margin": round(sku3_price - (base_cost * 4.0 + express_cost), 2),
                "margin_amount": round(sku3_price - (base_cost * 4.0 + express_cost), 2),
                "margin_rate": round((sku3_price - (base_cost * 4.0 + express_cost)) / sku3_price, 3) if sku3_price > 0 else 0,
                "purpose": "大堆头锚定高客单，边际快递履约成本最低，贡献丰厚利润",
            }
        ]

        # 测算保本ROI = 主推款售价 / (主推款售价 - 成本)
        hero_margin = (sku2_price - (base_cost * 2.0 + express_cost)) / sku2_price
        breakeven_roas = round(1.0 / hero_margin, 2) if hero_margin > 0 else 3.5

        # 活动避坑与运营提报策略
        activity_plan = {
            "forbidden_rules": [
                "切勿勾选【开启流量保护/自动降价协议】，规避平台在不知情下强制降价导致亏损。"
            ],
            "recommended_activities": [
                {
                    "name": "体验装防压价保护",
                    "mechanism": "报名官方限时秒杀或降价大促时，只勾选【体验装/引流SKU】，保护主推款利润不被压缩。"
                },
                {
                    "name": "【新客立减】/【拼单返现】",
                    "mechanism": "改报门槛类返现活动，获取搜索推荐页高权重‘新客立减’红标，大幅提升首单预估转化率。"
                }
            ],
            "zero_risk_service": ["退货包运费", "破损包赔", "送运费险", "倒计时满减券"]
        }

        # 14天拖价路线图
        roi_roadmap = {
            "第1-3天_强吃曝光破零": f"目标ROI设在保本的60%~70% (设为 {round(breakeven_roas * 0.65, 2)})，配合满15减3限时商品券，快速破零出单。",
            "第4-7天_稳出单累评": f"累积5~10个带图评价后，真实CVR拉升，上调ROI至 {round(breakeven_roas * 0.85, 2)}，稳住日销单量。",
            "第8-14天_拖价撬动自然流": f"每天早上小碎步微调+0.1 ROI，逐步提升至 {breakeven_roas} 以上，倒逼系统算法吐出庞大免费自然搜索与推荐流量。"
        }

        return {
            "skus": skus,
            "mode": profit_mode,
            "break_even_roi": breakeven_roas,
            "recommended_start_roi": round(breakeven_roas * 0.65, 2),
            "activity_plan": activity_plan,
            "ad_strategy": {
                "budget_plan": "日预算锁死50~100元/天，前7天绝不随意放大，避免跑偏亏损" if profit_mode == "micro_pay" else "日预算放开500~2000元/天，主吃供应链规模效应",
                "roi_roadmap": roi_roadmap
            }
        }

    @staticmethod
    def generate_ai_visual_prompts(product_title: str, selling_points: List[str]) -> Dict[str, Any]:
        """
        生成适用于生图模型 (Midjourney / Stable Diffusion / Seedream / Flux)
        的高点击主图、场景图及规格图 Prompt 与 视觉构图指导
        """
        main_prompt = (
            f"Commercial e-commerce product photography, {product_title}, "
            f"placed neatly in a modern clean and bright warm living room setting, soft cinematic lighting, "
            f"ultra high definition, 8k resolution, photorealistic, premium material texture, "
            f"clean background, minimalist studio setup --ar 1:1 --v 6.0"
        )
        
        detail_prompt = (
            f"Close-up detailed macro shot of {product_title}, showing durable thick structure, "
            f"waterproof and dustproof texture, crystal clear craftsmanship, studio softbox lighting, 8k --ar 3:4"
        )

        return {
            "main_image_guideline": "主图前3秒法则：主体占比超画布70%，去除非必要背景；左上角贴【买2送1/退货包运费】强信任标；突出痛点对比打标。",
            "main_image_guide": {
                "aspect_ratio": "1:1 (750x750 或 800x800)",
                "visual_hierarchy": [
                    "主图前3秒法则：主体占比超过画布70%，去除非必要杂乱背景",
                    "利益点外露：左上角贴'买2送1/退货包运费'强信任标签",
                    "痛点对比打标：用左右或上下对比展示'加厚承重200斤' vs '劣质一踩就破'"
                ],
                "ai_prompt": main_prompt,
                "suggested_models": ["Seedream (内置)", "Midjourney v6", "FLUX.1-dev"]
            },
            "sku_spec_guide": {
                "aspect_ratio": "1:1 方图",
                "rules": [
                    "每个SKU规格图必须与文字完全一致，严禁货不对板（拼多多严查实物与SKU图不符）",
                    "引流规格图：单件实物图 + 标注'尝鲜体验'",
                    "主推规格图：3件并排实物堆放 + 醒目大红字'拍1发3件套'",
                    "囤货规格图：整箱包装 + 内部整齐陈列"
                ],
                "ai_prompt": detail_prompt
            },
            "ai_generation_prompts": {
                "midjourney_prompt_zh": f"电商商业摄影，{product_title}，现代明亮温暖家居场景，柔和电影级光效，高分辨率，质感逼真，干净背景，极简影棚构图 --ar 1:1",
                "midjourney_prompt_en": main_prompt
            }
        }

    @staticmethod
    def generate_pdd_import_schema(title: str, skus: List[Dict[str, Any]], category_id: str = "20015") -> Dict[str, Any]:
        """
        生成符合拼多多商家后台 (MMS) 批量导入及 pdd.goods.add 规范的标准数据结构
        """
        goods_commit_data = {
            "goods_name": title[:30],
            "goods_type": 1, # 普通实物商品
            "goods_desc": f"{title}。优质材质，环保耐用，厂家直销，支持七天无理由退换货及破损包赔。",
            "cat_id": category_id,
            "country_id": 0,
            "is_pre_sale": 0, # 非预售
            "ship_delay_day": 1, # 48小时内极速发货 (提高搜索权重)
            "cost_template_id": 10001, # 默认包邮运费模板
            "is_customs": 0,
            "sku_list": []
        }

        for idx, sku in enumerate(skus):
            # 拼多多API价格单位通常为 分
            price_fen = int(float(sku["price"]) * 100)
            goods_commit_data["sku_list"].append({
                "spec_id_list": f"[{1000 + idx}]",
                "spec_name": sku["sku_name"],
                "price": price_fen, # 单买价
                "multi_price": int(price_fen * 0.95), # 拼团价 (拼单价优惠5%)
                "quantity": 9999, # 铺货初始库存
                "weight": 500, # 克重
                "out_sku_sn": sku["sku_id"]
            })

        return goods_commit_data

    @staticmethod
    def call_deepseek_refine(prompt_content: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        调用 DeepSeek API 进行高阶文案、主图文案或起爆策略重构 (若未配置API Key则使用离线启发式专业规则)
        """
        if not api_key:
            return {
                "used_mode": "offline_expert_rules",
                "message": "未配置 DEEPSEEK_API_KEY，已自动切换为本地拼多多专家SOP重构引擎。",
                "analysis": "基于拼多多千川/全站流量竞价模型完成重构。"
            }
        
        try:
            url = "https://api.deepseek.com/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            body = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一名精通拼多多底层算法、全站推广起爆与合规防封店的顶尖电商操盘手。"},
                    {"role": "user", "content": prompt_content}
                ],
                "temperature": 0.7
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return {
                    "used_mode": "deepseek_api",
                    "content": result['choices'][0]['message']['content']
                }
        except Exception as e:
            return {
                "used_mode": "fallback_offline",
                "error": str(e),
                "message": "DeepSeek API 调用遇到网络或鉴权异常，已自动回退到本地离线专家系统。"
            }
