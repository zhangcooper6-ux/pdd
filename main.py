"""
全域电商经营助手 - 主入口程序
支持交互式菜单、数据文件载入、全域指标计算、多维归因诊断、HTML大屏生成与Markdown行动看板导出
"""

import os
import sys
import argparse
import pandas as pd

if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# 引入项目模块
from ecommerce_assistant.analyzer import MetricNormalizer, OmnichannelAnalyzer
from ecommerce_assistant.data_generator import generate_omnichannel_dataset
from ecommerce_assistant.reporter import ReportGenerator

def print_banner():
    banner = """
========================================================================
       🚀 全域电商经营助手 (Omnichannel Commerce Assistant)
       统一天猫、京东、抖音、拼多多四平台口径 · 全链路漏斗 · 归因诊断 · 经营策略
========================================================================
    """
    print(banner)

def load_data(file_path: str) -> pd.DataFrame:
    """自动判断格式载入数据"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"未找到指定数据文件: {file_path}")
    
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        # 优先读取四平台经营明细或三平台经营明细，否则读取第一页
        try:
            df = pd.read_excel(file_path, sheet_name='四平台经营明细')
        except:
            try:
                df = pd.read_excel(file_path, sheet_name='三平台经营明细')
            except:
                df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='gbk')
    else:
        raise ValueError("不支持的文件格式，请提供 .xlsx, .xls 或 .csv 文件。")
    return df

def run_pipeline(data_path: str, output_dir: str = "d:/pddyy/ecommerce_assistant/output"):
    print(f"\n📂 正在载入并统一口径处理数据: {data_path} ...")
    df = load_data(data_path)
    print(f"✅ 成功载入数据，包含 {len(df)} 条记录，覆盖渠道: {list(df['channel'].unique())}")
    
    # 初始化分析引擎
    analyzer = OmnichannelAnalyzer(df)
    
    print("\n🔍 正在计算各平台核心大盘汇总指标...")
    summary = analyzer.get_channel_summary()
    
    print("\n---------------- 各平台经营大盘指标对比 ----------------")
    display_cols = ['channel', 'net_gmv', 'cvr', 'aov', 'refund_rate', 'roas', 'contribution_margin', 'repeat_rate']
    formatted_summary = summary[display_cols].copy()
    formatted_summary['net_gmv'] = formatted_summary['net_gmv'].apply(lambda x: f"¥{x:,.2f}")
    formatted_summary['cvr'] = formatted_summary['cvr'].apply(lambda x: f"{x:.2%}")
    formatted_summary['aov'] = formatted_summary['aov'].apply(lambda x: f"¥{x:.2f}")
    formatted_summary['refund_rate'] = formatted_summary['refund_rate'].apply(lambda x: f"{x:.2%}")
    formatted_summary['roas'] = formatted_summary['roas'].apply(lambda x: f"{x:.2f}")
    formatted_summary['contribution_margin'] = formatted_summary['contribution_margin'].apply(lambda x: f"{x:.2%}")
    formatted_summary['repeat_rate'] = formatted_summary['repeat_rate'].apply(lambda x: f"{x:.2%}")
    
    formatted_summary.columns = ['渠道', '净销售额(Net GMV)', '转化率(CVR)', '客单价(AOV)', '退款率', '商业化ROAS', '边际贡献率', '复购率']
    print(formatted_summary.to_string(index=False))
    print("---------------------------------------------------------")
    
    print("\n📈 正在解析商品货盘结构与四象限矩阵...")
    skus = analyzer.get_product_portfolio_analysis()
    
    print("\n🧠 正在进行三维深度归因（平台差异、商品结构硬伤、运营动作偏差）...")
    diagnostics = analyzer.diagnose_and_attribute()
    
    print("\n🎨 正在生成全域电商经营大屏与行动看板...")
    reporter = ReportGenerator(summary, analyzer.get_funnel_comparison(), skus, diagnostics)
    
    html_path = os.path.join(output_dir, "omnichannel_dashboard.html")
    md_path = os.path.join(output_dir, "action_board_7_14_30.md")
    
    reporter.generate_html_dashboard(html_path)
    reporter.generate_markdown_action_board(md_path)
    
    print("\n========================================================")
    print("🎉 分析与诊断已圆满完成！输出文件已生成：")
    print(f"1. 📊 交互式HTML大屏报告: {html_path}")
    print(f"2. 📝 7/14/30天经营调优行动看板: {md_path}")
    print("========================================================\n")

def main():
    print_banner()
    
    default_sample_path = "d:/pddyy/ecommerce_assistant/data/sample_omnichannel_data.csv"
    
    # 检查是否已有数据，若无则自动生成
    if not os.path.exists(default_sample_path):
        print("💡 初次运行，自动在本地生成标准全域电商模拟数据集与Excel模版...")
        generate_omnichannel_dataset(default_sample_path)
        
    parser = argparse.ArgumentParser(description="全域电商经营助手 - 天猫、京东、抖音多平台分析诊断程序")
    parser.add_argument("--data", type=str, default=default_sample_path, help="经营数据文件路径 (csv 或 xlsx)")
    parser.add_argument("--output", type=str, default="d:/pddyy/ecommerce_assistant/output", help="输出报告目录")
    parser.add_argument("--generate-sample", action="store_true", help="重新生成示例数据与Excel模板")
    
    args = parser.parse_args()
    
    if args.generate_sample:
        generate_omnichannel_dataset(default_sample_path)
        return
        
    run_pipeline(args.data, args.output)

if __name__ == "__main__":
    main()
