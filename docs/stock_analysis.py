import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from matplotlib.patches import Rectangle

plt.rcParams['font.sans-serif'] = ['SimHei', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False

def read_stock_data(file_path):
    df = pd.read_csv(file_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df = df.sort_values('trade_date')
    return df

def plot_close_price(df, output_path):
    plt.figure(figsize=(12, 6))
    plt.plot(df['trade_date'], df['close'], color='#1f77b4', linewidth=2, label='收盘价')
    
    ma5 = df['close'].rolling(window=5).mean()
    ma20 = df['close'].rolling(window=20).mean()
    ma60 = df['close'].rolling(window=60).mean()
    
    plt.plot(df['trade_date'], ma5, color='#ff7f0e', linewidth=1.5, label='5日均线')
    plt.plot(df['trade_date'], ma20, color='#2ca02c', linewidth=1.5, label='20日均线')
    plt.plot(df['trade_date'], ma60, color='#d62728', linewidth=1.5, label='60日均线')
    
    plt.title('风华高科(000636)每日收盘价走势图', fontsize=14, fontweight='bold')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('收盘价(元)', fontsize=12)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f'收盘价走势图已保存: {output_path}')

def plot_kline(df, output_path):
    """
    绘制K线图（蜡烛图）
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), 
                                    gridspec_kw={'height_ratios': [3, 1]},
                                    sharex=True)
    
    dates = df['trade_date'].values
    opens = df['open'].values
    closes = df['close'].values
    highs = df['high'].values
    lows = df['low'].values
    
    width = 0.6
    
    for i in range(len(df)):
        date = dates[i]
        open_price = opens[i]
        close_price = closes[i]
        high_price = highs[i]
        low_price = lows[i]
        
        if close_price >= open_price:
            color = '#ff4136'
            body_bottom = open_price
            body_height = close_price - open_price
        else:
            color = '#2dcc70'
            body_bottom = close_price
            body_height = open_price - close_price
        
        ax1.add_patch(Rectangle((mdates.date2num(date) - width/2, body_bottom), 
                                 width, body_height, 
                                 facecolor=color, edgecolor=color, linewidth=0.5))
        
        ax1.plot([mdates.date2num(date), mdates.date2num(date)],
                 [low_price, body_bottom], color=color, linewidth=1)
        ax1.plot([mdates.date2num(date), mdates.date2num(date)],
                 [body_bottom + body_height, high_price], color=color, linewidth=1)
    
    ma5 = df['close'].rolling(window=5).mean()
    ma10 = df['close'].rolling(window=10).mean()
    ma20 = df['close'].rolling(window=20).mean()
    
    ax1.plot(df['trade_date'], ma5, color='#ff7f0e', linewidth=1.2, label='MA5', alpha=0.8)
    ax1.plot(df['trade_date'], ma10, color='#1f77b4', linewidth=1.2, label='MA10', alpha=0.8)
    ax1.plot(df['trade_date'], ma20, color='#9467bd', linewidth=1.2, label='MA20', alpha=0.8)
    
    ax1.set_title('风华高科(000636) K线图', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格(元)', fontsize=12)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    
    vol = df['vol'].values / 10000
    vol_colors = ['#ff4136' if closes[i] >= opens[i] else '#2dcc70' for i in range(len(df))]
    
    ax2.bar(df['trade_date'], vol, width=0.6, color=vol_colors, alpha=0.7)
    
    vol_ma5 = df['vol'].rolling(window=5).mean() / 10000
    ax2.plot(df['trade_date'], vol_ma5, color='#ff7f0e', linewidth=1.2, label='成交量MA5', alpha=0.8)
    
    ax2.set_ylabel('成交量(万手)', fontsize=12)
    ax2.set_xlabel('日期', fontsize=12)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f'K线图已保存: {output_path}')

def calculate_technical_indicators(df):
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    df['vol_ma5'] = df['vol'].rolling(window=5).mean()
    df['vol_ma20'] = df['vol'].rolling(window=20).mean()
    
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    df['macd'] = df['ma20'] - df['ma60']
    df['signal'] = df['macd'].rolling(window=9).mean()
    
    return df

def generate_analysis_report(df, output_path):
    analysis = []
    analysis.append('# 风华高科(000636)股票分析报告')
    analysis.append('')
    analysis.append('## 一、基本信息')
    analysis.append('')
    analysis.append(f'- **股票代码**: 000636.SZ')
    analysis.append(f'- **股票名称**: 风华高科')
    analysis.append(f'- **分析周期**: {df["trade_date"].min().strftime("%Y-%m-%d")} 至 {df["trade_date"].max().strftime("%Y-%m-%d")}')
    analysis.append(f'- **交易天数**: {len(df)} 天')
    analysis.append('')
    
    analysis.append('## 二、行情概览')
    analysis.append('')
    
    first_close = df['close'].iloc[0]
    last_close = df['close'].iloc[-1]
    max_close = df['close'].max()
    min_close = df['close'].min()
    avg_close = df['close'].mean()
    std_close = df['close'].std()
    
    total_change = last_close - first_close
    total_pct_change = (total_change / first_close) * 100
    
    analysis.append(f'| 指标 | 数值 |')
    analysis.append(f'|------|------|')
    analysis.append(f'| 期初收盘价 | {first_close:.2f} 元 |')
    analysis.append(f'| 期末收盘价 | {last_close:.2f} 元 |')
    analysis.append(f'| 期间最高价 | {max_close:.2f} 元 |')
    analysis.append(f'| 期间最低价 | {min_close:.2f} 元 |')
    analysis.append(f'| 平均收盘价 | {avg_close:.2f} 元 |')
    analysis.append(f'| 价格标准差 | {std_close:.2f} |')
    analysis.append(f'| 累计涨跌额 | {total_change:.2f} 元 |')
    analysis.append(f'| 累计涨跌幅 | {total_pct_change:.2f}% |')
    analysis.append('')
    
    analysis.append('## 三、技术面分析')
    analysis.append('')
    
    analysis.append('### 3.1 均线分析')
    analysis.append('')
    
    latest_ma5 = df['ma5'].iloc[-1]
    latest_ma20 = df['ma20'].iloc[-1]
    latest_ma60 = df['ma60'].iloc[-1]
    
    analysis.append(f'- **5日均线**: {latest_ma5:.2f} 元')
    analysis.append(f'- **20日均线**: {latest_ma20:.2f} 元')
    analysis.append(f'- **60日均线**: {latest_ma60:.2f} 元')
    analysis.append('')
    
    if last_close > latest_ma5 > latest_ma20 > latest_ma60:
        analysis.append('**均线状态**: 多头排列，短期趋势向上')
    elif last_close < latest_ma5 < latest_ma20 < latest_ma60:
        analysis.append('**均线状态**: 空头排列，短期趋势向下')
    else:
        analysis.append('**均线状态**: 均线交织，趋势不明朗')
    analysis.append('')
    
    analysis.append('### 3.2 RSI分析')
    analysis.append('')
    
    latest_rsi = df['rsi'].iloc[-1]
    
    analysis.append(f'- **RSI(14)**: {latest_rsi:.2f}')
    analysis.append('')
    
    if latest_rsi > 70:
        analysis.append('**RSI状态**: 超买区域，可能存在回调风险')
    elif latest_rsi < 30:
        analysis.append('**RSI状态**: 超卖区域，可能存在反弹机会')
    else:
        analysis.append('**RSI状态**: 正常区域，多空力量均衡')
    analysis.append('')
    
    analysis.append('### 3.3 MACD分析')
    analysis.append('')
    
    latest_macd = df['macd'].iloc[-1]
    latest_signal = df['signal'].iloc[-1]
    
    analysis.append(f'- **MACD**: {latest_macd:.2f}')
    analysis.append(f'- **信号线**: {latest_signal:.2f}')
    analysis.append(f'- **MACD柱状图**: {latest_macd - latest_signal:.2f}')
    analysis.append('')
    
    if latest_macd > latest_signal and df['macd'].iloc[-2] <= df['signal'].iloc[-2]:
        analysis.append('**MACD状态**: 金叉信号，可能是买入机会')
    elif latest_macd < latest_signal and df['macd'].iloc[-2] >= df['signal'].iloc[-2]:
        analysis.append('**MACD状态**: 死叉信号，可能是卖出机会')
    elif latest_macd > 0:
        analysis.append('**MACD状态**: 多头市场，MACD在零轴上方')
    else:
        analysis.append('**MACD状态**: 空头市场，MACD在零轴下方')
    analysis.append('')
    
    analysis.append('### 3.4 成交量分析')
    analysis.append('')
    
    avg_vol = df['vol'].mean()
    latest_vol = df['vol'].iloc[-1]
    vol_ratio = latest_vol / avg_vol
    
    analysis.append(f'- **期间平均成交量**: {avg_vol/10000:.2f} 万手')
    analysis.append(f'- **最新成交量**: {latest_vol/10000:.2f} 万手')
    analysis.append(f'- **量比**: {vol_ratio:.2f}')
    analysis.append('')
    
    if vol_ratio > 1.5:
        analysis.append('**成交量状态**: 放量，市场关注度较高')
    elif vol_ratio < 0.5:
        analysis.append('**成交量状态**: 缩量，市场交投清淡')
    else:
        analysis.append('**成交量状态**: 正常水平')
    analysis.append('')
    
    analysis.append('## 四、基本面分析')
    analysis.append('')
    
    analysis.append('### 4.1 公司概况')
    analysis.append('')
    analysis.append('风华高科（000636）是一家专业从事新型元器件、电子材料、电子专用设备等电子信息基础产品的高新技术企业。')
    analysis.append('')
    analysis.append('**主要业务**:')
    analysis.append('- 电子元器件：电容器、电阻器、电感器等')
    analysis.append('- 电子材料：陶瓷粉体、电子浆料等')
    analysis.append('- 电子专用设备')
    analysis.append('')
    
    analysis.append('### 4.2 行业分析')
    analysis.append('')
    analysis.append('公司所属的电子元器件行业是电子信息产业的基础支撑，受益于：')
    analysis.append('- 新能源汽车、光伏、储能等新能源产业的快速发展')
    analysis.append('- 消费电子、通信设备的持续升级')
    analysis.append('- 国产替代趋势下的进口替代机遇')
    analysis.append('')
    
    analysis.append('### 4.3 市场表现总结')
    analysis.append('')
    analysis.append(f'过去一年，风华高科股价从 {first_close:.2f} 元波动至 {last_close:.2f} 元，累计涨幅 {total_pct_change:.2f}%。')
    analysis.append('')
    if total_pct_change > 0:
        analysis.append('**整体评价**: 股价表现较好，呈上涨趋势。')
    else:
        analysis.append('**整体评价**: 股价表现较弱，呈下跌趋势。')
    analysis.append('')
    
    analysis.append('## 五、风险提示')
    analysis.append('')
    analysis.append('- 电子元器件行业周期性波动风险')
    analysis.append('- 原材料价格波动风险')
    analysis.append('- 国际贸易环境变化风险')
    analysis.append('- 技术创新不及预期风险')
    analysis.append('')
    
    analysis.append('---')
    analysis.append(f'*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(analysis))
    
    print(f'分析报告已保存: {output_path}')

def main():
    csv_path = 'stock_data_fhgk.csv'
    image_path = 'fhgk_close_price.png'
    kline_path = 'fhgk_kline.png'
    report_path = 'fhgk_analysis_report.md'
    
    print('正在读取股票数据...')
    df = read_stock_data(csv_path)
    
    print(f'数据读取完成，共 {len(df)} 条记录')
    print(f'日期范围: {df["trade_date"].min().strftime("%Y-%m-%d")} 至 {df["trade_date"].max().strftime("%Y-%m-%d")}')
    
    print('')
    print('正在计算技术指标...')
    df = calculate_technical_indicators(df)
    
    print('')
    print('正在绘制收盘价走势图...')
    plot_close_price(df, image_path)
    
    print('')
    print('正在绘制K线图...')
    plot_kline(df, kline_path)
    
    print('')
    print('正在生成分析报告...')
    generate_analysis_report(df, report_path)
    
    print('')
    print('='*50)
    print('分析完成！')
    print(f'数据文件: {csv_path}')
    print(f'收盘价走势图: {image_path}')
    print(f'K线图: {kline_path}')
    print(f'分析报告: {report_path}')
    print('='*50)

if __name__ == '__main__':
    main()
