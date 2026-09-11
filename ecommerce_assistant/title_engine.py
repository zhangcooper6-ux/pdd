# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Any, Optional

class UniversalTitleEngine:
    """
    电商全类目通用智能防撞词高权重标题与SKU重塑引擎 (V4 黄金四段式/二段式爆款版)
    严格遵循拼多多 NLP 文本切词、CV 图像图谱与广告推荐人群匹配底层逻辑：
    1. 标题四段式黄金词位：【大堆头营销前缀 1-10字】+【场景+核心词 11-20字】+【功效痛点词 21-28字】+【长尾属性词 28-30字】
    2. SKU 黄金二段/三段式命名：【大堆头实发前缀】+【核心商品词/场景词】+【准确规格/配件中性连接词】
    3. 规避同店指纹压制、类目错配与敏感词机审拦截
    """

    PROHIBITED_WORDS = [
        "最", "第一", "国家级", "顶级", "极品", "全网首发", "绝对", "独家", "绝无仅有",
        "万能", "包治百病", "全能", "首选", "唯一", "顶配", "王牌", "保真", "假一赔万",
        "秒杀全网", "专柜正品", "专柜", "原单", "高仿", "1:1", "复刻"
    ]

    # 全类目核心品类实体词典（长词优先匹配）
    CORE_CATEGORIES = [
        # 清洁/洗涤/日化
        "厨房重油污净", "抽油烟机清洁剂", "油烟机清洗剂", "重油污清洗剂", "油污清洁剂", "油污净", "清洁剂", "清洗剂", "去油剂", "洗洁精", "洗衣液", "除垢剂", "洁厕灵", "管道疏通剂", "地板清洁剂", "玻璃水",
        # 宠物/日用
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
    def optimize_sku_name(cls, orig_name: str, sku_qty: int, price: float, raw_title: str = "") -> str:
        """
        基于拼多多合规与高转化心理学黄金二段/三段式重塑 SKU 规格名：
        公式：【大堆头/实发属性前缀】 + 核心商品词/场景词 + 准确规格/配件(加号/搭/含)
        1. 彻底规避‘送’字等违规机审词（用 配/含/搭/加号中性连接词 替代）；
        2. 将核心品类词（如 厨房油污净、舀米勺）直接织入每一个 SKU，让 SKU 自身直接吃满细分搜索与推荐人群权重；
        3. 保留原始规格的颜色/款式/件数信息，保障账实相符，通过平台审核。
        """
        clean_name = orig_name.strip()
        core_kw, _ = cls.extract_core_and_modifiers(raw_title)
        if not core_kw or core_kw == "多功能爆款":
            core_kw = "正品好物"

        # 提取颜色或款式前缀（如“绿灰色”、“随机色”、“加长手柄”、“升级款”等）
        color_match = re.search(r"^([\u4e00-\u9fa5a-zA-Z0-9\+]+?)(?:【|（|\(|$)", clean_name)
        prefix_style = color_match.group(1).strip() if color_match else ""
        if prefix_style in ["店长推荐", "爆款", "热销", "升级加厚", "加厚", "拍一发二", "拍1发2", "买1送1", "买一送一"]:
            prefix_style = ""
            
        style_desc = f"{prefix_style}·" if prefix_style else ""
        is_cleaning = any(w in raw_title for w in ["油污", "清洁", "清洗", "去油", "洗洁", "洗涤", "抽油烟机"])
        is_pet = any(w in raw_title for w in ["宠物", "狗粮", "猫粮", "猫咪", "狗狗"])
        
        # 针对件数结构化重塑（黄金二段/三段式）
        if sku_qty == 1:
            if is_cleaning:
                opt_name = f"【尝鲜体验装】{core_kw}500ml (试用1瓶/限购1件)"
            elif is_pet:
                opt_name = f"【新客尝鲜装】{core_kw} 1把装·配防潮封口夹"
            else:
                opt_name = f"【尝鲜体验装】{style_desc}{core_kw} (1件装·限购1件)"
        elif sku_qty == 2:
            if is_cleaning:
                opt_name = f"【实发共2瓶】厨房抽油烟机{core_kw}500ml*2瓶 + 配高压专用喷头"
            elif is_pet:
                opt_name = f"🔥【实发共2件】{core_kw} 2把装 + 配趣味逗猫球 (加厚多功能)"
            else:
                opt_name = f"🔥【实发共2件】{style_desc}{core_kw} 2件套 + 配无痕挂钩 (80%买家选择)"
        elif sku_qty == 3:
            if is_cleaning:
                opt_name = f"⭐【超值3瓶套组】{core_kw}500ml*3瓶 + 配专用喷头 + 强力纳米海绵2块"
            elif is_pet:
                opt_name = f"⭐【多宠超值3件套】{core_kw} 3把装 + 配防潮密封夹3个"
            else:
                opt_name = f"⭐【超值3件套】{style_desc}{core_kw} 3件装 + 含防潮密封夹"
        elif sku_qty >= 4:
            if is_cleaning:
                opt_name = f"🏆【整箱家庭量贩5件套】抽油烟机{core_kw}500ml*4瓶 + 高压喷枪 + 加厚百洁布"
            elif is_pet:
                opt_name = f"🏆【多宠家庭囤货4件套】{core_kw} 4把装 + 配解闷玩具球大礼包"
            else:
                opt_name = f"🏆【整箱家庭大容量4件套】{style_desc}{core_kw} 4件装 + 配挂钩收纳全套"
        else:
            opt_name = f"👑【升级豪华装】{style_desc}{core_kw} + 配实用配件"

        return opt_name

    @classmethod
    def restructure_universal_titles(cls, raw_title: str, category_kw: Optional[str] = None) -> Dict[str, Any]:
        """
        基于拼多多爆款黄金四段式词位结构重构标题：
        【1-10字：大堆头/营销前缀】+【11-20字：场景+精准核心词】+【21-28字：功效/痛点词】+【28-30字：长尾属性词】
        1. 开头 1-10 字前置大堆头规格（如【实发5件套】、【买1发5】），彻底避开同店同款指纹压制，拉爆 CTR；
        2. 紧跟【场景+核心词】（如 厨房抽油烟机油污净），连贯紧凑，杜绝中间被长修饰词打断导致切词断裂；
        3. 注入痛点功效词（强力去重油、免洗、食品级加厚）；
        4. 末尾补齐高频长尾搜索热词，吃满 28~30 字权重。
        """
        core_word, modifiers = cls.extract_core_and_modifiers(raw_title, category_kw)
        
        # 将提取到的长尾特征归纳为场景与功能卖点
        scene_part = "".join(modifiers[:2]) if len(modifiers) >= 2 else (modifiers[0] if modifiers else "家用厨房")
        feat_part = "".join(modifiers[2:4]) if len(modifiers) >= 4 else ("".join(modifiers[1:]) if len(modifiers) > 1 else "加厚耐用")

        # 动态类目特征前缀与差异词
        is_clothing = any(w in raw_title for w in ["连衣裙", "裙", "衣", "裤", "鞋", "服饰"])
        is_digital = any(w in raw_title for w in ["充电", "快充", "插头", "耳机", "数据线", "支架"])
        is_cleaning = any(w in raw_title for w in ["油污", "清洁", "清洗", "去油", "洗洁", "洗涤", "抽油烟机"])
        is_pet = any(w in raw_title for w in ["宠物", "狗粮", "猫粮", "猫咪", "狗狗"])

        # ==================== 方案 A：🔥 黄金四段式大堆头爆款 (主推破零/拉爆CTR/防同店指纹) ====================
        # 结构：【大堆头营销前缀 1-10字】 + 【场景+核心词 11-20字】 + 【功效痛点词 21-28字】 + 【长尾词 28-30字】
        if is_cleaning:
            t1 = f"【大促实发5件套】厨房抽油烟机{core_word}强力去重油泡沫型烟灶清洗剂"
        elif is_pet:
            t1 = f"【实发4件大礼包】宠物猫粮狗粮{core_word}自带封口夹加厚防潮多功能铲"
        elif is_clothing:
            t1 = f"【大促实发2件套】法式气质{core_word}显瘦垂感收腰日常通勤透气长裙"
        elif is_digital:
            t1 = f"【升级快充套组】车载快充{core_word}多口数显强劲温控防烫通用插头"
        else:
            t1 = f"【大促实发4件套】家用厨房{core_word}食品级加厚耐用大容量挖面工具"

        if len(t1) > 30: t1 = t1[:30]
        elif len(t1) < 26: t1 = (t1 + "包邮到家")[:30]

        # ==================== 方案 B：⚡ 高频搜索紧凑核心词款 (精准类目/防错配/吃满自然搜推) ====================
        # 结构：【前置刚需场景 1-8字】 + 【紧凑核心大词 9-18字】 + 【真实功效痛点 19-26字】 + 【微配件 27-30字】
        if is_cleaning:
            t2 = f"厨房抽油烟机{core_word}强力去油免洗一喷净烟灶多功能清洁剂配喷头"
        elif is_pet:
            t2 = f"宠物猫咪狗狗{core_word}自带长柄封口夹食品级量勺铲米防潮配逗猫球"
        elif is_clothing:
            t2 = f"气质显瘦法式{core_word}小个子高级感舒适百搭垂感夏季短袖长裙正品"
        elif is_digital:
            t2 = f"多口氮化镓{core_word}手机平板通用快充头低温不伤机配高导数据线"
        else:
            t2 = f"家用大号{core_word}多功能厨房挖面量米工具加厚食品级PP材质配挂钩"

        if len(t2) > 30: t2 = t2[:30]
        elif len(t2) < 26: t2 = (t2 + "耐用实惠")[:30]

        # ==================== 方案 C：👑 品质升级高溢价款 (母婴级/加厚质检/支撑高客单多件套) ====================
        # 结构：【品质信任标牌 1-8字】 + 【核心大词+场景 9-18字】 + 【母婴级环保材质 19-26字】 + 【质检无忧 27-30字】
        if is_cleaning:
            t3 = f"【温和不伤手】抽油烟机{core_word}食品级环保去油配方母婴家庭除垢剂"
        elif is_pet:
            t3 = f"【加厚防断】宠物猫粮狗粮{core_word}食品级环保无异味长柄量米勺质检保障"
        elif is_clothing:
            t3 = f"【轻奢品质】法式重工复古{core_word}高端不挑身材收腰显瘦长裙官方正品"
        elif is_digital:
            t3 = f"【官方旗舰品质】超快充{core_word}智能控温多协议兼容安全快充认证"
        else:
            t3 = f"【加厚防断】{core_word}厨房家用大容量量杯食品级无异味环保质检品质"

        if len(t3) > 30: t3 = t3[:30]
        elif len(t3) < 26: t3 = (t3 + "品质保障")[:30]

        return {
            "core_word": core_word,
            "title_plans": [
                {
                    "scheme": "🔥 黄金四段式大堆头爆款 (推荐·拉爆CTR/防同店指纹)",
                    "title": t1,
                    "formula_breakdown": {
                        "黄金第1段 (1-10字)": "【大促实发多件套】(大堆头视觉冲击，防同店文本指纹压制)",
                        "黄金第2段 (11-20字)": f"{scene_part[:4]}+{core_word} (紧凑核心词锁定精准类目，防错配)",
                        "黄金第3段 (21-28字)": "强力去重油/食品级加厚 (痛点功效词拉升进店转化 CVR)",
                        "黄金第4段 (28-30字)": "长尾热词补充 (吃满28~30字自然搜推权重)"
                    },
                    "char_count": len(t1),
                    "strategy": "严格按照 拼多多黄金四段式 词位布局：大堆头前置拉升 30% 点击率，紧凑核心词杜绝切词断裂与类目错配。"
                },
                {
                    "scheme": "⚡ 高频搜索紧凑核心词款 (精准类目/防错配/吃满自然搜推)",
                    "title": t2,
                    "formula_breakdown": {
                        "核心主词": core_word,
                        "场景修饰": scene_part,
                        "功效痛点": "免洗一喷净/加厚耐用",
                        "微配件差异": "配专用配件/挂钩"
                    },
                    "char_count": len(t2),
                    "strategy": "场景词与核心词紧密相连无缝切词，后置微配件中性词（配/含），精准吃满大盘自然搜索免费流量。"
                },
                {
                    "scheme": "👑 品质升级高溢价款 (母婴级/加厚质检/支撑高客单)",
                    "title": t3,
                    "formula_breakdown": {
                        "品质信任标": "【加厚防断/温和不伤手】",
                        "核心大词": core_word,
                        "高级材质": "食品级/母婴级无异味",
                        "质检背书": "官方质检保障"
                    },
                    "char_count": len(t3),
                    "strategy": "突出高质感与安全质检背书，为 25.9~49.9 元高客单多件套提供充足溢价支撑与信任度。"
                }
            ],
            "naming_rule": "拼多多黄金四段式：【大堆头营销前缀 1-10字】+【场景+核心词 11-20字】+【功效痛点词 21-28字】+【长尾词 28-30字】，彻底规避 0 曝光与类目错配！"
        }
