# analysts.py

import os
import requests
from dotenv import load_dotenv
import numpy as np
import fundingrate as fr
from taapi_client import TaapiClient

# 加载.env环境变量（本地开发用，线上可省略）
load_dotenv()

def get_env_var(name):
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"[错误] 未设置{name}环境变量，请在.env文件中配置。")
    return value

DEEPSEEK_API_KEY = get_env_var('DEEPSEEK_API_KEY')
TAAPI_SECRET = get_env_var('TAAPI_SECRET')
DEEPSEEK_API_URL = get_env_var('DEEPSEEK_API_URL')
COINGECKO_API_URL = get_env_var('COINGECKO_API_URL')
BINANCE_API_URL = get_env_var('BINANCE_API_URL')
ARKHAM_API_URL = get_env_var('ARKHAM_API_URL')
ALTERNATIVE_ME_API_URL = get_env_var('ALTERNATIVE_ME_API_URL')

market_report_prompt = (
    "你是一名加密货币市场分析师。"
    "请根据提供的实时行情数据，简明扼要输出：\n"
    "1. 当前价格（美元）- 必须使用提供的实时价格,小数点保留4位\n"
    "2. 主要阻力位、支撑位、目标价（各1个，必须有具体数值）\n"
    "3. 【宏观经济学】结合当前BTC价格、美元走势、全球主要政策变动、关税、战争去向等最新公开信息，用一句话点评宏观环境对该币种的影响\n"
    "4. 【K线信号】分4小时MACD，1天MACD，一周MACD，一个月MACD来判断是否有突破、回调、下跌通道、上升通道或震荡区间等典型买卖信号，并用一句话说明，必须给出关键价位或区间。\n"
    "5. 【心理学】结合当前社交热度和价格波动，用一句话点评市场情绪\n"
    "6. 一句简短操作建议\n"
    "重要：你必须使用提供的实时价格数据，不要使用任何过时的价格信息。请严格按照上述格式输出，不要展开分析，不要输出多余文字。"
)
sentiment_report_prompt = (
    "你是一名加密货币社交分析师。"
    "请仅根据近一周内的新闻、事件、重要人物（如美联储、特朗普等）发言，美联储政策、ETF决策、关税等，简明扼要输出：\n"
    "1. 重要新闻或事件摘要（近一周内）\n"
    "2. 用一句话总结这些新闻或事件对加密货币市场分析师给出的币价的影响（如利好、利空、中性）\n"
    "请严格按照上述格式输出，不要展开分析，不要输出多余文字。"
)
news_report_prompt = (
    "你是一名加密货币新闻分析师。"
    "请根据最新一条相关新闻，简明扼要输出：\n"
    "1. 新闻标题或主要内容（请特别关注政策变动、战争、美国非农数据等宏观新闻，需给出关键影响价位或区间）\n"
    "2. 根据当前黄金价格走势（上涨/下跌/盘整）、美股主要指数（道指、纳指、标普500）表现，一句话分析对币价的潜在影响\n"    
    "3. 用一句话总结该新闻对币价的影响（如利好、利空、中性）\n"
    "请严格按照上述格式输出，不要展开分析，不要输出多余文字。"
)
fundamentals_report_prompt = """
你是一位加密货币基本面分析师。你的任务是分析给定代币的基本面数据，并给出一个简洁的、不超过150字的总结。
你的分析应该基于以下几点：
1.  **项目基本情况**：简要介绍项目的目标、技术和价值主张。
2.  **代币经济学**：评估代币的供应、分配和效用。
3.  **市场情绪与技术指标**：结合贪婪恐惧指数、RSI（相对强弱指数）和资金费率，判断当前市场情绪和技术状态。
4.  **综合判断**：根据以上信息，对该代币的短期（1-3个月）和长期（1年以上）潜力做出评估，并明确给出“看涨”、“看跌”或“中性”的观点。

请直接输出你的分析报告，不要包含任何额外的前言或结语。
"""
bull_history_prompt = (
    "你是一名多头研究员。"
    "请用一句话总结当前多头倾向或信号，并指出关键价位或区间。"
   # "重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
bear_history_prompt = (
    "你是一名空头研究员。"
    "请用一句话总结当前空头倾向或信号，并指出关键价位或区间。"
    #"重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
research_manager_report_prompt = (
    "你是一名研究经理。"
    "请用一句话总结所有分析师报告的核心结论，需包含关键价位、区间或信号。"
    #"重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
trader_investment_plan_prompt = (
    "你是一名加密货币交易员。"
    "请用一句话给出当前最优的交易建议，并给出建议买入/卖出价位或区间。"
   # "重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
risky_history_prompt = (
    "你是一名激进风险分析师。"
    "请用一句话总结当前高风险信号或事件，并指出关键风险价位或区间。"
    #"重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
safe_history_prompt = (
    "你是一名保守风险分析师。"
    "请用一句话总结当前低风险信号或安全性，并指出关键安全价位或区间。"
    #"重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
neutral_history_prompt = (
    "你是一名中立风险分析师。"
    "请用一句话总结当前风险与机会的平衡情况，并指出关键平衡价位或区间。"
    #"重要：必须基于提供的实时价格数据进行分析，不要使用过时的价格信息。"
    "不要展开分析，不要输出多余文字。"
)
judge_decision_prompt = (
    "你是一名研究主管/投资组合管理者。"
    "请结合所有分析师的结论，综合推理得出最终的{token_code}合约购买建议，价格小数保留4位，内容包括：\n"
    "1. 建议做多买入价格（应结合前述分析师报告中的支撑位、K线区间、回调点等关键数据，合理推理，不要总是等于现价，若为挂单策略请明确说明）\n"
    "2. 做多止盈价格（具体数值）\n"
    "3. 做多止损价格（具体数值）\n"
    "4. 做多预期收益比例（如+10%）\n"
    "5. 做多最大亏损比例（如-5%）\n"
    "6. 建议做空买入价格（应与当前价格接近，若为挂单策略请明确说明）\n"
    "7. 做空止盈价格（具体数值）\n"
    "8. 做空止损价格（具体数值）\n"
    "9. 做空预期收益比例（如+10%）\n"
    "10. 做空最大亏损比例（如-5%）\n"
    "11. 一句话简要说明理由，并说明买入策略类型（现价/挂单）\n"
    "请严格参考前述分析师给出的当前价格、阻力位、支撑位、K线信号等关键数据，合理推理建议价位。"
    "建议合约做多或做空价、止盈价、止损价必须与当前价格保持合理区间，除非明确为挂单策略。"
    "请严格按照上述格式输出，不要展开分析，不要输出多余文字。"
)

# 免费获取币价等行情数据（CoinGecko）
# 全局缓存价格数据
price_cache = {}

def get_token_market_data(token_code):
    """
    获取币种实时市场数据，包括价格、市值、成交量等
    返回格式化的价格信息，确保数据准确性
    """
    # 检查缓存
    if token_code.upper() in price_cache:
        return price_cache[token_code.upper()]
        
    print(f"正在获取 {token_code} 的实时价格数据...")
    symbol_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDT': 'tether',
        'BNB': 'binancecoin',
        'DOGE': 'dogecoin',
        'SOL': 'solana',
        'ADA': 'cardano',
        'XRP': 'ripple',
        'TRX': 'tron',
        'FIL': 'filecoin',
        'AVAX': 'avalanche-2',
        'DOT': 'polkadot',
        'MATIC': 'matic-network',
        'LTC': 'litecoin',
        'UNI': 'uniswap',
        'LINK': 'chainlink',
        'ATOM': 'cosmos',
        'ETC': 'ethereum-classic',
        'XLM': 'stellar',
        'BCH': 'bitcoin-cash',
        'NEAR': 'near',
        'APT': 'aptos',
        'OP': 'optimism',
        'ARB': 'arbitrum',
        'MKR': 'maker',
        'VET': 'vechain',
        'IMX': 'immutable-x',
        'HBAR': 'hedera-hashgraph',
        'CRO': 'crypto-com-chain',
        'ALGO': 'algorand',
        'ICP': 'internet-computer',
        'THETA': 'theta-token',
        'FTM': 'fantom',
        'XMR': 'monero',
        'GRT': 'the-graph',
        'STX': 'blockstack',
        'INJ': 'injective-protocol',
        'RUNE': 'thorchain',
        'AAVE': 'aave',
        'SAND': 'the-sandbox',
        'MANA': 'decentraland',
        'GALA': 'gala',
        'CHZ': 'chiliz',
        'HOT': 'holochain',
        'ENJ': 'enjincoin',
        'FLOW': 'flow',
        'ONE': 'harmony',
        'EGLD': 'elrond-erd-2',
        'XTZ': 'tezos',
        'NEO': 'neo',
        'KSM': 'kusama',
        'WAVES': 'waves',
        'ZEC': 'zcash',
        'DASH': 'dash',
        'BAT': 'basic-attention-token',
        'COMP': 'compound-governance-token',
        'SNX': 'havven',
        'YFI': 'yearn-finance',
        'SUSHI': 'sushi',
        'CRV': 'curve-dao-token',
        '1INCH': '1inch',
        'ANKR': 'ankr',
        'ZIL': 'zilliqa',
        'QTUM': 'qtum',
        'IOTA': 'iota',
        'RVN': 'ravencoin',
        'ICX': 'icon',
        'ONT': 'ontology',
        'NANO': 'nano',
        'SC': 'siacoin',
        'DGB': 'digibyte',
        'STORJ': 'storj',
        'OMG': 'omisego',
        'ZRX': '0x',
        'REP': 'augur',
        'KNC': 'kyber-network-crystal',
        'BAND': 'band-protocol',
        'OCEAN': 'ocean-protocol',
        'ALPHA': 'alpha-finance',
        'AUDIO': 'audius',
        'RLC': 'iexec-rlc',
        'RSR': 'reserve-rights',
        'CTSI': 'cartesi',
        'API3': 'api3',
        'DENT': 'dent',
        'COTI': 'coti',
        'CFX': 'conflux-token',
        'ROSE': 'oasis-network',
        'SKL': 'skale',
        'IOTX': 'iotex',
        'ANKR': 'ankr',
        'ZEN': 'horizen',
        'DYDX': 'dydx',
        'RNDR': 'render-token',
        'MINA': 'mina-protocol',
        'ENS': 'ethereum-name-service',
        'GAL': 'galxe',
        'BLUR': 'blur',
        'SUI': 'sui',
        'SEI': 'sei-network',
        'PYTH': 'pyth-network',
        'JUP': 'jupiter',
        'WIF': 'dogwifhat',
        'BONK': 'bonk',
        'PEPE': 'pepe',
        'SHIB': 'shiba-inu',
        'FLOKI': 'floki',
        'BABYDOGE': 'babydogecoin',
        'SAFEMOON': 'safemoon',
        'MOON': 'moonshot',
        'ELON': 'dogelon-mars',
        'SAMO': 'samoyedcoin',
        'COPE': 'cope',
        'RAY': 'raydium',
        'SRM': 'serum',
        'ORCA': 'orca',
        'MNGO': 'mango-markets',
        'STEP': 'step-finance',
        'SLND': 'solend',
        'MER': 'merit-circle',
        'GMT': 'stepn',
        'GST': 'green-satoshi-token',
        'APE': 'apecoin',
        'DYDX': 'dydx',
        'PERP': 'perpetual-protocol',
        'RAD': 'radicle',
        'BADGER': 'badger-dao',
        'KP3R': 'keep3rv1',
        'HEGIC': 'hegic',
        'PICKLE': 'pickle-finance',
        'CREAM': 'cream-2',
        'ALPHA': 'alpha-finance',
        'BETA': 'beta-finance',
        'GAMMA': 'gamma-strategies',
        'DELTA': 'delta-exchange-token',
        'THETA': 'theta-token',
        'OMEGA': 'omega-protocol-money',
        'SIGMA': 'sigma-protocol',
        'LAMBDA': 'lambda',
        'PHI': 'phi',
        'PSI': 'psi',
        'CHI': 'chi-gastoken',
        'XI': 'xi-token',
        'OMICRON': 'omicron',
        'UPSILON': 'upsilon',
    }
    token_id = symbol_map.get(token_code.upper(), token_code.lower())
    url = f"{COINGECKO_API_URL}/coins/{token_id}"
    try:
        # Add rate limiting with 1 second delay between requests
        import time
        time.sleep(1)  # Respect CoinGecko's rate limits (10-30 calls/minute)
        
        # Add retry logic for 429 errors
        max_retries = 3
        for attempt in range(max_retries):
            resp = requests.get(url, timeout=10)
            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 60)  # Exponential backoff
                    time.sleep(wait_time)
                    continue
            resp.raise_for_status()
            break
            
        data = resp.json()
        price = data['market_data']['current_price']['usd']
        market_cap = data['market_data']['market_cap']['usd']
        
        # 缓存数据
        price_cache[token_code.upper()] = {
            'price': price,
            'market_cap': market_cap,
            'data': data
        }
        volume = data['market_data']['total_volume']['usd']
        last_updated = data['last_updated']
        # 社区数据
        reddit = data.get('community_data', {}).get('reddit_average_posts_48h', 'N/A')
        twitter = data.get('community_data', {}).get('twitter_followers', 'N/A')
        
        # 格式化价格显示，确保准确性
        formatted_price = f"{price:,.2f}" if price else "0.00"
        
        print(f"✅ 成功获取 {token_code} 实时价格: {formatted_price} USD")
        
        return {
            'price': price,
            'price_formatted': formatted_price,
            'market_cap': market_cap,
            'volume': volume,
            'name': data['name'],
            'symbol': data['symbol'],
            'last_updated': last_updated,
            'reddit_posts_48h': reddit,
            'twitter_followers': twitter
        }
    except Exception as e:
        return {'error': str(e)}

# 获取近30天K线最高价、最低价
def get_token_ohlc(token_code, days=30):
    symbol_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDT': 'tether',
        'BNB': 'binancecoin',
        'DOGE': 'dogecoin',
        'SOL': 'solana',
        'ADA': 'cardano',
        'XRP': 'ripple',
        'TRX': 'tron',
        'FIL': 'filecoin',
        'AVAX': 'avalanche-2',
        'DOT': 'polkadot',
        'MATIC': 'matic-network',
        'LTC': 'litecoin',
        'UNI': 'uniswap',
        'LINK': 'chainlink',
        'ATOM': 'cosmos',
        'ETC': 'ethereum-classic',
        'XLM': 'stellar',
        'BCH': 'bitcoin-cash',
        'NEAR': 'near',
        'APT': 'aptos',
        'OP': 'optimism',
        'ARB': 'arbitrum',
        'MKR': 'maker',
        'VET': 'vechain',
        'IMX': 'immutable-x',
        'HBAR': 'hedera-hashgraph',
        'CRO': 'crypto-com-chain',
        'ALGO': 'algorand',
        'ICP': 'internet-computer',
        'THETA': 'theta-token',
        'FTM': 'fantom',
        'XMR': 'monero',
        'GRT': 'the-graph',
        'STX': 'blockstack',
        'INJ': 'injective-protocol',
        'RUNE': 'thorchain',
        'AAVE': 'aave',
        'SAND': 'the-sandbox',
        'MANA': 'decentraland',
        'GALA': 'gala',
        'CHZ': 'chiliz',
        'HOT': 'holochain',
        'ENJ': 'enjincoin',
        'FLOW': 'flow',
        'ONE': 'harmony',
        'EGLD': 'elrond-erd-2',
        'XTZ': 'tezos',
        'NEO': 'neo',
        'KSM': 'kusama',
        'WAVES': 'waves',
        'ZEC': 'zcash',
        'DASH': 'dash',
        'BAT': 'basic-attention-token',
        'COMP': 'compound-governance-token',
        'SNX': 'havven',
        'YFI': 'yearn-finance',
        'SUSHI': 'sushi',
        'CRV': 'curve-dao-token',
        '1INCH': '1inch',
        'ANKR': 'ankr',
        'ZIL': 'zilliqa',
        'QTUM': 'qtum',
        'IOTA': 'iota',
        'RVN': 'ravencoin',
        'ICX': 'icon',
        'ONT': 'ontology',
        'NANO': 'nano',
        'SC': 'siacoin',
        'DGB': 'digibyte',
        'STORJ': 'storj',
        'OMG': 'omisego',
        'ZRX': '0x',
        'REP': 'augur',
        'KNC': 'kyber-network-crystal',
        'BAND': 'band-protocol',
        'OCEAN': 'ocean-protocol',
        'ALPHA': 'alpha-finance',
        'AUDIO': 'audius',
        'RLC': 'iexec-rlc',
        'RSR': 'reserve-rights',
        'CTSI': 'cartesi',
        'API3': 'api3',
        'DENT': 'dent',
        'COTI': 'coti',
        'CFX': 'conflux-token',
        'ROSE': 'oasis-network',
        'SKL': 'skale',
        'IOTX': 'iotex',
        'ANKR': 'ankr',
        'ZEN': 'horizen',
        'DYDX': 'dydx',
        'RNDR': 'render-token',
        'MINA': 'mina-protocol',
        'ENS': 'ethereum-name-service',
        'GAL': 'galxe',
        'BLUR': 'blur',
        'SUI': 'sui',
        'SEI': 'sei-network',
        'PYTH': 'pyth-network',
        'JUP': 'jupiter',
        'WIF': 'dogwifhat',
        'BONK': 'bonk',
        'PEPE': 'pepe',
        'SHIB': 'shiba-inu',
        'FLOKI': 'floki',
        'BABYDOGE': 'babydogecoin',
        'SAFEMOON': 'safemoon',
        'MOON': 'moonshot',
        'ELON': 'dogelon-mars',
        'SAMO': 'samoyedcoin',
        'COPE': 'cope',
        'RAY': 'raydium',
        'SRM': 'serum',
        'ORCA': 'orca',
        'MNGO': 'mango-markets',
        'STEP': 'step-finance',
        'SLND': 'solend',
        'MER': 'merit-circle',
        'GMT': 'stepn',
        'GST': 'green-satoshi-token',
        'APE': 'apecoin',
        'DYDX': 'dydx',
        'PERP': 'perpetual-protocol',
        'RAD': 'radicle',
        'BADGER': 'badger-dao',
        'KP3R': 'keep3rv1',
        'HEGIC': 'hegic',
        'PICKLE': 'pickle-finance',
        'CREAM': 'cream-2',
        'ALPHA': 'alpha-finance',
        'BETA': 'beta-finance',
        'GAMMA': 'gamma-strategies',
        'DELTA': 'delta-exchange-token',
        'THETA': 'theta-token',
        'OMEGA': 'omega-protocol-money',
        'SIGMA': 'sigma-protocol',
        'LAMBDA': 'lambda',
        'PHI': 'phi',
        'PSI': 'psi',
        'CHI': 'chi-gastoken',
        'XI': 'xi-token',
        'OMICRON': 'omicron',
        'UPSILON': 'upsilon',
    }
    token_id = symbol_map.get(token_code.upper(), token_code.lower())
    url = f"{COINGECKO_API_URL}/coins/{token_id}/ohlc?vs_currency=usd&days={days}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return {'error': '无K线数据'}
        highs = [item[2] for item in data]
        lows = [item[3] for item in data]
        return {
            'max_high': max(highs),
            'min_low': min(lows)
        }
    except Exception as e:
        return {'error': str(e)}

# 免费获取相关新闻（CoinGecko status_updates）
def get_token_news(token_code):
    symbol_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDT': 'tether',
        'BNB': 'binancecoin',
        'DOGE': 'dogecoin',
        'SOL': 'solana',
        'ADA': 'cardano',
        'XRP': 'ripple',
        'TRX': 'tron',
        'FIL': 'filecoin',
        'AVAX': 'avalanche-2',
        'DOT': 'polkadot',
        'MATIC': 'matic-network',
        'LTC': 'litecoin',
        'UNI': 'uniswap',
        'LINK': 'chainlink',
        'ATOM': 'cosmos',
        'ETC': 'ethereum-classic',
        'XLM': 'stellar',
        'BCH': 'bitcoin-cash',
        'NEAR': 'near',
        'APT': 'aptos',
        'OP': 'optimism',
        'ARB': 'arbitrum',
        'MKR': 'maker',
        'VET': 'vechain',
        'IMX': 'immutable-x',
        'HBAR': 'hedera-hashgraph',
        'CRO': 'crypto-com-chain',
        'ALGO': 'algorand',
        'ICP': 'internet-computer',
        'THETA': 'theta-token',
        'FTM': 'fantom',
        'XMR': 'monero',
        'GRT': 'the-graph',
        'STX': 'blockstack',
        'INJ': 'injective-protocol',
        'RUNE': 'thorchain',
        'AAVE': 'aave',
        'SAND': 'the-sandbox',
        'MANA': 'decentraland',
        'GALA': 'gala',
        'CHZ': 'chiliz',
        'HOT': 'holochain',
        'ENJ': 'enjincoin',
        'FLOW': 'flow',
        'ONE': 'harmony',
        'EGLD': 'elrond-erd-2',
        'XTZ': 'tezos',
        'NEO': 'neo',
        'KSM': 'kusama',
        'WAVES': 'waves',
        'ZEC': 'zcash',
        'DASH': 'dash',
        'BAT': 'basic-attention-token',
        'COMP': 'compound-governance-token',
        'SNX': 'havven',
        'YFI': 'yearn-finance',
        'SUSHI': 'sushi',
        'CRV': 'curve-dao-token',
        '1INCH': '1inch',
        'ANKR': 'ankr',
        'ZIL': 'zilliqa',
        'QTUM': 'qtum',
        'IOTA': 'iota',
        'RVN': 'ravencoin',
        'ICX': 'icon',
        'ONT': 'ontology',
        'NANO': 'nano',
        'SC': 'siacoin',
        'DGB': 'digibyte',
        'STORJ': 'storj',
        'OMG': 'omisego',
        'ZRX': '0x',
        'REP': 'augur',
        'KNC': 'kyber-network-crystal',
        'BAND': 'band-protocol',
        'OCEAN': 'ocean-protocol',
        'ALPHA': 'alpha-finance',
        'AUDIO': 'audius',
        'RLC': 'iexec-rlc',
        'RSR': 'reserve-rights',
        'CTSI': 'cartesi',
        'API3': 'api3',
        'DENT': 'dent',
        'COTI': 'coti',
        'CFX': 'conflux-token',
        'ROSE': 'oasis-network',
        'SKL': 'skale',
        'IOTX': 'iotex',
        'ANKR': 'ankr',
        'ZEN': 'horizen',
        'DYDX': 'dydx',
        'RNDR': 'render-token',
        'MINA': 'mina-protocol',
        'ENS': 'ethereum-name-service',
        'GAL': 'galxe',
        'BLUR': 'blur',
        'SUI': 'sui',
        'SEI': 'sei-network',
        'PYTH': 'pyth-network',
        'JUP': 'jupiter',
        'WIF': 'dogwifhat',
        'BONK': 'bonk',
        'PEPE': 'pepe',
        'SHIB': 'shiba-inu',
        'FLOKI': 'floki',
        'BABYDOGE': 'babydogecoin',
        'SAFEMOON': 'safemoon',
        'MOON': 'moonshot',
        'ELON': 'dogelon-mars',
        'SAMO': 'samoyedcoin',
        'COPE': 'cope',
        'RAY': 'raydium',
        'SRM': 'serum',
        'ORCA': 'orca',
        'MNGO': 'mango-markets',
        'STEP': 'step-finance',
        'SLND': 'solend',
        'MER': 'merit-circle',
        'GMT': 'stepn',
        'GST': 'green-satoshi-token',
        'APE': 'apecoin',
        'DYDX': 'dydx',
        'PERP': 'perpetual-protocol',
        'RAD': 'radicle',
        'BADGER': 'badger-dao',
        'KP3R': 'keep3rv1',
        'HEGIC': 'hegic',
        'PICKLE': 'pickle-finance',
        'CREAM': 'cream-2',
        'ALPHA': 'alpha-finance',
        'BETA': 'beta-finance',
        'GAMMA': 'gamma-strategies',
        'DELTA': 'delta-exchange-token',
        'THETA': 'theta-token',
        'OMEGA': 'omega-protocol-money',
        'SIGMA': 'sigma-protocol',
        'LAMBDA': 'lambda',
        'PHI': 'phi',
        'PSI': 'psi',
        'CHI': 'chi-gastoken',
        'XI': 'xi-token',
        'OMICRON': 'omicron',
        'UPSILON': 'upsilon',
    }
    token_id = symbol_map.get(token_code.upper(), token_code.lower())
    url = f"{COINGECKO_API_URL}/coins/{token_id}/status_updates"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        updates = data.get('status_updates', [])
        if not updates:
            return '暂无相关新闻动态。'
        # 取最新1条
        item = updates[0]
        return f"[{item['created_at']}] {item['user']}：{item['description']}"
    except Exception as e:
        return f'获取新闻失败：{e}'

# 免费获取社交热度（CoinGecko社区数据）
def get_token_social(token_code):
    data = get_token_market_data(token_code)
    if 'error' in data:
        return f"获取社交数据失败：{data['error']}"
    return (
        f"Reddit近48小时发帖数：{data['reddit_posts_48h']}，"
        f"Twitter关注者数：{data['twitter_followers']}"
    )

def call_deepseek(prompt):
    if not DEEPSEEK_API_KEY:
        return "[错误] 未设置DEEPSEEK_API_KEY环境变量。"
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"[DeepSeek API调用失败] {e}"

def get_binance_4h_klines(symbol="BTCUSDT", limit=100):
    """
    获取币安4小时K线数据，默认100根（约16天）。symbol如BTCUSDT。
    返回收盘价列表。
    """
    url = f"{BINANCE_API_URL}/klines?symbol={symbol}&interval=4h&limit={limit}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        closes = [float(item[4]) for item in data]  # 收盘价
        return closes
    except Exception as e:
        return []


def calc_macd(close_list, fast=12, slow=26, signal=9):
    """
    计算MACD指标，返回macd, signal, hist最新值。
    """
    if len(close_list) < slow + signal:
        return None, None, None
    close = np.array(close_list)
    ema_fast = np.zeros_like(close)
    ema_slow = np.zeros_like(close)
    ema_fast[0] = close[0]
    ema_slow[0] = close[0]
    alpha_fast = 2 / (fast + 1)
    alpha_slow = 2 / (slow + 1)
    for i in range(1, len(close)):
        ema_fast[i] = alpha_fast * close[i] + (1 - alpha_fast) * ema_fast[i-1]
        ema_slow[i] = alpha_slow * close[i] + (1 - alpha_slow) * ema_slow[i-1]
    diff = ema_fast - ema_slow
    dea = np.zeros_like(diff)
    dea[0] = diff[0]
    alpha_signal = 2 / (signal + 1)
    for i in range(1, len(diff)):
        dea[i] = alpha_signal * diff[i] + (1 - alpha_signal) * dea[i-1]
    macd = diff - dea
    return diff[-1], dea[-1], macd[-1]


def get_macd_signal(token_code):
    """
    获取币种4小时MACD指标及多空信号。
    """
    symbol_map = {
        'BTC': 'BTCUSDT',
        'ETH': 'ETHUSDT',
        'BNB': 'BNBUSDT',
        'DOGE': 'DOGEUSDT',
        'SOL': 'SOLUSDT',
        'ADA': 'ADAUSDT',
        'XRP': 'XRPUSDT',
        'TRX': 'TRXUSDT',
        'FIL': 'FILUSDT',
        'AVAX': 'AVAXUSDT',
        'DOT': 'DOTUSDT',
        'MATIC': 'MATICUSDT',
        'LTC': 'LTCUSDT',
        'UNI': 'UNIUSDT',
        'LINK': 'LINKUSDT',
        'ATOM': 'ATOMUSDT',
        'ETC': 'ETCUSDT',
        'XLM': 'XLMUSDT',
        'BCH': 'BCHUSDT',
        'NEAR': 'NEARUSDT',
        'APT': 'APTUSDT',
        'OP': 'OPUSDT',
        'ARB': 'ARBUSDT',
        'MKR': 'MKRUSDT',
        'VET': 'VETUSDT',
        'IMX': 'IMXUSDT',
        'HBAR': 'HBARUSDT',
        'CRO': 'CROUSDT',
        'ALGO': 'ALGOUSDT',
        'ICP': 'ICPUSDT',
        'THETA': 'THETAUSDT',
        'FTM': 'FTMUSDT',
        'XMR': 'XMRUSDT',
        'GRT': 'GRTUSDT',
        'STX': 'STXUSDT',
        'INJ': 'INJUSDT',
        'RUNE': 'RUNEUSDT',
        'AAVE': 'AAVEUSDT',
        'SAND': 'SANDUSDT',
        'MANA': 'MANAUSDT',
        'GALA': 'GALAUSDT',
        'CHZ': 'CHZUSDT',
        'HOT': 'HOTUSDT',
        'ENJ': 'ENJUSDT',
        'FLOW': 'FLOWUSDT',
        'ONE': 'ONEUSDT',
        'EGLD': 'EGLDUSDT',
        'XTZ': 'XTZUSDT',
        'NEO': 'NEOUSDT',
        'KSM': 'KSMUSDT',
        'WAVES': 'WAVESUSDT',
        'ZEC': 'ZECUSDT',
        'DASH': 'DASHUSDT',
        'BAT': 'BATUSDT',
        'COMP': 'COMPUSDT',
        'SNX': 'SNXUSDT',
        'YFI': 'YFIUSDT',
        'SUSHI': 'SUSHIUSDT',
        'CRV': 'CRVUSDT',
        '1INCH': '1INCHUSDT',
        'ANKR': 'ANKRUSDT',
        'ZIL': 'ZILUSDT',
        'QTUM': 'QTUMUSDT',
        'IOTA': 'IOTAUSDT',
        'RVN': 'RVNUSDT',
        'ICX': 'ICXUSDT',
        'ONT': 'ONTUSDT',
        'NANO': 'NANOUSDT',
        'SC': 'SCUSDT',
        'DGB': 'DGBUSDT',
        'STORJ': 'STORJUSDT',
        'OMG': 'OMGUSDT',
        'ZRX': 'ZRXUSDT',
        'REP': 'REPUSDT',
        'KNC': 'KNCUSDT',
        'BAND': 'BANDUSDT',
        'OCEAN': 'OCEANUSDT',
        'ALPHA': 'ALPHAUSDT',
        'AUDIO': 'AUDIOUSDT',
        'RLC': 'RLCUSDT',
        'RSR': 'RSRUSDT',
        'CTSI': 'CTSIUSDT',
        'API3': 'API3USDT',
        'DENT': 'DENTUSDT',
        'COTI': 'COTIUSDT',
        'CFX': 'CFXUSDT',
        'ROSE': 'ROSEUSDT',
        'SKL': 'SKLUSDT',
        'IOTX': 'IOTXUSDT',
        'ANKR': 'ANKRUSDT',
        'ZEN': 'ZENUSDT',
        'DYDX': 'DYDXUSDT',
        'RNDR': 'RNDRUSDT',
        'MINA': 'MINAUSDT',
        'ENS': 'ENSUSDT',
        'GAL': 'GALUSDT',
        'BLUR': 'BLURUSDT',
        'SUI': 'SUIUSDT',
        'SEI': 'SEIUSDT',
        'PYTH': 'PYTHUSDT',
        'JUP': 'JUPUSDT',
        'WIF': 'WIFUSDT',
        'BONK': 'BONKUSDT',
        'PEPE': 'PEPEUSDT',
        'SHIB': 'SHIBUSDT',
        'FLOKI': 'FLOKIUSDT',
        'BABYDOGE': 'BABYDOGEUSDT',
        'SAFEMOON': 'SAFEMOONUSDT',
        'MOON': 'MOONUSDT',
        'ELON': 'ELONUSDT',
        'SAMO': 'SAMOUSDT',
        'COPE': 'COPEUSDT',
        'RAY': 'RAYUSDT',
        'SRM': 'SRMUSDT',
        'ORCA': 'ORCAUSDT',
        'MNGO': 'MNGOUSDT',
        'STEP': 'STEPUSDT',
        'SLND': 'SLNDUSDT',
        'MER': 'MERUSDT',
        'GMT': 'GMTUSDT',
        'GST': 'GSTUSDT',
        'APE': 'APEUSDT',
        'DYDX': 'DYDXUSDT',
        'PERP': 'PERPUSDT',
        'RAD': 'RADUSDT',
        'BADGER': 'BADGERUSDT',
        'KP3R': 'KP3RUSDT',
        'HEGIC': 'HEGICUSDT',
        'PICKLE': 'PICKLEUSDT',
        'CREAM': 'CREAMUSDT',
        'ALPHA': 'ALPHAUSDT',
        'BETA': 'BETAUSDT',
        'GAMMA': 'GAMMAUSDT',
        'DELTA': 'DELTAUSDT',
        'THETA': 'THETAUSDT',
        'OMEGA': 'OMEGAUSDT',
        'SIGMA': 'SIGMAUSDT',
        'LAMBDA': 'LAMBDAUSDT',
        'PHI': 'PHIUSDT',
        'PSI': 'PSIUSDT',
        'CHI': 'CHIUSDT',
        'XI': 'XIUSDT',
        'OMICRON': 'OMICRONUSDT',
        'UPSILON': 'UPSILONUSDT',
        'PHI': 'PHIUSDT',
        'CHI': 'CHIUSDT',
        'PSI': 'PSIUSDT',
        'OMEGA': 'OMEGAUSDT',
        'SIGMA': 'SIGMAUSDT',
        'LAMBDA': 'LAMBDAUSDT',
        'XI': 'XIUSDT',
        'OMICRON': 'OMICRONUSDT',
        'UPSILON': 'UPSILONUSDT',
        # 可补充
    }
    symbol = symbol_map.get(token_code.upper())
    if not symbol:
        symbol = token_code.upper() + 'USDT'
    closes = get_binance_4h_klines(symbol)
    if not closes or len(closes) < 35:
        return "MACD数据获取失败"
    diff, dea, macd = calc_macd(closes)
    if diff is None or dea is None or macd is None:
        return "MACD数据不足"
    # 多空判断
    if diff > dea and macd > 0:
        signal = "多头（看涨）"
    elif diff < dea and macd < 0:
        signal = "空头（看跌）"
    else:
        signal = "震荡/信号不明"
    return f"4小时MACD: DIFF={diff:.2f}, DEA={dea:.2f}, MACD={macd:.2f}，信号：{signal}"

# 市场分析师：集成实时行情+K线数据
def market_report(token_code):
    market_data = get_token_market_data(token_code)
    ohlc = get_token_ohlc(token_code, days=30)
    macd_str = get_macd_signal(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    if 'error' in ohlc:
        ohlc_str = f"K线数据获取失败：{ohlc['error']}"
    else:
        ohlc_str = f"近30天最高价：{ohlc['max_high']} USD，最低价：{ohlc['min_low']} USD"
    prompt = (
        f"{market_report_prompt}\n"
        f"分析对象：{token_code}\n"
        f"最新价格：{market_data['price_formatted']} USD\n"
        f"市值：{market_data['market_cap']:,.0f} USD\n"
        f"24小时成交量：{market_data['volume']:,.0f} USD\n"
        f"数据更新时间：{market_data['last_updated']}\n"
        f"{ohlc_str}\n"
        f"{macd_str}\n"
    )
    return call_deepseek(prompt)

# 社交分析师：集成免费社交热度
def sentiment_report(token_code):
    prompt = (
        f"{sentiment_report_prompt}\n"
        f"分析对象：{token_code}\n"
    )
    return call_deepseek(prompt)

# 新闻分析师：集成免费新闻和链上大额交易数据
def get_arkham_whale_transactions(token_code):
    """
    使用非官方Arkham API获取大额交易数据。
    注意：这是一个非官方的、未经授权的API，可能随时失效。
    """
    # 这是基于社区逆向工程的非官方API端点，可能随时变更
    # 我们将尝试获取特定代币的转账数据
    url = f"{ARKHAM_API_URL}/transfers?base={token_code.upper()}&limit=10&offset=0"
    headers = {
        # 非官方API可能不需要API密钥，但可能需要特定的User-Agent或其他头信息
        # 这里我们使用一个通用的User-Agent
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data or 'transfers' not in data or not data['transfers']:
            return "使用Arkham API未找到相关大额交易数据。"

        report_lines = ["近期大额交易摘要 (来自 Arkham Intelligence):"]
        for tx in data['transfers'][:5]: # 最多显示5条
            from_addr = tx.get('fromAddress', {}).get('address', 'N/A')
            to_addr = tx.get('toAddress', {}).get('address', 'N/A')
            value_usd = tx.get('valueUSD', 0)
            token_symbol = tx.get('token', {}).get('symbol', token_code.upper())
            
            line = f"- 价值约 ${value_usd:,.2f} USD 的 {token_symbol} 从 {from_addr} 转移到 {to_addr}。"
            report_lines.append(line)
        
        return "\n".join(report_lines)

    except Exception as e:
        return f"获取Arkham大额交易数据失败：{e}。这可能是一个非官方或已失效的API。"

def news_report(token_code):
    news = get_token_news(token_code)
    whale_data = get_arkham_whale_transactions(token_code)

    prompt = (
        f"{news_report_prompt}\n"
        f"分析对象：{token_code}\n"
        f"最新相关新闻：{news}\n"
        f"链上大额交易数据：\n{whale_data}\n"
    )
    return call_deepseek(prompt)

# 其余角色保持不变，均为一句话结论
def get_fear_and_greed_index():
    try:
        response = requests.get(f"{ALTERNATIVE_ME_API_URL}/fng/?limit=1")
        response.raise_for_status()
        data = response.json()
        return data['data'][0]['value']
    except Exception as e:
        print(f"获取贪婪恐惧指数失败: {e}")
        return "N/A"

def get_rsi(symbol, interval='1d'):
    """使用 TAAPI.IO 获取RSI指标。"""
    if not TAAPI_SECRET:
        return "TAAPI.IO API secret not configured."
    try:
        client = TaapiClient(TAAPI_SECRET)
        results = client.get_indicator(indicator='rsi', exchange='binance', symbol=f'{symbol.upper()}/USDT', interval=interval)
        if isinstance(results, dict):
            return results.get('value')
        else:
            return f"获取RSI失败: 返回结果异常: {results}"
    except Exception as e:
        return f"获取RSI失败: {e}"

def get_funding_rates(symbol):
    """使用 fundingrate 包获取资金费率。"""
    try:
        # TODO: 替换为 fundingrate 包的正确用法
        # rate = fr.get_funding_rate(symbol.upper())
        return "资金费率功能未实现，请补充 fundingrate 包的正确用法"
    except Exception as e:
        return f"获取资金费率失败: {e}"

def fundamentals_report(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    if 'price_formatted' not in market_data:
        market_data['price_formatted'] = f"{market_data['price']:,.2f}" if 'price' in market_data else "N/A"

    fear_and_greed_index = get_fear_and_greed_index()
    rsi = get_rsi(token_code)
    funding_rate = get_funding_rates(token_code)

    prompt = (
        f"{fundamentals_report_prompt}\n"
        f"分析对象：{token_code}\n"
        f"当前价格：{market_data['price_formatted']} USD\n"
        f"贪婪恐惧指数：{fear_and_greed_index}\n"
        f"RSI (1d): {rsi}\n"
        f"资金费率: {funding_rate}"
    )
    return call_deepseek(prompt)

def bull_history(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    if 'price_formatted' not in market_data:
        market_data['price_formatted'] = f"{market_data['price']:,.2f}" if 'price' in market_data else "N/A"
    prompt = f"{bull_history_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def bear_history(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    prompt = f"{bear_history_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def research_manager_report(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    prompt = f"{research_manager_report_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def trader_investment_plan(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    prompt = f"{trader_investment_plan_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def risky_history(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    prompt = f"{risky_history_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def safe_history(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    prompt = f"{safe_history_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def neutral_history(token_code):
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    prompt = f"{neutral_history_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD"
    return call_deepseek(prompt)

def judge_decision(analysis_results, token_code):
    # 获取实时价格数据
    market_data = get_token_market_data(token_code)
    if 'error' in market_data:
        return f"获取行情数据失败：{market_data['error']}"
    
    summary = "\n".join([f"{role}: {result}" for role, result in analysis_results.items()])
    prompt = f"{judge_decision_prompt}\n分析对象：{token_code}\n当前价格：{market_data['price_formatted']} USD\n以下是各分析师的报告：\n{summary}"
    return call_deepseek(prompt)