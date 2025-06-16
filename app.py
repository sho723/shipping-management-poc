import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="海運管理システム PoC",
    page_icon="🚢",
    layout="wide"
)

# サンプルデータ生成関数
@st.cache_data
def generate_sample_data():
    """デモ用サンプルデータ生成"""
    
    # 船舶データ
    ships_data = [
        {"ship_id": "BULK_001", "ship_name": "海王丸", "capacity": 60000, "status": "航海中"},
        {"ship_id": "BULK_002", "ship_name": "大洋丸", "capacity": 58000, "status": "荷役中"},
        {"ship_id": "BULK_003", "ship_name": "太平丸", "capacity": 62000, "status": "沖待ち"},
        {"ship_id": "BULK_004", "ship_name": "東海丸", "capacity": 59000, "status": "入港準備"},
    ]
    
    # 航海データ
    voyages_data = []
    cargo_patterns = [
        {"pattern": "CORN+MILO", "corn_ratio": 0.6, "milo_ratio": 0.4, "barley_ratio": 0.0},
        {"pattern": "CORN+BARLEY", "corn_ratio": 0.7, "milo_ratio": 0.0, "barley_ratio": 0.3},
        {"pattern": "MILO+BARLEY", "corn_ratio": 0.0, "milo_ratio": 0.55, "barley_ratio": 0.45},
    ]
    
    for i, ship in enumerate(ships_data):
        pattern = random.choice(cargo_patterns)
        total_cargo = ship["capacity"] - random.randint(2000, 5000)
        
        voyage = {
            "voyage_id": f"V2024{i+1:03d}",
            "ship_name": ship["ship_name"],
            "ship_status": ship["status"],
            "total_cargo": total_cargo,
            "cargo_pattern": pattern["pattern"],
            "corn_tons": int(total_cargo * pattern["corn_ratio"]),
            "milo_tons": int(total_cargo * pattern["milo_ratio"]),
            "barley_tons": int(total_cargo * pattern["barley_ratio"]),
            "loading_port": random.choice(["Seattle", "Vancouver", "New Orleans"]),
            "eta": datetime.now() + timedelta(days=random.randint(1, 10)),
            "discharge_ports": random.choice([["CHIBA"], ["YOKOHAMA"], ["CHIBA", "NAGOYA"], ["YOKOHAMA", "CHIBA"]]),
        }
        voyages_data.append(voyage)
    
    return pd.DataFrame(ships_data), pd.DataFrame(voyages_data)

def main():
    st.title("🚢 海運管理システム PoC")
    st.markdown("---")
    
    # サイドバー
    st.sidebar.title("📋 ナビゲーション")
    page = st.sidebar.selectbox(
        "ページ選択",
        ["🏠 ダッシュボード", "📊 合積み分析", "🎯 最適化シミュレーション", "📈 実績レポート"]
    )
    
    # データ読み込み
    ships_df, voyages_df = generate_sample_data()
    
    if page == "🏠 ダッシュボード":
        show_dashboard(ships_df, voyages_df)
    elif page == "📊 合積み分析":
        show_cargo_analysis(voyages_df)
    elif page == "🎯 最適化シミュレーション":
        show_optimization_sim()
    elif page == "📈 実績レポート":
        show_performance_report(voyages_df)

def show_dashboard(ships_df, voyages_df):
    st.header("📊 現在の運航状況")
    
    # KPIメトリクス
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sailing_ships = len(ships_df[ships_df['status'] == '航海中'])
        st.metric("航海中", f"{sailing_ships}隻", "正常")
    
    with col2:
        waiting_ships = len(ships_df[ships_df['status'] == '沖待ち'])
        st.metric("沖待ち", f"{waiting_ships}隻", "12時間平均")
    
    with col3:
        loading_ships = len(ships_df[ships_df['status'] == '荷役中'])
        st.metric("荷役中", f"{loading_ships}隻", "進行中")
    
    with col4:
        total_cargo = voyages_df['total_cargo'].sum()
        st.metric("総取扱量", f"{total_cargo:,}t", "+15% vs前月")
    
    st.markdown("---")
    
    # 船舶状況テーブル
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚢 船舶別運航状況")
        
        # 詳細情報付きテーブル
        display_df = voyages_df[['ship_name', 'cargo_pattern', 'total_cargo', 'loading_port', 'eta']].copy()
        display_df['eta'] = display_df['eta'].dt.strftime('%m/%d %H:%M')
        display_df.columns = ['船舶名', '貨物構成', '積載量(t)', '積地', 'ETA']
        
        st.dataframe(display_df, use_container_width=True)
    
    with col2:
        st.subheader("📈 船舶ステータス")
        
        # ステータス分布
        status_counts = ships_df['status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="船舶ステータス分布"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

def show_cargo_analysis(voyages_df):
    st.header("📊 合積み構成分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("貨物パターン別頻度")
        pattern_counts = voyages_df['cargo_pattern'].value_counts()
        
        fig = px.bar(
            x=pattern_counts.index,
            y=pattern_counts.values,
            title="合積みパターン使用頻度",
            labels={'x': '貨物パターン', 'y': '航海数'}
        )
        fig.update_traces(marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("貨物タイプ別取扱量")
        
        cargo_totals = {
            'CORN': voyages_df['corn_tons'].sum(),
            'MILO': voyages_df['milo_tons'].sum(),
            'BARLEY': voyages_df['barley_tons'].sum()
        }
        
        fig = px.pie(
            values=list(cargo_totals.values()),
            names=list(cargo_totals.keys()),
            title="貨物タイプ別構成比"
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            marker_colors=['#FFD93D', '#6BCF7F', '#4D96FF']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 詳細分析テーブル
    st.subheader("🔍 航海別貨物詳細")
    
    analysis_df = voyages_df[['voyage_id', 'ship_name', 'cargo_pattern', 'corn_tons', 'milo_tons', 'barley_tons', 'total_cargo']].copy()
    analysis_df.columns = ['航海ID', '船舶名', '貨物パターン', 'コーン(t)', 'マイロ(t)', '飼料麦(t)', '合計(t)']
    
    st.dataframe(analysis_df, use_container_width=True)

def show_optimization_sim():
    st.header("🎯 合積み最適化シミュレーション")
    
    st.info("💡 異なる貨物構成での収益性をシミュレーションできます")
    
    # 入力パラメータ
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 条件設定")
        
        ship_capacity = st.number_input(
            "船舶容量 (トン)",
            min_value=50000,
            max_value=70000,
            value=60000,
            step=1000
        )
        
        corn_ratio = st.slider("コーン比率", 0.0, 1.0, 0.6, 0.1)
        milo_ratio = st.slider("マイロ比率", 0.0, 1.0-corn_ratio, 0.3, 0.1)
        barley_ratio = 1.0 - corn_ratio - milo_ratio
        
        st.write(f"**飼料麦比率**: {barley_ratio:.1f}")
        
        # 価格設定（デモ用）
        corn_price = st.number_input("コーン単価 ($/t)", value=250.0)
        milo_price = st.number_input("マイロ単価 ($/t)", value=240.0)
        barley_price = st.number_input("飼料麦単価 ($/t)", value=280.0)
    
    with col2:
        st.subheader("📊 最適化結果")
        
        if st.button("🔍 最適化実行", type="primary"):
            # 計算実行
            corn_tons = int(ship_capacity * corn_ratio)
            milo_tons = int(ship_capacity * milo_ratio)
            barley_tons = int(ship_capacity * barley_ratio)
            
            total_revenue = (
                corn_tons * corn_price +
                milo_tons * milo_price +
                barley_tons * barley_price
            )
            
            # 結果表示
            st.success("✅ 最適化完了!")
            
            result_col1, result_col2 = st.columns(2)
            
            with result_col1:
                st.metric("コーン", f"{corn_tons:,}t", f"{corn_ratio:.1%}")
                st.metric("マイロ", f"{milo_tons:,}t", f"{milo_ratio:.1%}")
                st.metric("飼料麦", f"{barley_tons:,}t", f"{barley_ratio:.1%}")
            
            with result_col2:
                st.metric("総売上", f"${total_revenue:,.0f}")
                st.metric("平均単価", f"${total_revenue/ship_capacity:.0f}/t")
                
                # 効率性スコア（デモ用）
                efficiency_score = random.randint(75, 95)
                st.metric("効率スコア", f"{efficiency_score}点", "良好")
            
            # 構成比チャート
            cargo_data = {
                'Cargo': ['コーン', 'マイロ', '飼料麦'],
                'Tons': [corn_tons, milo_tons, barley_tons],
                'Revenue': [corn_tons * corn_price, milo_tons * milo_price, barley_tons * barley_price]
            }
            
            fig = px.bar(
                cargo_data,
                x='Cargo',
                y=['Tons'],
                title="最適化後の貨物構成",
                labels={'value': 'トン数', 'Cargo': '貨物タイプ'}
            )
            st.plotly_chart(fig, use_container_width=True)

def show_performance_report(voyages_df):
    st.header("📈 実績レポート")
    
    # 期間選択
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("📅 分析期間")
        period = st.selectbox(
            "期間選択",
            ["今月", "先月", "過去3ヶ月", "過去半年"]
        )
        
        cargo_filter = st.multiselect(
            "貨物フィルター",
            ["CORN+MILO", "CORN+BARLEY", "MILO+BARLEY"],
            default=["CORN+MILO", "CORN+BARLEY", "MILO+BARLEY"]
        )
    
    with col2:
        st.subheader("📊 パフォーマンス指標")
        
        # フィルター適用
        filtered_df = voyages_df[voyages_df['cargo_pattern'].isin(cargo_filter)]
        
        # 時系列データ（デモ用）
        date_range = pd.date_range(start='2024-01-01', end='2024-06-30', freq='M')
        monthly_cargo = [random.randint(150000, 200000) for _ in date_range]
        
        monthly_df = pd.DataFrame({
            'Month': date_range,
            'Cargo_Volume': monthly_cargo
        })
        
        fig = px.line(
            monthly_df,
            x='Month',
            y='Cargo_Volume',
            title=f"月別取扱量推移 ({period})",
            labels={'Cargo_Volume': '取扱量 (t)', 'Month': '月'}
        )
        fig.update_traces(line_color='#FF6B6B', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    # サマリー統計
    st.subheader("📋 期間サマリー")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        total_voyages = len(filtered_df)
        st.metric("総航海数", f"{total_voyages}回")
    
    with summary_col2:
        avg_cargo = filtered_df['total_cargo'].mean()
        st.metric("平均積載量", f"{avg_cargo:,.0f}t")
    
    with summary_col3:
        utilization = random.randint(85, 95)
        st.metric("船腹利用率", f"{utilization}%", "良好")
    
    with summary_col4:
        on_time_rate = random.randint(88, 96)
        st.metric("定時到着率", f"{on_time_rate}%", "+2%")

if __name__ == "__main__":
    main()
