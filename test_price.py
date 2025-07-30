# test_price.py
# 测试价格获取功能

from analysts import get_token_market_data

def test_price_accuracy():
    """测试价格获取的准确性"""
    test_tokens = ['BTC', 'ETH', 'SOL']
    
    print("=" * 50)
    print("测试实时价格获取功能")
    print("=" * 50)
    
    for token in test_tokens:
        print(f"\n测试 {token} 价格获取:")
        try:
            data = get_token_market_data(token)
            if 'error' in data:
                print(f"❌ {token} 价格获取失败: {data['error']}")
            else:
                print(f"✅ {token} 当前价格: {data['price_formatted']} USD")
                print(f"   市值: {data['market_cap']:,.0f} USD")
                print(f"   24h成交量: {data['volume']:,.0f} USD")
                print(f"   更新时间: {data['last_updated']}")
        except Exception as e:
            print(f"❌ {token} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print("价格获取测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_price_accuracy() 