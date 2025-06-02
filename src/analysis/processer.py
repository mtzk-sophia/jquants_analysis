import os
from typing import Dict, List

import numpy as np
import pandas as pd


def calculate_sma(data: pd.DataFrame, window: int) -> pd.Series:
    """単純移動平均（SMA）を計算"""
    return data.rolling(window=window).mean()


def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> Dict[str, pd.Series]:
    """ボリンジャーバンドを計算"""
    sma = calculate_sma(data, window)
    std = data.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return {
        'middle': sma,
        'upper': upper_band,
        'lower': lower_band
    }


def calculate_ema(data: pd.DataFrame, span: int) -> pd.Series:
    """指数移動平均（EMA）を計算"""
    return data.ewm(span=span, adjust=False).mean()


def calculate_macd(data: pd.DataFrame) -> Dict[str, pd.Series]:
    """MACDを計算"""
    ema12 = calculate_ema(data, 12)
    ema26 = calculate_ema(data, 26)
    macd_line = ema12 - ema26
    signal_line = calculate_ema(macd_line, 9)
    histogram = macd_line - signal_line
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def detect_macd_crossovers(macd_line: pd.Series, signal_line: pd.Series) -> Dict[str, pd.Series]:
    """MACDのゴールデンクロスとデッドクロスを検出
    
    Returns:
        Dict[str, pd.Series]: 
            - golden_cross: ゴールデンクロスの日はTrue
            - dead_cross: デッドクロスの日はTrue
    """
    # 前日との差分を計算
    macd_diff = macd_line - signal_line
    prev_macd_diff = macd_diff.shift(1)
    
    # クロスオーバーの検出
    golden_cross = (prev_macd_diff < 0) & (macd_diff > 0)  # 下から上へのクロス
    dead_cross = (prev_macd_diff > 0) & (macd_diff < 0)    # 上から下へのクロス
    
    return {
        'golden_cross': golden_cross,
        'dead_cross': dead_cross
    }


def process_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """株価データを読み込み、技術指標を計算"""
    
    # 会社ごとにグループ化して処理
    result_dfs = []
    for company in df['Code'].unique():
        company_data = df[df['Code'] == company].copy()
        
        # 終値を使用して技術指標を計算
        close_prices = company_data['Close']
        
        # 移動平均の計算
        company_data['SMA5'] = calculate_sma(close_prices, 5)
        company_data['SMA25'] = calculate_sma(close_prices, 25)
        company_data['SMA75'] = calculate_sma(close_prices, 75)
        
        # ボリンジャーバンドの計算
        bb = calculate_bollinger_bands(close_prices)
        company_data['BB_middle'] = bb['middle']
        company_data['BB_upper'] = bb['upper']
        company_data['BB_lower'] = bb['lower']
        
        # MACDの計算
        macd = calculate_macd(close_prices)
        company_data['MACD'] = macd['macd']
        company_data['MACD_signal'] = macd['signal']
        company_data['MACD_histogram'] = macd['histogram']
        
        # MACDのクロスオーバー検出
        crossovers = detect_macd_crossovers(macd['macd'], macd['signal'])
        company_data['MACD_golden_cross'] = crossovers['golden_cross']
        company_data['MACD_dead_cross'] = crossovers['dead_cross']
        
        result_dfs.append(company_data)
    
    # 全データを結合
    result_df = pd.concat(result_dfs)
    return result_df
