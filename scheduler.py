import os
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from main import roles_tasks
from analysts import judge_decision

# 加载环境变量
load_dotenv()

# 邮件配置
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

def send_email(subject, body):
    """发送邮件函数"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # 使用SSL连接SMTP服务器（适用于465端口）
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def analyze_token(token_code):
    """分析单个加密货币并返回结果"""
    analysis_results = {}
    for role, func in roles_tasks.items():
        if role in ["研究主管", "投资组合管理者"]:
            continue
        try:
            analysis_results[role] = func(token_code)
        except Exception as e:
            analysis_results[role] = f"分析失败: {str(e)}"

    try:
        final_decision = judge_decision(analysis_results, token_code)
        return f"【{token_code} 分析报告】\n{final_decision}\n\n"
    except Exception as e:
        return f"【{token_code} 分析失败】\n错误信息: {str(e)}\n\n"

def analyze_multiple_tokens(tokens):
    """分析多个加密货币并发送邮件"""
    results = []
    for token in tokens:
        results.append(analyze_token(token))

    combined_report = "\n".join(results)
    send_email("每日加密货币分析报告", combined_report)

def main():
    # 从环境变量读取需要分析的加密货币代码
    tokens_str = os.getenv('ANALYSIS_TOKENS', 'BTC,ETH,SOL,ADA')
    tokens = [token.strip() for token in tokens_str.split(',')]

    # 创建调度器
    scheduler = BlockingScheduler()

    # 程序启动时立即执行一次
    analyze_multiple_tokens(tokens)

    # 添加定时任务：每天执行时间（可修改hour参数调整）
    # 格式说明：hour='0,4,8,12,16,20' 表示每天0/4/8/12/16/20点执行
    # 如需修改时间，修改hour参数即可，例如：hour='1,5,9,13,17,21' 表示每天1/5/9/13/17/21点执行
    scheduler.add_job(
        analyze_multiple_tokens,
        trigger='cron',
        hour='0,4,8,12,16,20',  # 执行时间配置处
        minute=0,
        second=0,
        args=[tokens]
    )

    print("定时任务已启动，按Ctrl+C停止...")
    scheduler.start()

if __name__ == "__main__":
    main()