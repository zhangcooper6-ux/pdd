"""
全域电商经营助手 - 前后端分离 RESTful API 服务
支持 天猫、京东、抖音、拼多多 四平台经营分析、数据上传与动态诊断
"""

import os
import io
import pandas as pd
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from ecommerce_assistant.analyzer import MetricNormalizer, OmnichannelAnalyzer
from ecommerce_assistant.data_generator import generate_omnichannel_dataset
from ecommerce_assistant.pdd_copier import PddProductAnalyzer
from ecommerce_assistant.pricing_calculator import EcommercePricingCalculator
from pydantic import BaseModel

app = FastAPI(
    title="全域电商经营助手 API",
    description="支持天猫、京东、抖音、拼多多四平台经营诊断与前后端分离系统",
    version="2.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_CSV = os.path.join(BASE_DIR, "ecommerce_assistant", "data", "sample_omnichannel_data.csv")
DATA_FILE_XLSX = os.path.join(BASE_DIR, "ecommerce_assistant", "data", "sample_omnichannel_data.xlsx")
WEB_DIR = os.path.join(BASE_DIR, "web")

def load_current_dataset() -> pd.DataFrame:
    """加载当前生效的数据集，若不存在则初始化生成四平台数据"""
    if not os.path.exists(DATA_FILE_CSV):
        return generate_omnichannel_dataset(DATA_FILE_CSV)
    try:
        return pd.read_csv(DATA_FILE_CSV, encoding='utf-8-sig')
    except UnicodeDecodeError:
        return pd.read_csv(DATA_FILE_CSV, encoding='gbk')

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0", "channels": ["天猫", "京东", "抖音", "拼多多"]}

@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """获取四平台核心经营大盘总览指标"""
    df = load_current_dataset()
    analyzer = OmnichannelAnalyzer(df)
    summary_df = analyzer.get_channel_summary()
    
    # 转换为前端友好的字典列表
    records = summary_df.to_dict(orient="records")
    
    # 汇总全网大盘总量
    total_net_gmv = float(summary_df['net_gmv'].sum())
    total_gmv = float(summary_df['gmv'].sum())
    total_visitors = int(summary_df['visitors'].sum())
    total_orders = int(summary_df['paid_orders'].sum())
    total_ad_spend = float(summary_df['ad_spend'].sum())
    total_refund = float(summary_df['refund_amount'].sum())
    
    overall = {
        "total_net_gmv": round(total_net_gmv, 2),
        "total_gmv": round(total_gmv, 2),
        "total_visitors": total_visitors,
        "total_orders": total_orders,
        "total_ad_spend": round(total_ad_spend, 2),
        "total_refund": round(total_refund, 2),
        "overall_refund_rate": round(total_refund / total_gmv, 4) if total_gmv > 0 else 0,
        "overall_roas": round(total_gmv / total_ad_spend, 2) if total_ad_spend > 0 else 0,
        "overall_cvr": round(int(summary_df['paid_buyers'].sum()) / total_visitors, 4) if total_visitors > 0 else 0
    }
    
    return {
        "success": True,
        "overall": overall,
        "channel_summaries": records
    }

@app.get("/api/dashboard/funnels")
async def get_funnels():
    """获取各平台关键转化漏斗对比"""
    df = load_current_dataset()
    analyzer = OmnichannelAnalyzer(df)
    funnels = analyzer.get_funnel_comparison()
    return {
        "success": True,
        "funnels": funnels
    }

@app.get("/api/dashboard/skus")
async def get_skus(channel: Optional[str] = None):
    """获取商品结构明细与波士顿矩阵四象限分类"""
    df = load_current_dataset()
    analyzer = OmnichannelAnalyzer(df)
    sku_df = analyzer.get_product_portfolio_analysis()
    
    if channel and channel != "全部":
        sku_df = sku_df[sku_df['channel'] == channel]
        
    return {
        "success": True,
        "count": len(sku_df),
        "skus": sku_df.to_dict(orient="records")
    }

@app.get("/api/dashboard/diagnostics")
async def get_diagnostics():
    """获取多维归因诊断、机会清单与 7/14/30 天调优方案"""
    df = load_current_dataset()
    analyzer = OmnichannelAnalyzer(df)
    diag = analyzer.diagnose_and_attribute()
    return {
        "success": True,
        "diagnostics": diag
    }

@app.post("/api/data/reset")
async def reset_sample_data():
    """重新生成四平台标准基准数据"""
    df = generate_omnichannel_dataset(DATA_FILE_CSV)
    return {
        "success": True,
        "message": "已重置并生成天猫、京东、抖音、拼多多四平台标准经营数据",
        "rows": len(df)
    }

@app.post("/api/data/upload")
async def upload_custom_data(file: UploadFile = File(...)):
    """上传自定义 CSV 或 Excel 经营数据进行全域解析"""
    filename = file.filename.lower()
    if not (filename.endswith(".csv") or filename.endswith(".xlsx") or filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="仅支持上传 CSV 或 Excel (.xlsx/.xls) 格式文件")
    
    content = await file.read()
    try:
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(content), encoding='gbk')
        else:
            # 读取 Excel 第一个工作表
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    # 验证必要基础字段
    required_cols = ["channel", "sku_id", "sku_name", "visitors", "paid_orders", "gmv"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"上传数据缺少核心必要字段: {', '.join(missing)}")
    
    # 补齐缺省数值列
    optional_defaults = {
        "impressions": 0, "product_views": 0, "cart_uv": 0,
        "paid_buyers": df.get("paid_orders", 0), "paid_units": df.get("paid_orders", 0),
        "refund_amount": 0.0, "ad_spend": 0.0, "cogs": 0.0, "repeat_buyers": 0,
        "category": "常规品类", "price_band": "普通价格带"
    }
    for col, default_val in optional_defaults.items():
        if col not in df.columns:
            df[col] = default_val

    # 保存并覆盖当前数据文件
    os.makedirs(os.path.dirname(DATA_FILE_CSV), exist_ok=True)
    df.to_csv(DATA_FILE_CSV, index=False, encoding='utf-8-sig')
    
    return {
        "success": True,
        "message": f"成功载入自定义数据，共包含 {len(df)} 行SKU数据，覆盖渠道: {', '.join(df['channel'].unique().tolist())}"
    }

@app.get("/api/data/download-template")
async def download_template():
    """下载最新包含天猫、京东、抖音、拼多多四平台填报规范的 Excel 模板"""
    if not os.path.exists(DATA_FILE_XLSX):
        generate_omnichannel_dataset(DATA_FILE_CSV)
    return FileResponse(
        path=DATA_FILE_XLSX,
        filename="全域电商四平台经营数据填报模板.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 定义对标请求体
class BenchmarkAnalyzeRequest(BaseModel):
    url_or_text: str
    base_cost: float = 4.5
    strategy_mode: str = "micro_pay" # free_traffic, micro_pay, strong_pay
    api_key: Optional[str] = None
    custom_title: Optional[str] = None
    custom_skus: Optional[List[Dict[str, Any]]] = None
    express_fee: float = 1.8
    material_fee: float = 0.1
    labor_fee: float = 0.25
    refund_rate: float = 0.15
    insurance_fee: float = 0.0
    platform_commission_rate: float = 0.006

@app.post("/api/pdd/analyze-benchmark")
async def analyze_pdd_benchmark(req: BenchmarkAnalyzeRequest):
    """
    拼多多对标商品智能拆解与上架重塑接口
    """
    try:
        # 1. 结构化提取 (支持自定义校准的真实标题与 SKU)
        raw_info = PddProductAnalyzer.parse_product_url(
            req.url_or_text, 
            custom_skus=req.custom_skus, 
            custom_title=req.custom_title
        )
        
        # 2. 合规与违禁词排查
        compliance = PddProductAnalyzer.audit_compliance(raw_info["raw_title"], raw_info["benchmark_skus"])
        
        # 3. 标题与命名规则重塑 (严格执行四段式防比价公式: 核心词 + 长尾修饰 + 材质场景 + 防比价差异词)
        titles = PddProductAnalyzer.restructure_title_and_rules(
            category_keywords=raw_info["category_keyword"],
            selling_points=raw_info["selling_points"],
            raw_title=raw_info["raw_title"]
        )
        
        # 4. 黄金SKU矩阵与推广出价测算 (接入全局快递、包材、退率与扣点)
        sku_matrix = PddProductAnalyzer.design_golden_sku_matrix(
            base_cost=req.base_cost, 
            profit_mode=req.strategy_mode,
            express_fee=req.express_fee,
            material_fee=req.material_fee,
            labor_fee=req.labor_fee,
            refund_rate=req.refund_rate,
            insurance_fee=req.insurance_fee,
            platform_commission_rate=req.platform_commission_rate
        )

        # 4.5 精算对标卡位截流与投产压制策略
        interception = PddProductAnalyzer.calculate_interception_strategy(
            benchmark_skus=raw_info["benchmark_skus"],
            base_cost=req.base_cost,
            express_fee=req.express_fee,
            material_fee=req.material_fee,
            labor_fee=req.labor_fee,
            refund_rate=req.refund_rate,
            platform_commission_rate=req.platform_commission_rate,
            strategy_mode=req.strategy_mode,
            golden_sku_matrix=sku_matrix
        )
        sku_matrix["interception_strategy"] = interception
        
        # 5. 生图与视觉重塑提示词
        visuals = PddProductAnalyzer.generate_ai_visual_prompts(titles["title_plans"][0]["title"], raw_info["selling_points"])
        
        # 6. 生成拼多多合规上架MMS数据
        mms_data = PddProductAnalyzer.generate_pdd_import_schema(titles["title_plans"][0]["title"], sku_matrix["skus"])
        
        # 7. 可选调用 DeepSeek
        deepseek_res = None
        if req.api_key:
            deepseek_res = PddProductAnalyzer.call_deepseek_refine(
                f"请针对对标商品【{raw_info['raw_title']}】，结合微付费/强付费起爆SOP，生成一套更具杀伤力的高点击差异化卖点和评价引流方案。",
                req.api_key
            )

        return {
            "success": True,
            "data": {
                "raw_benchmark_info": raw_info,
                "compliance_audit": compliance,
                "title_plans": titles["title_plans"],
                "naming_rule": titles["naming_rule"],
                "golden_sku_matrix": sku_matrix,
                "interception_strategy": interception,
                "activity_plan": sku_matrix["activity_plan"],
                "visual_prompts": visuals,
                "pdd_open_api_schema": mms_data,
                "deepseek_refine": deepseek_res
            }
        }
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print("ERROR IN analyze_pdd_benchmark:\n", err_msg)
        return {"success": False, "error": str(e), "traceback": err_msg}

@app.post("/api/pdd/export-import-file")
async def export_pdd_import_file(data: Dict[str, Any]):
    """
    导出拼多多官方支持的直接铺货上架 CSV / Excel
    """
    rows = []
    # 兼容来自前端整体分析对象或直传 pdd_open_api_schema
    schema = data.get("pdd_open_api_schema", data)
    title = schema.get("goods_name", "拼多多爆款新品")
    for sku in schema.get("sku_list", []):
        rows.append({
            "商品名称": title,
            "规格名称": sku.get("spec_name"),
            "单买价(元)": round(sku.get("price", 0) / 100, 2),
            "拼单价(元)": round(sku.get("multi_price", 0) / 100, 2),
            "库存": sku.get("quantity", 9999),
            "商家编码": sku.get("out_sku_sn"),
            "发货时效": "48小时",
            "是否包邮": "是"
        })
    df = pd.DataFrame(rows)
    export_path = os.path.join(BASE_DIR, "ecommerce_assistant", "output", "pdd_goods_upload.csv")
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    df.to_csv(export_path, index=False, encoding="utf-8-sig")
    return FileResponse(path=export_path, filename="pdd_goods_upload.csv", media_type="text/csv")

@app.get("/api/readme")
async def get_readme_content():
    """获取本地 README.md 内容供前端在线 Markdown 阅读器渲染"""
    readme_path = os.path.join(BASE_DIR, "README.md")
    if not os.path.exists(readme_path):
        raise HTTPException(status_code=404, detail="README.md 文件不存在")
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"success": True, "content": content}

@app.get("/api/pdd/download-sop")
async def download_pdd_sop_doc():
    """下载拼多多爆款 SOP 全景指南 Markdown 文档"""
    sop_path = os.path.join(BASE_DIR, "拼多多高阶运营与新链接无基础销量起爆_SOP全景指南.md")
    if not os.path.exists(sop_path):
        raise HTTPException(status_code=404, detail="SOP文件不存在")
    return FileResponse(path=sop_path, filename="拼多多高阶运营与新链接无基础销量起爆_SOP全景指南.md", media_type="text/markdown")

# 定义算价请求体
class SinglePricingRequest(BaseModel):
    sku_name: str = "默认规格"
    sku_qty: int = 1
    unit_cost: float = 1.0
    selling_price: float = 9.9
    express_fee: float = 1.8
    material_fee: float = 0.1
    labor_fee: float = 0.25
    refund_rate: float = 0.15
    insurance_fee: float = 0.0
    platform_commission_rate: float = 0.006
    coupon_amount: float = 2.0
    discount_rate: float = 0.7
    actual_roas: Optional[float] = None

class BatchPricingRequest(BaseModel):
    skus: List[Dict[str, Any]]
    common_express: float = 1.8
    common_material: float = 0.1
    common_labor: float = 0.25
    common_refund_rate: float = 0.15
    common_insurance: float = 0.0
    common_commission_rate: float = 0.006
    target_roas: Optional[float] = None

@app.post("/api/pricing/calculate-single")
async def calculate_single_pricing(req: SinglePricingRequest):
    """单 SKU 极速在线算价 API"""
    res = EcommercePricingCalculator.calculate_single_sku(
        sku_name=req.sku_name,
        sku_qty=req.sku_qty,
        unit_cost=req.unit_cost,
        selling_price=req.selling_price,
        express_fee=req.express_fee,
        material_fee=req.material_fee,
        labor_fee=req.labor_fee,
        refund_rate=req.refund_rate,
        insurance_fee=req.insurance_fee,
        platform_commission_rate=req.platform_commission_rate,
        coupon_amount=req.coupon_amount,
        discount_rate=req.discount_rate,
        actual_roas=req.actual_roas
    )
    return {"success": True, "data": res}

@app.post("/api/pricing/calculate-batch")
async def calculate_batch_pricing(req: BatchPricingRequest):
    """多 SKU 批量算价与日/月度利润模拟 API"""
    res = EcommercePricingCalculator.batch_calculate(
        skus_input=req.skus,
        common_express=req.common_express,
        common_material=req.common_material,
        common_labor=req.common_labor,
        common_refund_rate=req.common_refund_rate,
        common_insurance=req.common_insurance,
        common_commission_rate=req.common_commission_rate,
        target_roas=req.target_roas
    )
    return {"success": True, "data": res}

# 挂载前端静态页面 (SPA)
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 正在启动全域电商经营助手前后端独立服务: http://127.0.0.1:8888")
    uvicorn.run(app, host="127.0.0.1", port=8888)
