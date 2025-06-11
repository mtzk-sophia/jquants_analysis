import os
from typing import Dict, List

import numpy as np
import pandas as pd


def calculate_sma(data: pd.DataFrame, window: int) -> pd.Series:
    """単純移動平均（SMA）を計算"""
    return data.rolling(window=window).mean()


def calculate_bollinger_bands(data: pd.DataFrame, window: int=25, num_std: float=2.0) -> Dict[str, pd.Series]:
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


def detect_band_walk(close: pd.Series, upper_band: pd.Series, lower_band: pd.Series, window: int = 25, threshold: float = 0.02) -> Dict[str, pd.Series]:
    """バンドウォークを上部と下部に分けて検出する関数
    
    Args:
        close: 終値
        upper_band: ボリンジャーバンドの上限
        lower_band: ボリンジャーバンドの下限
        window: 判定する期間（デフォルト25日）
        threshold: 価格変動の閾値（デフォルト2%）
    
    Returns:
        Dict[str, pd.Series]: 
            - upper_band_walk: 上部バンドウォークの場合はTrue
            - lower_band_walk: 下部バンドウォークの場合はTrue
    """
    # 価格の変動率を計算
    price_change = close.pct_change(window).abs()
    
    # バンドの幅に対する価格の位置を計算（0-1の範囲）
    band_width = upper_band - lower_band
    price_position = (close - lower_band) / band_width
    
    # 上部バンドウォークの条件：
    # 1. 価格変動が閾値以下
    # 2. 価格がバンドの上部にある（0.7-0.9の範囲）
    upper_band_walk = (price_change <= threshold) & (price_position.between(0.7, 0.9))
    
    # 下部バンドウォークの条件：
    # 1. 価格変動が閾値以下
    # 2. 価格がバンドの下部にある（0.1-0.3の範囲）
    lower_band_walk = (price_change <= threshold) & (price_position.between(0.1, 0.3))
    
    return {
        'upper_band_walk': upper_band_walk,
        'lower_band_walk': lower_band_walk
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
        
        # バンドウォークの検出（上部と下部）
        band_walks = detect_band_walk(
            close_prices,
            company_data['BB_upper'],
            company_data['BB_lower']
        )
        company_data['UpperBandWalk'] = band_walks['upper_band_walk']
        company_data['LowerBandWalk'] = band_walks['lower_band_walk']
        
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
