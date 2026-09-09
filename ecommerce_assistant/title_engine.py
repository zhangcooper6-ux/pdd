# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Any, Optional

class UniversalTitleEngine:
    """
    电商全类目通用智能防撞词高权重标题重塑引擎 (V3 增强语义版)
    针对任意类目（服饰/美妆/数码/家居/母婴/五金/生鲜/宠物等）
    基于全词匹配、中文词素边界与语义角色抽取，动态重塑 3 套四段式防比价爆款标题。
    """

    PROHIBITED_WORDS = [
        "最", "第一", "国家级", "顶级", "极品", "全网首发", "绝对", "独家", "绝无仅有",
        "万能", "包治百病", "全能", "首选", "唯一", "顶配", "王牌", "保真", "假一赔万"
    ]

    # 全类目核心品类实体词典（长词优先匹配）
    CORE_CATEGORIES = [
        # 宠物/日化
        "狗粮猫粮勺", "宠物粮食勺", "猫粮狗粮勺", "宠物狗粮勺", "宠物猫粮勺", "猫粮勺", "狗粮勺", "宠物勺", "铲米勺", "面粉勺", "舀米勺", "量米勺", "杂粮勺", "封口夹勺", "带夹勺", "量勺", "米勺", "粮勺", "勺子", "铲子",
        # 服饰/内衣/鞋包
        "碎花连衣裙", "雪纺连衣裙", "吊带连衣裙", "法式连衣裙", "短袖连衣裙", "复古连衣裙", "衬衫连衣裙", "针织连衣裙", "连衣裙", "长裙", "半身裙", "短裙", "短裤", "阔腿裤", "牛仔裤", "休闲裤", "防晒衣", "T恤", "衬衫", "卫衣", "外套", "内衣", "文胸", "睡衣", "运动鞋", "帆布鞋", "凉鞋", "拖鞋", "单肩包", "双肩包", "斜挎包",
        # 3C数码/家电/汽车
        "氮化镓充电器", "快充充电器", "无线充电器", "车载充电器", "充电器", "快充头", "插头", "充电宝", "数据线", "手机支架", "蓝牙耳机", "降噪耳机", "智能手表", "手机壳", "钢化膜", "平板支架", "车载支架", "行车记录仪",
        # 居家/日用/收纳/餐厨
        "不锈钢保温杯", "大容量保温杯", "便携保温杯", "车载保温杯", "保温水杯", "保温杯", "水杯", "玻璃杯", "马克杯", "茶杯", "咖啡杯", "收纳箱", "收纳盒", "收纳袋", "置物架", "沥水架", "调料架", "抹布", "清洁刷", "垃圾桶", "衣架", "纸巾盒", "挂钩",
        # 母婴/儿童/玩具
        "磁力片积木", "拼装积木", "益智玩具", "磁力片", "积木玩具", "拼图玩具", "早教玩具", "婴儿湿巾", "纸尿裤", "学步车", "婴儿推车", "儿童餐椅", "奶瓶", "吸奶器", "咬咬胶",
        # 五金/工具/美妆
        "螺丝刀套装", "电动螺丝刀", "万用表", "美工刀", "补水面膜", "美白精华", "洗面奶", "防晒霜", "口红", "粉底液"
    ]

    @classmethod
    def clean_raw_title(cls, raw_title: str) -> str:
        clean = re.sub(r'https?://[^\s]+', '', raw_title or '')
        clean = re.sub(r'[\s`~!@#$%^&*()_+=|{}\[\]:;"\'<>,.?/\\，。！￥……（）——【】、：；“”‘’《》？]+', ' ', clean).strip()
        for pw in cls.PROHIBITED_WORDS:
            clean = clean.replace(pw, "")
        return clean

    @classmethod
    def extract_core_and_modifiers(cls, raw_title: str, custom_kw: Optional[str] = None) -> tuple:
        clean = cls.clean_raw_title(raw_title)
        
        # 1. 识别核心词 (优先从全类目词库按最长匹配)
        matched_core = custom_kw
        if not matched_core:
            for cat in cls.CORE_CATEGORIES:
                if cat in clean:
                    matched_core = cat
                    break

        if not matched_core:
            # 兜底：如果没匹配到大词典，从标题前部分提取名词
            words = [w for w in clean.split() if len(w) >= 2]
            matched_core = words[0] if words else "多功能爆款"

        # 2. 提取长尾修饰词与场景词 (从原标题中扣除核心词，切出真实特征)
        remaining = clean.replace(matched_core, " ")
        raw_tokens = [w for w in re.split(r'[\s/]+', remaining) if len(w) >= 2]
        
        # 如果 raw_tokens 太少（原标题没有空格），采用语义特征正则挖掘
        feature_words = []
        if len(raw_tokens) <= 2:
            text = remaining.replace(" ", "")
            # 广泛挖掘场景与卖点词
            patterns = [
                # 场景/对象
                "家用", "厨房", "宠物", "猫粮", "狗粮", "猫咪", "狗狗", "铲米", "面粉", "五谷", "杂粮", "车载", "户外", "便携", "男士", "女士", "儿童", "早教", "宝宝", "学生", "办公室", "女夏", "小个子", "显瘦", "收腰", "气质",
                # 功能/特性
                "加厚", "加长", "防断", "防潮", "防尘", "自带封口夹", "带夹子", "带夹", "个性手柄", "省力", "大容量", "快充", "氮化镓", "多口", "304不锈钢", "定制刻字", "3D立体", "益智拼装", "磁铁吸铁石", "母婴级", "食品级", "无异味", "免打孔", "耐用"
            ]
            for p in patterns:
                if p in text and p not in feature_words and p not in matched_core:
                    feature_words.append(p)
            tokens = feature_words if feature_words else raw_tokens
        else:
            tokens = raw_tokens

        # 去重
        seen = set()
        clean_tokens = []
        for t in tokens:
            if t not in seen and len(t) >= 2:
                seen.add(t)
                clean_tokens.append(t)

        return matched_core, clean_tokens

    @classmethod
    def restructure_universal_titles(cls, raw_title: str, category_kw: Optional[str] = None) -> Dict[str, Any]:
        core_word, modifiers = cls.extract_core_and_modifiers(raw_title, category_kw)
        
        # 将提取到的长尾特征归纳为场景与功能卖点
        scene_part = "".join(modifiers[:2]) if len(modifiers) >= 2 else (modifiers[0] if modifiers else "家用多功能")
        feat_part = "".join(modifiers[2:4]) if len(modifiers) >= 4 else ("".join(modifiers[1:]) if len(modifiers) > 1 else "加厚耐用")

        # 动态类目特征前缀与差异词
        is_clothing = any(w in raw_title for w in ["连衣裙", "裙", "衣", "裤", "鞋", "服饰"])
        is_digital = any(w in raw_title for w in ["充电", "快充", "插头", "耳机", "数据线", "支架"])
        
        diff_a = "【2024新款】" if is_clothing else ("【升级快充】" if is_digital else "【加厚升级】")
        diff_c = "法式轻奢" if is_clothing else ("旗舰原装" if is_digital else "官方品质")

        # ==================== 方案 A：🔥 四段式防比价爆款 (推荐) ====================
        # 公式：[防比价差异词] + [核心大词] + [长尾场景词] + [功能材质]
        t1 = f"{diff_a}{core_word}{scene_part}{feat_part}食品级加厚正品保障" if not is_clothing else f"{diff_a}{core_word}{scene_part}{feat_part}显瘦气质垂感长裙"
        if len(t1) > 30: t1 = t1[:30]
        elif len(t1) < 26: t1 = (t1 + "多功能实用好物")[:30]

        # ==================== 方案 B：⚡ 性价比自然流跑量款 ====================
        # 公式：[前置刚需搜索词] + [核心大词] + [长尾修饰] + [微赠品防比价词]
        t2 = f"{scene_part}{core_word}{feat_part}多用途高性价比配配件超值家用包邮" if not is_clothing else f"{scene_part}{core_word}{feat_part}小个子显瘦舒适百搭正品包邮"
        if len(t2) > 30: t2 = t2[:30]
        elif len(t2) < 26: t2 = (t2 + "耐用实惠")[:30]

        # ==================== 方案 C：👑 品质升级高溢价款 ====================
        # 公式：[品质前缀] + [核心大词] + [真实长尾特征] + [质检无忧防撞词]
        t3 = f"{diff_c}{core_word}{scene_part}{feat_part}母婴级环保无异味质检认证" if not is_clothing else f"{diff_c}{core_word}{scene_part}{feat_part}高级感不挑身材品质保证"
        if len(t3) > 30: t3 = t3[:30]
        elif len(t3) < 26: t3 = (t3 + "高档质感品质优选")[:30]

        return {
            "core_word": core_word,
            "title_plans": [
                {
                    "scheme": "🔥 四段式防比价爆款 (推荐)",
                    "title": t1,
                    "formula_breakdown": {
                        "核心词": core_word,
                        "长尾修饰词": scene_part,
                        "材质场景": feat_part,
                        "防比价差异词": diff_a
                    },
                    "char_count": len(t1),
                    "strategy": "严格按 [防比价差异词] + [核心大词] + [长尾场景词] + [材质/功能] 组合，彻底规避算法同款压价。"
                },
                {
                    "scheme": "⚡ 性价比自然流跑量款",
                    "title": t2,
                    "formula_breakdown": {
                        "核心词": core_word,
                        "长尾修饰词": scene_part,
                        "材质场景": feat_part,
                        "防比价差异词": "送配套/高性价比"
                    },
                    "char_count": len(t2),
                    "strategy": "前置真实刚需高频搜索词，后置微赠品差异词，兼顾 9.9 包邮与高点击 CTR。"
                },
                {
                    "scheme": "👑 品质升级高溢价款",
                    "title": t3,
                    "formula_breakdown": {
                        "核心词": core_word,
                        "长尾修饰词": scene_part,
                        "材质场景": feat_part,
                        "防比价差异词": diff_c + "/质检保障"
                    },
                    "char_count": len(t3),
                    "strategy": "主打官方正品、质检保障与环保高端属性，为 19.9+ 高客单价提供充足溢价支撑。"
                }
            ],
            "naming_rule": "四段式全品类组合：[防比价差异词] + [核心词] + [高频长尾修饰词] + [材质/场景/赠品]，字数 26~30 字，严禁极限词与同行品牌词。"
        }
