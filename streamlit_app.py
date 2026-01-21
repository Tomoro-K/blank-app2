"""
探索的データ分析（EDA）自動化アプリ
CSVファイルをアップロードするだけで、データの概要把握を自動で行います。
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

# 日本語フォントの設定
matplotlib.rcParams['font.family'] = ['MS Gothic', 'Hiragino Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

# ページ設定
st.set_page_config(
    page_title="EDA自動化ツール",
    page_icon="📊",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown('<p class="main-header">📊 EDA自動化ツール</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">CSVファイルをアップロードするだけで、データ分析を自動化します</p>', unsafe_allow_html=True)

# セッション状態の初期化
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None

# サイドバー：ファイルアップロード
with st.sidebar:
    st.header("📁 データアップロード")
    uploaded_file = st.file_uploader(
        "CSVファイルを選択してください",
        type=['csv'],
        help="UTF-8またはShift-JISエンコーディングのCSVファイルに対応しています"
    )
    
    if uploaded_file is not None:
        # エンコーディングの選択
        encoding = st.selectbox(
            "エンコーディング",
            ['utf-8', 'shift-jis', 'cp932'],
            help="ファイルが正しく読み込めない場合は別のエンコーディングを試してください"
        )
        
        try:
            df = pd.read_csv(uploaded_file, encoding=encoding)
            st.session_state.df = df.copy()
            st.session_state.original_df = df.copy()
            st.success(f"✅ データを読み込みました！\n\n行数: {len(df):,} 行\n列数: {len(df.columns)} 列")
        except Exception as e:
            st.error(f"❌ ファイルの読み込みに失敗しました: {str(e)}")
    
    st.divider()
    
    # 前処理オプション
    st.header("🔧 前処理オプション")
    
    if st.session_state.df is not None:
        if st.button("🔄 元のデータに戻す", use_container_width=True):
            st.session_state.df = st.session_state.original_df.copy()
            st.success("データをリセットしました")
            st.rerun()
        
        st.subheader("欠損値の処理")
        
        fill_method = st.selectbox(
            "補完方法を選択",
            ['選択してください', '平均値で補完', '中央値で補完', '最頻値で補完', '0で補完', '欠損行を削除']
        )
        
        if fill_method != '選択してください':
            # 数値列のみ取得
            numeric_cols = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()
            
            target_cols = st.multiselect(
                "対象列を選択",
                numeric_cols if fill_method != '欠損行を削除' else st.session_state.df.columns.tolist(),
                help="空の場合は全ての数値列が対象になります"
            )
            
            if st.button("✨ 前処理を実行", type="primary", use_container_width=True):
                df = st.session_state.df.copy()
                cols = target_cols if target_cols else numeric_cols
                
                if fill_method == '平均値で補完':
                    for col in cols:
                        if col in df.columns and df[col].dtype in [np.float64, np.int64]:
                            df[col] = df[col].fillna(df[col].mean())
                    st.success("平均値で欠損値を補完しました")
                    
                elif fill_method == '中央値で補完':
                    for col in cols:
                        if col in df.columns and df[col].dtype in [np.float64, np.int64]:
                            df[col] = df[col].fillna(df[col].median())
                    st.success("中央値で欠損値を補完しました")
                    
                elif fill_method == '最頻値で補完':
                    for col in cols:
                        if col in df.columns:
                            mode_val = df[col].mode()
                            if len(mode_val) > 0:
                                df[col] = df[col].fillna(mode_val[0])
                    st.success("最頻値で欠損値を補完しました")
                    
                elif fill_method == '0で補完':
                    for col in cols:
                        if col in df.columns:
                            df[col] = df[col].fillna(0)
                    st.success("0で欠損値を補完しました")
                    
                elif fill_method == '欠損行を削除':
                    cols_to_check = target_cols if target_cols else df.columns.tolist()
                    before_rows = len(df)
                    df = df.dropna(subset=cols_to_check)
                    after_rows = len(df)
                    st.success(f"欠損行を削除しました（{before_rows - after_rows}行削除）")
                
                st.session_state.df = df
                st.rerun()

# メインコンテンツ
if st.session_state.df is not None:
    df = st.session_state.df
    
    # タブで表示を切り替え
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 データプレビュー", 
        "📈 基本統計量", 
        "🔍 欠損値分析", 
        "📊 可視化", 
        "🔗 相関分析"
    ])
    
    # タブ1: データプレビュー
    with tab1:
        st.subheader("データプレビュー")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("行数", f"{len(df):,}")
        with col2:
            st.metric("列数", f"{len(df.columns)}")
        with col3:
            st.metric("数値列", f"{len(df.select_dtypes(include=[np.number]).columns)}")
        with col4:
            st.metric("カテゴリ列", f"{len(df.select_dtypes(include=['object']).columns)}")
        
        st.divider()
        
        # 表示行数の選択
        n_rows = st.slider("表示行数", min_value=5, max_value=min(100, len(df)), value=10)
        st.dataframe(df.head(n_rows), use_container_width=True)
        
        st.divider()
        
        # データ型情報
        st.subheader("列情報")
        col_info = pd.DataFrame({
            '列名': df.columns,
            'データ型': df.dtypes.astype(str),
            '非欠損数': df.count().values,
            '欠損数': df.isnull().sum().values,
            'ユニーク数': df.nunique().values
        })
        st.dataframe(col_info, use_container_width=True)
    
    # タブ2: 基本統計量
    with tab2:
        st.subheader("基本統計量")
        
        # 数値列の統計量
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            st.markdown("### 📊 数値列の統計量")
            stats = numeric_df.describe().T
            stats['範囲'] = stats['max'] - stats['min']
            stats['変動係数'] = (stats['std'] / stats['mean'] * 100).round(2)
            st.dataframe(stats.round(3), use_container_width=True)
        else:
            st.info("数値列がありません")
        
        # カテゴリ列の統計量
        category_df = df.select_dtypes(include=['object'])
        if not category_df.empty:
            st.markdown("### 📝 カテゴリ列の統計量")
            cat_stats = category_df.describe().T
            st.dataframe(cat_stats, use_container_width=True)
            
            st.markdown("### 📋 カテゴリ値の分布")
            selected_cat = st.selectbox("列を選択", category_df.columns)
            if selected_cat:
                value_counts = df[selected_cat].value_counts()
                st.bar_chart(value_counts)
    
    # タブ3: 欠損値分析
    with tab3:
        st.subheader("欠損値分析")
        
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        
        missing_df = pd.DataFrame({
            '欠損数': missing,
            '欠損率(%)': missing_pct
        }).sort_values('欠損数', ascending=False)
        
        # 欠損値サマリー
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("欠損値を含む列数", f"{(missing > 0).sum()}")
        with col2:
            st.metric("総欠損値数", f"{missing.sum():,}")
        with col3:
            st.metric("データ全体の欠損率", f"{(missing.sum() / (len(df) * len(df.columns)) * 100):.2f}%")
        
        st.divider()
        
        # 欠損値テーブル
        st.markdown("### 列ごとの欠損値")
        st.dataframe(missing_df, use_container_width=True)
        
        # 欠損値のヒートマップ
        if missing.sum() > 0:
            st.markdown("### 欠損値のヒートマップ")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 欠損値のあるの列のみ表示
            missing_cols = missing[missing > 0].index.tolist()
            if missing_cols:
                sns.heatmap(
                    df[missing_cols].isnull().T,
                    cbar=True,
                    cmap='YlOrRd',
                    yticklabels=True,
                    ax=ax
                )
                ax.set_xlabel('行インデックス')
                ax.set_ylabel('列名')
                ax.set_title('欠損値パターン（赤が欠損）')
                st.pyplot(fig)
                plt.close()
        else:
            st.success("🎉 データに欠損値はありません！")
    
    # タブ4: 可視化
    with tab4:
        st.subheader("データ可視化")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            # ヒストグラム
            st.markdown("### 📊 ヒストグラム")
            hist_cols = st.multiselect(
                "表示する列を選択（最大6列）",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))],
                max_selections=6
            )
            
            if hist_cols:
                n_cols = min(3, len(hist_cols))
                n_rows = (len(hist_cols) + n_cols - 1) // n_cols
                
                fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows))
                if n_rows * n_cols == 1:
                    axes = [axes]
                else:
                    axes = axes.flatten()
                
                for i, col in enumerate(hist_cols):
                    axes[i].hist(df[col].dropna(), bins=30, edgecolor='white', alpha=0.7, color='#667eea')
                    axes[i].set_title(col)
                    axes[i].set_xlabel('値')
                    axes[i].set_ylabel('頻度')
                
                # 余分なサブプロットを非表示
                for j in range(len(hist_cols), len(axes)):
                    axes[j].set_visible(False)
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
            st.divider()
            
            # 箱ひげ図
            st.markdown("### 📦 箱ひげ図")
            box_cols = st.multiselect(
                "表示する列を選択（箱ひげ図用）",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))],
                key="box_cols"
            )
            
            if box_cols:
                fig, ax = plt.subplots(figsize=(10, 6))
                df[box_cols].boxplot(ax=ax)
                ax.set_title('箱ひげ図')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
            st.divider()
            
            # 散布図
            st.markdown("### 🔵 散布図")
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X軸", numeric_cols, key="scatter_x")
            with col2:
                y_col = st.selectbox("Y軸", numeric_cols, index=min(1, len(numeric_cols)-1), key="scatter_y")
            
            if x_col and y_col:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(df[x_col], df[y_col], alpha=0.5, c='#667eea')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f'{x_col} vs {y_col}')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        else:
            st.info("数値列がないため、可視化できません")
    
    # タブ5: 相関分析
    with tab5:
        st.subheader("相関分析")
        
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) >= 2:
            # 相関行列
            corr = numeric_df.corr()
            
            st.markdown("### 🔗 相関行列（ヒートマップ）")
            fig, ax = plt.subplots(figsize=(12, 10))
            mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
            sns.heatmap(
                corr,
                mask=mask,
                annot=True,
                fmt='.2f',
                cmap='RdBu_r',
                center=0,
                square=True,
                linewidths=0.5,
                ax=ax,
                vmin=-1,
                vmax=1
            )
            ax.set_title('相関行列')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            st.divider()
            
            # 強い相関のペアを表示
            st.markdown("### 📊 強い相関を持つ変数ペア")
            
            threshold = st.slider("相関係数の閾値", 0.0, 1.0, 0.5, 0.1)
            
            # 上三角行列から強い相関を抽出
            strong_corr = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    if abs(corr.iloc[i, j]) >= threshold:
                        strong_corr.append({
                            '変数1': corr.columns[i],
                            '変数2': corr.columns[j],
                            '相関係数': corr.iloc[i, j]
                        })
            
            if strong_corr:
                strong_corr_df = pd.DataFrame(strong_corr)
                strong_corr_df = strong_corr_df.sort_values('相関係数', key=abs, ascending=False)
                st.dataframe(strong_corr_df, use_container_width=True)
            else:
                st.info(f"閾値 {threshold} 以上の相関を持つペアはありません")
            
            st.divider()
            
            # ペアプロット（サンプル）
            if len(numeric_df.columns) <= 6 and len(df) > 0:
                st.markdown("### 🔍 ペアプロット")
                st.caption("※データ量が多い場合は時間がかかる場合があります")
                
                if st.button("ペアプロットを生成", type="primary"):
                    with st.spinner("ペアプロットを生成中..."):
                        # サンプリング（データが多い場合）
                        sample_df = numeric_df.sample(n=min(500, len(numeric_df)), random_state=42)
                        
                        fig = sns.pairplot(sample_df, diag_kind='hist', plot_kws={'alpha': 0.5})
                        fig.fig.suptitle('ペアプロット', y=1.02)
                        st.pyplot(fig)
                        plt.close()
            elif len(numeric_df.columns) > 6:
                st.info("列数が多いため、ペアプロットは表示しません（6列以下で表示可能）")
        else:
            st.info("相関分析には2つ以上の数値列が必要です")

else:
    # アップロード前の案内
    st.info("👈 左のサイドバーからCSVファイルをアップロードしてください")
    
    # 機能説明
    st.markdown("---")
    st.markdown("## 🎯 このツールでできること")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📋 データ概要
        - データプレビュー
        - 列情報の確認
        - データ型の把握
        """)
    
    with col2:
        st.markdown("""
        ### 📈 統計分析
        - 基本統計量の算出
        - 欠損値の検出と可視化
        - 相関分析
        """)
    
    with col3:
        st.markdown("""
        ### 🔧 前処理機能
        - 欠損値の補完（平均/中央値/最頻値）
        - 欠損行の削除
        - データのリセット
        """)
    
    st.markdown("---")
    st.markdown("## 📊 可視化機能")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **ヒストグラム**: 数値データの分布を確認
        - **箱ひげ図**: 外れ値やデータの散らばりを把握
        - **散布図**: 2変数間の関係を可視化
        """)
    
    with col2:
        st.markdown("""
        - **相関行列ヒートマップ**: 変数間の相関を一覧
        - **ペアプロット**: 全変数ペアの関係を表示
        - **欠損値ヒートマップ**: 欠損パターンを可視化
        """)

# フッター
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #888;">Made with ❤️ using Streamlit</p>',
    unsafe_allow_html=True
)
