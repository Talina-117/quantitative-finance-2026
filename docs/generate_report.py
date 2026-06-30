#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风华高科(000636.SZ) 全面分析报告 HTML 生成器
使用字符串拼接而非f-string来避免JS花括号冲突
"""

import json
import csv
import os
from datetime import datetime


def load_csv_data(csv_path):
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    rows.sort(key=lambda x: x['trade_date'])
    return rows


def process_kline_data(rows):
    dates = []
    ohlc = []
    volumes = []
    pct_changes = []
    closes = []

    for row in rows:
        d = row['trade_date']
        date_str = "{}-{}-{}".format(d[:4], d[4:6], d[6:8])
        dates.append(date_str)
        o = float(row['open'])
        c = float(row['close'])
        l = float(row['low'])
        h = float(row['high'])
        ohlc.append([o, c, l, h])
        volumes.append(float(row['vol']))
        pct_changes.append(float(row['pct_chg']))
        closes.append(c)

    ma5 = []
    ma10 = []
    ma20 = []
    ma60 = []

    for i in range(len(closes)):
        if i >= 4:
            ma5.append(round(sum(closes[i-4:i+1]) / 5, 2))
        else:
            ma5.append(None)
        if i >= 9:
            ma10.append(round(sum(closes[i-9:i+1]) / 10, 2))
        else:
            ma10.append(None)
        if i >= 19:
            ma20.append(round(sum(closes[i-19:i+1]) / 20, 2))
        else:
            ma20.append(None)
        if i >= 59:
            ma60.append(round(sum(closes[i-59:i+1]) / 60, 2))
        else:
            ma60.append(None)

    vol_colors = []
    for item in ohlc:
        if item[1] >= item[0]:
            vol_colors.append('#e74c3c')
        else:
            vol_colors.append('#27ae60')

    return {
        'dates': dates, 'ohlc': ohlc, 'volumes': volumes,
        'pct_changes': pct_changes, 'closes': closes,
        'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'ma60': ma60,
        'vol_colors': vol_colors,
    }


def calc_rsi(closes, period=14):
    rsi_values = [None] * period
    for i in range(period, len(closes)):
        gains = 0
        losses = 0
        for j in range(i - period, i):
            delta = closes[j+1] - closes[j]
            if delta > 0:
                gains += delta
            else:
                losses += abs(delta)
        avg_gain = gains / period
        avg_loss = losses / period
        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rsi_values.append(round(100 - (100 / (1 + avg_gain / avg_loss)), 2))
    return rsi_values


def calc_macd(closes, short=12, long_period=26, signal=9):
    ema_short = [closes[0]]
    ema_long = [closes[0]]
    k_short = 2.0 / (short + 1)
    k_long = 2.0 / (long_period + 1)
    k_signal = 2.0 / (signal + 1)

    for i in range(1, len(closes)):
        ema_short.append(ema_short[-1] * (1 - k_short) + closes[i] * k_short)
        ema_long.append(ema_long[-1] * (1 - k_long) + closes[i] * k_long)

    dif = [s - l for s, l in zip(ema_short, ema_long)]
    dea = [dif[0]]
    for i in range(1, len(dif)):
        dea.append(dea[-1] * (1 - k_signal) + dif[i] * k_signal)
    macd_bar = [2 * (d - e) for d, e in zip(dif, dea)]

    # 前 long_period-1 个数据不完整，置None
    for i in range(long_period - 1):
        dif[i] = None
        dea[i] = None
        macd_bar[i] = None

    return dif, dea, macd_bar


def generate_html(csv_path, output_path):
    rows = load_csv_data(csv_path)
    kline = process_kline_data(rows)
    rsi_values = calc_rsi(kline['closes'], 14)
    macd_dif, macd_dea, macd_bar = calc_macd(kline['closes'])

    # 将所有数据序列化为JSON字符串，用于JS嵌入
    D = json.dumps(kline['dates'])
    O = json.dumps(kline['ohlc'])
    V = json.dumps(kline['volumes'])
    MA5 = json.dumps(kline['ma5'])
    MA10 = json.dumps(kline['ma10'])
    MA20 = json.dumps(kline['ma20'])
    MA60 = json.dumps(kline['ma60'])
    VC = json.dumps(kline['vol_colors'])
    RSI = json.dumps(rsi_values)
    MDIF = json.dumps(macd_dif)
    MDEA = json.dumps(macd_dea)
    MBAR = json.dumps(macd_bar)

    # 财务数据
    rev_data = json.dumps([round(41.08, 2), round(57.56, 2), round(15.15, 2)])
    np_data = json.dumps([round(2.28, 2), round(2.83, 2), round(0.89, 2)])
    rev_labels = json.dumps(['2025Q3', '2025全年', '2026Q1'])

    # 分红数据
    div_years = json.dumps(['2024', '2023', '2022', '2022H1', '2021'])
    div_amounts = json.dumps([1.50, 0.50, 1.00, 1.144, 1.16])

    # 资金流向数据
    fund_labels = json.dumps(['主力净流入', '超大单净流入', '中单净流入', '小单净流入'])
    fund_values = json.dumps([30531.17, -12752.83, -28492.74, -2038.43])

    # 股东户数
    sh_labels = json.dumps(['2025-08', '2025-09', '2025-12', '2026-03', '2026-04', '2026-05'])
    sh_values = json.dumps([9.04, 9.25, 10.08, 15.32, 13.64, 21.72])

    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>风华高科(000636.SZ) 全面分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  :root {
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --text: #2c3e50;
    --text-secondary: #7f8c8d;
    --accent: #3498db;
    --red: #e74c3c;
    --green: #27ae60;
    --border: #e0e0e0;
    --shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.6; }
  .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
  .header { background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: #fff; padding: 30px; border-radius: 12px; margin-bottom: 24px; }
  .header h1 { font-size: 28px; margin-bottom: 8px; }
  .header .subtitle { font-size: 14px; color: rgba(255,255,255,0.8); }
  .metrics-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }
  .metric-card { background: var(--card-bg); border-radius: 8px; padding: 16px; box-shadow: var(--shadow); text-align: center; }
  .metric-card .label { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
  .metric-card .value { font-size: 22px; font-weight: 700; }
  .metric-card .value.red { color: var(--red); }
  .metric-card .value.green { color: var(--green); }
  .metric-card .sub { font-size: 11px; color: var(--text-secondary); }
  .section { background: var(--card-bg); border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: var(--shadow); }
  .section h2 { font-size: 20px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid var(--accent); }
  .section h3 { font-size: 16px; margin: 16px 0 8px; color: var(--accent); }
  .data-table { width: 100%; border-collapse: collapse; margin: 12px 0; }
  .data-table th { background: #f0f3f5; padding: 10px 12px; text-align: left; font-size: 13px; }
  .data-table td { padding: 8px 12px; font-size: 13px; border-bottom: 1px solid var(--border); }
  .data-table .red { color: var(--red); }
  .data-table .green { color: var(--green); }
  .chart-box { width: 100%; height: 400px; margin: 12px 0; }
  .chart-box-sm { width: 100%; height: 280px; margin: 12px 0; }
  .tag { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; margin: 2px; }
  .tag-red { background: #fdecea; color: var(--red); }
  .tag-green { background: #e8f8f0; color: var(--green); }
  .tag-blue { background: #e8f4fd; color: var(--accent); }
  .tag-orange { background: #fef5e7; color: #e67e22; }
  .tag-purple { background: #f4ecf7; color: #8e44ad; }
  .conclusion { background: linear-gradient(135deg, #2c3e50, #34495e); color: #fff; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
  .conclusion h2 { border-bottom-color: rgba(255,255,255,0.3); }
  .conclusion .highlight { background: rgba(231,76,60,0.2); padding: 12px; border-radius: 8px; margin: 12px 0; }
  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .info-item { display: flex; align-items: baseline; }
  .info-item .key { font-size: 13px; color: var(--text-secondary); min-width: 100px; }
  .info-item .val { font-size: 14px; font-weight: 500; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .footer { text-align: center; color: var(--text-secondary); font-size: 12px; padding: 20px; }
  @media (max-width: 768px) {
    .metrics-grid { grid-template-columns: repeat(3, 1fr); }
    .two-col { grid-template-columns: 1fr; }
    .info-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>风华高科(000636.SZ) 全面分析报告</h1>
  <div class="subtitle">地方国企 | 电子元器件 | 广东省肇庆市 | 数据截至 2026-06-30</div>
</div>

<div class="metrics-grid">
  <div class="metric-card">
    <div class="label">最新收盘价</div>
    <div class="value">72.24</div>
    <div class="sub">6/30 一字跌停 -10%</div>
  </div>
  <div class="metric-card">
    <div class="label">PE(TTM)</div>
    <div class="value red">272x</div>
    <div class="sub">远期PE 236x | 极高估值</div>
  </div>
  <div class="metric-card">
    <div class="label">PB</div>
    <div class="value red">6.7x</div>
    <div class="sub">市值 835.8亿</div>
  </div>
  <div class="metric-card">
    <div class="label">年涨幅(YTD)</div>
    <div class="value red">+344%</div>
    <div class="sub">52周高84 低13.42</div>
  </div>
  <div class="metric-card">
    <div class="label">股息率(TTM)</div>
    <div class="value">0.21%</div>
    <div class="sub">几乎无分红回报</div>
  </div>
</div>

<div class="conclusion">
  <h2>核心判断</h2>
  <div class="highlight">
    <strong>高风险警示：</strong>风华高科过去一年涨幅超340%，当前PE(TTM) 272x、PB 6.7x，估值已远超基本面支撑范围。6月30日出现一字跌停（-10%），MACD/KDJ出现空头信号，主力超大单净流出，股东户数从9万暴增至21.7万——典型的<span class="tag tag-red">筹码分散</span> + <span class="tag tag-red">估值泡沫</span>格局。<br><br>
    <strong>操作建议：</strong>已持仓者应考虑逐步减仓或设止损线；未持仓者不建议追高入场。如后续跌至40-50元区间（PE回到60-80x、PB回到3-4x）且基本面持续改善，方可重新评估。
  </div>
</div>

<div class="section">
  <h2>一、公司概况</h2>
  <div class="info-grid">
    <div>
      <div class="info-item"><span class="key">公司名称</span><span class="val">风华高科</span></div>
      <div class="info-item"><span class="key">股票代码</span><span class="val">000636.SZ</span></div>
      <div class="info-item"><span class="key">上市日期</span><span class="val">1996-11-29</span></div>
      <div class="info-item"><span class="key">企业性质</span><span class="val">地方国企（广东广晟控股23.59%）</span></div>
      <div class="info-item"><span class="key">董事长</span><span class="val">李程</span></div>
      <div class="info-item"><span class="key">所属行业</span><span class="val">电子 - 电子元器件</span></div>
    </div>
    <div>
      <div class="info-item"><span class="key">主营业务</span><span class="val">研制、生产、销售电子元器件、电子材料</span></div>
      <div class="info-item"><span class="key">注册地址</span><span class="val">广东省肇庆市风华路18号</span></div>
      <div class="info-item"><span class="key">总股本</span><span class="val">11.57亿股</span></div>
      <div class="info-item"><span class="key">流通市值</span><span class="val">835.8亿元</span></div>
      <div class="info-item"><span class="key">网站</span><span class="val">www.fhcomp.com</span></div>
    </div>
  </div>
  <h3>业务结构</h3>
  <p>风华高科是国内领先的被动元器件制造商，核心产品包括<strong>MLCC（多层陶瓷电容器）</strong>、<strong>片式电阻器</strong>、<strong>电感器</strong>等，同时布局上游陶瓷粉体、电子浆料等关键材料。公司背靠广东省广晟控股集团（持股23.59%），属于广东省属国企体系。</p>
  <p><span class="tag tag-blue">国产替代</span> <span class="tag tag-blue">新能源车配套</span> <span class="tag tag-blue">消费电子复苏</span> <span class="tag tag-purple">被动元器件龙头</span></p>
</div>

<div class="section">
  <h2>二、价格走势与K线分析</h2>
  <div id="kline_chart" class="chart-box" style="height:480px;"></div>
  <h3>走势特征分析</h3>
  <table class="data-table">
    <tr><th>阶段</th><th>时间</th><th>价格区间</th><th>特征</th></tr>
    <tr><td>底部横盘</td><td>2025.08-12</td><td>13-17元</td><td>日均成交量极低，交投清淡，窄幅震荡</td></tr>
    <tr><td>第一波拉升</td><td>2026.01-02</td><td>17-26元</td><td>放量突破，连续涨停启动</td></tr>
    <tr><td>高位震荡</td><td>2026.03</td><td>20-27元</td><td>冲高回落，3月3日一字跌停后剧烈震荡</td></tr>
    <tr><td>第二波主升浪</td><td>2026.04-06中旬</td><td>22-84元</td><td class="red">极速拉升，连续涨停，6月29日冲高84元</td></tr>
    <tr><td>跌停调整</td><td>2026.06.30</td><td class="red">80.27-72.24(-10%)</td><td class="red">一字跌停封死，量仅4.47万手</td></tr>
  </table>
  <p style="color:var(--red);font-weight:600;">6月30日的一字跌停是重大警示信号：开盘即跌停价72.24元，全天无法打开，买卖极度失衡。结合此前连续涨停的极端走势，表明主力资金可能已在高位完成出货。</p>
</div>

<div class="section">
  <h2>三、技术面分析</h2>
  <h3>3.1 均线系统</h3>
  <table class="data-table">
    <tr><th>均线</th><th>数值(元)</th><th>与现价关系</th><th>信号</th></tr>
    <tr><td>MA5</td><td>76.60</td><td class="red">现价(72.24) &lt; MA5</td><td class="red">短期跌破5日线，偏空</td></tr>
    <tr><td>MA10</td><td>74.55</td><td class="red">现价 &lt; MA10</td><td class="red">跌破10日线，短期调整确立</td></tr>
    <tr><td>MA20</td><td>67.70</td><td class="green">现价 &gt; MA20</td><td>中期趋势仍在上方</td></tr>
    <tr><td>MA60</td><td>41.26</td><td class="green">现价 &gt;&gt; MA60</td><td>远离60日线，偏离极大</td></tr>
    <tr><td>MA120</td><td>30.99</td><td class="green">现价 &gt;&gt;&gt; MA120</td><td>偏离半年线超130%</td></tr>
    <tr><td>MA250</td><td>22.82</td><td class="green">现价 &gt;&gt;&gt;&gt; MA250</td><td>偏离年线超217%</td></tr>
  </table>
  <p><span class="tag tag-orange">5/10日线破位</span> <span class="tag tag-red">远离长期均线（均值回归风险极大）</span></p>

  <div class="two-col">
    <div>
      <h3>3.2 MACD</h3>
      <table class="data-table">
        <tr><th>指标</th><th>数值</th><th>信号</th></tr>
        <tr><td>DIF</td><td>9.05</td><td>DIF &lt; DEA</td></tr>
        <tr><td>DEA</td><td>9.38</td><td>-</td></tr>
        <tr><td>MACD柱</td><td class="red">-0.66</td><td class="red">空头，绿柱出现</td></tr>
      </table>
      <p><span class="tag tag-red">MACD柱转绿</span> DIF下穿DEA趋势形成，短期偏空。DIF仍在零轴上方，中期多头格局尚未完全破坏。</p>
    </div>
    <div>
      <h3>3.3 KDJ</h3>
      <table class="data-table">
        <tr><th>指标</th><th>数值</th><th>信号</th></tr>
        <tr><td>K</td><td>67.33</td><td>中位</td></tr>
        <tr><td>D</td><td>79.47</td><td>偏高</td></tr>
        <tr><td>J</td><td class="red">43.07</td><td class="red">J&lt;&lt;K/D，空头背离</td></tr>
      </table>
      <p><span class="tag tag-red">J值严重背离</span> J值(43)远低于K(67)和D(79)，典型空头背离形态，预示短期调整压力。</p>
    </div>
  </div>

  <h3>3.4 RSI 与布林带</h3>
  <div class="two-col">
    <div>
      <table class="data-table">
        <tr><th>RSI</th><th>数值</th><th>信号</th></tr>
        <tr><td>RSI2</td><td class="red">18.89</td><td class="red">极度超卖(跌停导致)</td></tr>
        <tr><td>RSI6</td><td>49.06</td><td>中性区域</td></tr>
        <tr><td>RSI12</td><td>59.93</td><td>偏强</td></tr>
        <tr><td>RSI24</td><td>65.75</td><td>偏强</td></tr>
      </table>
      <p>RSI2跌至18.89是跌停日的极端值，不代表真正的超卖买入信号——跌停板上的RSI超卖是<strong>流动性枯竭</strong>而非机会。</p>
    </div>
    <div>
      <table class="data-table">
        <tr><th>布林带</th><th>数值</th><th>信号</th></tr>
        <tr><td>上轨</td><td>82.74</td><td>-</td></tr>
        <tr><td>中轨</td><td>67.70</td><td>约MA20</td></tr>
        <tr><td>下轨</td><td>52.66</td><td>-</td></tr>
        <tr><td>现价位置</td><td>72.24</td><td>中轨与上轨之间</td></tr>
      </table>
      <p>布林带开口极大(上轨82.74 vs 下轨52.66，带宽30元)，波动率极高。现价从中轨上方回落，若跌破中轨67.70将进入中下轨区间。</p>
    </div>
  </div>

  <h3>3.5 技术指标综合图</h3>
  <div id="tech_chart" class="chart-box" style="height:320px;"></div>

  <h3>3.6 成交量与量价分析</h3>
  <p>量比 0.32（极度缩量）——跌停日成交仅4.47万手，远低于日均7.36万手。<strong>跌停缩量不是好事</strong>：意味着卖方封单极强，买方完全无力接盘，而非"惜售"。此前主升浪期间日均成交量130-260万手，如今跌停缩量至4.47万手，说明流动性骤降。</p>
  <p><span class="tag tag-red">跌停缩量</span> <span class="tag tag-red">流动性枯竭</span> <span class="tag tag-orange">换手率3.87%</span></p>
</div>

<div class="section">
  <h2>四、筹码与资金分析</h2>
  <div class="two-col">
    <div>
      <h3>4.1 筹码分布</h3>
      <table class="data-table">
        <tr><th>指标</th><th>数值</th><th>解读</th></tr>
        <tr><td>获利盘比例</td><td>51.8%</td><td>约半数持仓盈利</td></tr>
        <tr><td>平均成本</td><td>71.98元</td><td class="red">接近现价，大量筹码高位集中</td></tr>
        <tr><td>90%集中度</td><td>19.53</td><td>筹码分布较宽</td></tr>
        <tr><td>70%集中度</td><td>13.04</td><td>-</td></tr>
      </table>
      <p style="color:var(--red);font-weight:600;">平均成本71.98元约等于现价72.24元，大量筹码集中在70-80元高位区。一旦跌破70元，近半数持仓将转为亏损，可能引发恐慌抛售。</p>
    </div>
    <div>
      <h3>4.2 资金流向</h3>
      <div id="fund_chart" class="chart-box-sm"></div>
      <table class="data-table">
        <tr><th>类别</th><th>净流入(万元)</th><th>信号</th></tr>
        <tr><td>主力净流入</td><td class="green">+30,531</td><td>表面看主力仍在流入</td></tr>
        <tr><td>超大单净流入</td><td class="red">-12,753</td><td class="red">超大资金在撤出!</td></tr>
        <tr><td>中单净流入</td><td class="red">-28,493</td><td>-</td></tr>
        <tr><td>小单净流入</td><td class="red">-2,038</td><td>-</td></tr>
      </table>
      <p><span class="tag tag-red">超大单净流出</span> 主力净流入看似正向，但超大单(机构/大资金)实际净流出1.27亿——超大单才是真正的机构行为。</p>
    </div>
  </div>

  <h3>4.3 股东户数变化</h3>
  <div id="shareholder_chart" class="chart-box-sm"></div>
  <p>股东户数从2025年8月的<strong>9.04万户</strong>暴增至2026年5月的<strong>21.72万户</strong>，增幅140%。典型的<span class="tag tag-red">筹码从集中到分散</span>——大量散户在高位接盘，早期低位建仓的机构逐步退出。人均持股从12,798股降至5,327股，筹码极度分散。</p>
</div>

<div class="section">
  <h2>五、基本面分析</h2>
  <h3>5.1 财务数据概览</h3>
  <table class="data-table">
    <tr><th>指标</th><th>2025全年</th><th>2026Q1</th><th>TTM</th></tr>
    <tr><td>营业收入</td><td>57.56亿</td><td>15.15亿</td><td>59.97亿</td></tr>
    <tr><td>归母净利润</td><td>2.83亿</td><td>0.89亿</td><td>3.07亿</td></tr>
    <tr><td>基本EPS</td><td>0.25元</td><td>0.08元</td><td>0.27元</td></tr>
    <tr><td>毛利率(TTM)</td><td>17.8%</td><td>-</td><td class="red">17.6%</td></tr>
    <tr><td>净利率(TTM)</td><td>4.9%</td><td>-</td><td class="red">5.1%</td></tr>
    <tr><td>研发费用</td><td>2.84亿</td><td>0.69亿</td><td>-</td></tr>
  </table>
  <p style="color:var(--red);">核心矛盾：市值835.8亿 vs TTM净利润3.07亿，PE(TTM) = 272x。即使远期PE(236x)也意味着市场定价<strong>未来8-10年净利润需增长20倍以上</strong>才能合理化。对毛利率17%的被动元器件企业，预期过于乐观。</p>

  <h3>5.2 盈利质量</h3>
  <table class="data-table">
    <tr><th>指标</th><th>2025全年</th><th>2026Q1</th><th>问题</th></tr>
    <tr><td>经营活动现金流</td><td class="green">+4.26亿</td><td class="red">-2.18亿</td><td class="red">Q1经营CF转负!</td></tr>
    <tr><td>投资活动现金流</td><td class="red">-7.41亿</td><td>-0.50亿</td><td>持续大额资本开支</td></tr>
    <tr><td>筹资活动现金流</td><td class="red">-4.83亿</td><td>+0.02亿</td><td>-</td></tr>
    <tr><td>FCFE</td><td class="red">-2.25亿</td><td class="red">-3.91亿</td><td class="red">自由现金流持续为负</td></tr>
  </table>
  <p><span class="tag tag-red">经营现金流Q1转负</span> <span class="tag tag-red">FCFE持续为负</span> —— 净利润3亿但经营现金流Q1为负，可能与应收账款大幅增加(18亿)有关。盈利质量存疑。</p>

  <div class="two-col">
    <div>
      <h3>5.3 收入与利润趋势</h3>
      <div id="revenue_chart" class="chart-box-sm"></div>
    </div>
    <div>
      <h3>5.4 分红回报</h3>
      <div id="dividend_chart" class="chart-box-sm"></div>
      <p>近5年累计分红约4.32亿，2024年10派1.5元，对应股息率仅0.21%——远低于银行存款利率，投资回报完全依赖股价上涨。</p>
    </div>
  </div>

  <h3>5.5 行业与催化</h3>
  <p><strong>看多逻辑（市场定价的叙事）：</strong></p>
  <ul>
    <li>MLCC国产替代：日韩巨头占全球70%+份额，风华高科作为国内龙头受益于国产替代加速</li>
    <li>新能源车/AI服务器需求：单车MLCC用量从3000颗增至1万+颗</li>
    <li>产能扩张：近年持续投资扩产(投资CF -7.4亿)，产能爬坡后营收有望增长</li>
    <li>消费电子周期复苏预期</li>
  </ul>
  <p><strong>看空逻辑（被市场忽视的风险）：</strong></p>
  <ul>
    <li class="red">毛利率17.6%极低——被动元器件本质是标准化大宗商品，竞争激烈，提价能力弱</li>
    <li class="red">净利率5.1%——即使营收翻倍，净利润也仅6亿，PE仍超100x</li>
    <li class="red">FCFE持续为负——需要不断融资/投入才能维持增长，非"轻资产高回报"模式</li>
    <li class="red">行业周期性——MLCC上一轮景气顶点在2018年，此后价格持续下行，景气持续性待验证</li>
    <li class="red">应收账款18亿——占营收30%，回款风险不可忽视</li>
  </ul>
</div>

<div class="section">
  <h2>六、估值评估</h2>
  <h3>6.1 绝对估值</h3>
  <table class="data-table">
    <tr><th>估值指标</th><th>当前值</th><th>合理参考</th><th>偏离程度</th></tr>
    <tr><td>PE(TTM)</td><td class="red">272x</td><td>电子元器件行业中枢25-35x</td><td class="red">偏高7-10倍</td></tr>
    <tr><td>PE(远期)</td><td class="red">236x</td><td>-</td><td class="red">仍然极高</td></tr>
    <tr><td>PB</td><td class="red">6.7x</td><td>行业中枢2-3x</td><td class="red">偏高2-3倍</td></tr>
    <tr><td>PS</td><td class="red">13.9x</td><td>行业中枢1.5-2.5x</td><td class="red">偏高5-9倍</td></tr>
    <tr><td>股息率</td><td class="red">0.21%</td><td>最低可接受2%</td><td class="red">几乎无分红</td></tr>
  </table>

  <h3>6.2 估值还原场景</h3>
  <table class="data-table">
    <tr><th>场景</th><th>假设净利润</th><th>合理PE</th><th>对应市值</th><th>对应股价</th></tr>
    <tr><td>悲观(行业下行)</td><td>2亿</td><td>25x</td><td>50亿</td><td class="red">约4.3元</td></tr>
    <tr><td>中性(当前延续)</td><td>3亿</td><td>30x</td><td>90亿</td><td>约7.8元</td></tr>
    <tr><td>乐观(翻倍增长)</td><td>6亿</td><td>35x</td><td>210亿</td><td class="green">约18元</td></tr>
    <tr><td>极端乐观(5倍增长)</td><td>15亿</td><td>40x</td><td>600亿</td><td class="green">约52元</td></tr>
  </table>
  <p style="color:var(--red);font-weight:600;">即使最极端乐观场景下（净利润增长5倍至15亿），合理股价也仅约52元，仍低于当前72.24元。当前835亿市值隐含的预期需要净利润达20亿+(增长7倍)，对毛利率17%的元器件企业几乎不可能。</p>
</div>

<div class="section">
  <h2>七、多维度评估雷达</h2>
  <div id="radar_chart" class="chart-box" style="height:360px;"></div>
  <p>评分维度说明（1-5分，5为最优）：</p>
  <ul>
    <li><strong>盈利能力 2分</strong>：毛利率17.6%，净利率5.1%，ROE仅2.4%</li>
    <li><strong>成长性 3分</strong>：营收增速尚可，但净利增速能否持续存疑</li>
    <li><strong>估值合理性 1分</strong>：PE 272x，PB 6.7x，估值极端偏高</li>
    <li><strong>现金流质量 2分</strong>：经营CF Q1转负，FCFE持续为负</li>
    <li><strong>筹码结构 1分</strong>：股东户数暴增140%，筹码极度分散</li>
    <li><strong>技术形态 2分</strong>：5/10日线破位，MACD/KDJ空头信号</li>
  </ul>
</div>

<div class="section" style="border: 2px solid var(--red);">
  <h2 style="color:var(--red);">八、风险提示</h2>
  <table class="data-table">
    <tr><th>风险类型</th><th>等级</th><th>说明</th></tr>
    <tr><td class="red">估值泡沫风险</td><td><span class="tag tag-red">极高</span></td><td>PE 272x、PB 6.7x，即使业绩翻倍也无法支撑</td></tr>
    <tr><td class="red">流动性风险</td><td><span class="tag tag-red">极高</span></td><td>跌停缩量=流动性枯竭，后续可能连续跌停</td></tr>
    <tr><td class="red">筹码分散风险</td><td><span class="tag tag-red">极高</span></td><td>股东户数21.7万，人均持股5327股，散户主导</td></tr>
    <tr><td>行业周期风险</td><td><span class="tag tag-orange">高</span></td><td>MLCC价格周期性波动，景气高点后通常2-3年下行</td></tr>
    <tr><td>盈利质量风险</td><td><span class="tag tag-orange">高</span></td><td>经营CF Q1转负，应收账款18亿占营收30%</td></tr>
    <tr><td>政策/贸易风险</td><td><span class="tag tag-blue">中</span></td><td>电子元器件出口依赖，关税政策变动影响</td></tr>
  </table>
</div>

<div class="footer">
  <p>数据来源：腾讯自选股行情接口(westock-data) + 本地CSV历史数据</p>
  <p>报告生成时间：""" + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
  <p>本报告仅供参考，不构成投资建议。投资有风险，决策需谨慎。</p>
</div>

</div>

<script>
document.addEventListener('DOMContentLoaded', function() {

  // K线数据
  var dates = """ + D + """;
  var ohlc = """ + O + """;
  var volumes = """ + V + """;
  var ma5 = """ + MA5 + """;
  var ma10 = """ + MA10 + """;
  var ma20 = """ + MA20 + """;
  var ma60 = """ + MA60 + """;
  var volColors = """ + VC + """;

  // 技术指标数据
  var rsiVals = """ + RSI + """;
  var macdDif = """ + MDIF + """;
  var macdDea = """ + MDEA + """;
  var macdBarVals = """ + MBAR + """;

  // 财务数据
  var revData = """ + rev_data + """;
  var npData = """ + np_data + """;
  var revLabels = """ + rev_labels + """;

  // 分红数据
  var divYears = """ + div_years + """;
  var divAmounts = """ + div_amounts + """;

  // 资金流向
  var fundLabels = """ + fund_labels + """;
  var fundValues = """ + fund_values + """;

  // 股东户数
  var shLabels = """ + sh_labels + """;
  var shValues = """ + sh_values + """;

  // ---- K线图 ----
  var klineChart = echarts.init(document.getElementById('kline_chart'));

  var klineData = [];
  for (var i = 0; i < ohlc.length; i++) {
    var item = ohlc[i];
    var color = item[1] >= item[0] ? '#e74c3c' : '#27ae60';
    klineData.push({
      value: item,
      itemStyle: { color: color, color0: color, borderColor: color, borderColor0: color }
    });
  }

  var volData = [];
  for (var i = 0; i < volumes.length; i++) {
    volData.push({
      value: volumes[i],
      itemStyle: { color: volColors[i] }
    });
  }

  klineChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['日K', '成交量', 'MA5', 'MA10', 'MA20', 'MA60'] },
    grid: [
      { left: '8%', right: '4%', top: '8%', height: '55%' },
      { left: '8%', right: '4%', top: '70%', height: '22%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates, gridIndex: 1 }
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitLine: { show: false } },
      { scale: true, gridIndex: 1, splitLine: { show: false } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 60, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', bottom: '4%', start: 60, end: 100 }
    ],
    series: [
      {
        name: '日K', type: 'candlestick', data: klineData,
        xAxisIndex: 0, yAxisIndex: 0,
        itemStyle: { color: '#e74c3c', color0: '#27ae60', borderColor: '#e74c3c', borderColor0: '#27ae60' }
      },
      { name: 'MA5', type: 'line', data: ma5, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1 }, symbol: 'none' },
      { name: 'MA10', type: 'line', data: ma10, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1 }, symbol: 'none' },
      { name: 'MA20', type: 'line', data: ma20, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1 }, symbol: 'none' },
      { name: 'MA60', type: 'line', data: ma60, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1, color: '#d62728' }, symbol: 'none' },
      {
        name: '成交量', type: 'bar', data: volData,
        xAxisIndex: 1, yAxisIndex: 1, itemStyle: { opacity: 0.7 }
      }
    ]
  });

  // ---- 技术指标(RSI+MACD) ----
  var techChart = echarts.init(document.getElementById('tech_chart'));

  var macdBarData = [];
  for (var i = 0; i < macdBarVals.length; i++) {
    var v = macdBarVals[i];
    if (v === null) { macdBarData.push({ value: null }); continue; }
    macdBarData.push({
      value: v,
      itemStyle: { color: v >= 0 ? '#e74c3c' : '#27ae60' }
    });
  }

  techChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['RSI(14)', 'DIF', 'DEA', 'MACD柱'] },
    grid: [
      { left: '8%', right: '4%', top: '8%', height: '38%' },
      { left: '8%', right: '4%', top: '55%', height: '38%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates, gridIndex: 1 }
    ],
    yAxis: [
      { type: 'value', name: 'RSI', min: 0, max: 100, gridIndex: 0, splitLine: { show: false } },
      { type: 'value', name: 'MACD', gridIndex: 1, splitLine: { show: false } }
    ],
    series: [
      { name: 'RSI(14)', type: 'line', data: rsiVals, xAxisIndex: 0, yAxisIndex: 0, lineStyle: { color: '#9467bd', width: 1.5 }, symbol: 'none' },
      { name: 'DIF', type: 'line', data: macdDif, xAxisIndex: 1, yAxisIndex: 1, lineStyle: { color: '#e74c3c', width: 1.5 }, symbol: 'none' },
      { name: 'DEA', type: 'line', data: macdDea, xAxisIndex: 1, yAxisIndex: 1, lineStyle: { color: '#3498db', width: 1.5 }, symbol: 'none' },
      { name: 'MACD柱', type: 'bar', data: macdBarData, xAxisIndex: 1, yAxisIndex: 1, itemStyle: { opacity: 0.7 } }
    ]
  });

  // ---- 资金流向 ----
  var fundChart = echarts.init(document.getElementById('fund_chart'));
  fundChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}万元' },
    series: [{
      type: 'pie', radius: ['35%', '65%'],
      data: [
        { name: '主力净流入', value: fundValues[0], itemStyle: { color: fundValues[0] > 0 ? '#e74c3c' : '#27ae60' } },
        { name: '超大单净流入', value: fundValues[1], itemStyle: { color: fundValues[1] > 0 ? '#e74c3c' : '#27ae60' } },
        { name: '中单净流入', value: fundValues[2], itemStyle: { color: fundValues[2] > 0 ? '#e74c3c' : '#27ae60' } },
        { name: '小单净流入', value: fundValues[3], itemStyle: { color: fundValues[3] > 0 ? '#e74c3c' : '#27ae60' } }
      ]
    }]
  });

  // ---- 股东户数 ----
  var shChart = echarts.init(document.getElementById('shareholder_chart'));
  shChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: shLabels },
    yAxis: { type: 'value', name: '户数(万)' },
    series: [{
      type: 'bar',
      data: shValues,
      itemStyle: { color: '#e74c3c' },
      label: { show: true, position: 'top' }
    }]
  });

  // ---- 收入与利润 ----
  var revChart = echarts.init(document.getElementById('revenue_chart'));
  revChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['营收(亿)', '净利(亿)'] },
    xAxis: { type: 'category', data: revLabels },
    yAxis: [
      { type: 'value', name: '营收(亿)' },
      { type: 'value', name: '净利(亿)' }
    ],
    series: [
      { name: '营收(亿)', type: 'bar', data: revData },
      { name: '净利(亿)', type: 'line', yAxisIndex: 1, data: npData }
    ]
  });

  // ---- 分红 ----
  var divChart = echarts.init(document.getElementById('dividend_chart'));
  divChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: divYears },
    yAxis: { type: 'value', name: '每10股派息(元)' },
    series: [{
      type: 'bar',
      data: divAmounts,
      itemStyle: { color: '#3498db' },
      label: { show: true, position: 'top' }
    }]
  });

  // ---- 雷达图 ----
  var radarChart = echarts.init(document.getElementById('radar_chart'));
  radarChart.setOption({
    radar: {
      indicator: [
        { name: '盈利能力', max: 5 },
        { name: '成长性', max: 5 },
        { name: '估值合理性', max: 5 },
        { name: '现金流质量', max: 5 },
        { name: '筹码结构', max: 5 },
        { name: '技术形态', max: 5 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: [2, 3, 1, 2, 1, 2],
        name: '风华高科综合评分',
        areaStyle: { color: 'rgba(231,76,60,0.3)' },
        lineStyle: { color: '#e74c3c' },
        itemStyle: { color: '#e74c3c' }
      }]
    }]
  });

  // 窗口resize自适应
  window.addEventListener('resize', function() {
    klineChart.resize();
    techChart.resize();
    fundChart.resize();
    shChart.resize();
    revChart.resize();
    divChart.resize();
    radarChart.resize();
  });
});
</script>
</body>
</html>""")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    print("HTML报告已生成: " + output_path)
    return output_path


if __name__ == '__main__':
    csv_path = '/Users/talina/Desktop/quantitative-finance/docs/stock_data_fhgk.csv'
    output_path = '/Users/talina/Desktop/quantitative-finance/docs/fhgk_analysis_report.html'
    generate_html(csv_path, output_path)
