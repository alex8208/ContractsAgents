# main.py

from analysts import (
    market_report, sentiment_report, news_report, fundamentals_report,
    bull_history, bear_history, research_manager_report, trader_investment_plan,
    risky_history, safe_history, neutral_history, judge_decision
)

roles_tasks = {
    "市场分析师": market_report,
    "社交分析师": sentiment_report,
    "新闻分析师": news_report,
    "基本面分析师": fundamentals_report,
    "多头研究员": bull_history,
    "空头研究员": bear_history,
    "研究经理": research_manager_report,
    "交易员": trader_investment_plan,
    "激进风险分析师": risky_history,
    "保守风险分析师": safe_history,
    "中立风险分析师": neutral_history,
    "研究主管": judge_decision,
    "投资组合管理者": judge_decision
}

def main():
    token_code = input("请输入加密货币代码或合约地址：")
    analysis_results = {}

    for role, func in roles_tasks.items():
        if role in ["研究主管", "投资组合管理者"]:
            continue  # 最终决策后面统一处理
        print(f"[{role}] 正在推理中，请稍候...")
        analysis_results[role] = func(token_code)

    # 输出各角色分析
    for role, result in analysis_results.items():
        print(f"{role}：{result}")

    print("[研究主管/投资组合管理者] 正在综合分析，请稍候...")
    # 最终决策
    final_decision = judge_decision(analysis_results, token_code)
    print("\n" + "="*30)
    print("最终合约购买方案：", final_decision)
    print("="*30)

if __name__ == "__main__":
    main() 