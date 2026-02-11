import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import calendar

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Dashboard Pasta Mía",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# PALETAS DE COLORES MEJORADAS
# ============================================
COLOR_PALETTES = {
    # Colores vibrantes para gráficos de barras
    'vibrant': [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
        '#F1948A', '#7DCEA0', '#F5B7B1', '#AED6F1', '#F9E79F'
    ],
    # Colores para gráficos de pastel
    'pie': [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
    ],
    # Colores degradados para líneas
    'gradient': ['#0EA5E9', '#2563EB', '#7C3AED', '#DB2777'],
    # Colores para métricas
    'metrics': {
        'ventas': '#0EA5E9',
        'productos': '#8B5CF6',
        'transacciones': '#10B981',
        'ticket': '#F59E0B'
    }
}

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0EA5E9 0%, #8B5CF6 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
        border-top: 4px solid var(--metric-color);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #1E293B;
        letter-spacing: -0.02em;
    }
    .metric-label {
        color: #64748B;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .filter-section {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .price-variation {
        background: #E0F2FE;
        color: #0369A1;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #7DD3FC;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CARGA Y LIMPIEZA DE DATOS - CORREGIDO
# ============================================
@st.cache_data
def load_and_clean_data():
    """Carga y limpia los datos del Excel"""
    try:
        df = pd.read_excel('ventas.xlsx', sheet_name=0)
    except:
        st.warning("⚠️ No se encontró el archivo 'ventas.xlsx'. Usando datos de ejemplo...")
        return create_sample_data()
    
    # Limpieza de datos
    df = df.dropna(subset=['Fecha', 'Cliente', 'Producto'], how='all')
    df = df[df['Cliente'] != 'NaN']
    df = df[df['Producto'] != 'NaN']
    
    # Convertir tipos
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha'])
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    
    # ============================================
    # MANEJO DE COLUMNA DE IMPORTE - CORREGIDO
    # ============================================
    # Verificar si existe la columna 'Importe_Venta' o 'Precio'
    if 'Importe_Venta' in df.columns:
        df['Importe_Venta'] = pd.to_numeric(df['Importe_Venta'], errors='coerce')
    elif 'Precio' in df.columns:
        df['Importe_Venta'] = pd.to_numeric(df['Precio'], errors='coerce')
    else:
        # Buscar cualquier columna que pueda contener el importe
        posibles = ['Total', 'Monto', 'Venta', 'Importe']
        encontrada = False
        for col in posibles:
            if col in df.columns:
                df['Importe_Venta'] = pd.to_numeric(df[col], errors='coerce')
                encontrada = True
                break
        if not encontrada:
            st.error("❌ No se encontró una columna de importe/venta en el archivo")
            return pd.DataFrame()
    
    # Eliminar filas con valores nulos en Importe_Venta o Cantidad
    df = df.dropna(subset=['Importe_Venta', 'Cantidad'])
    
    # Calcular precio unitario
    df['Precio_Unitario'] = df['Importe_Venta'] / df['Cantidad']
    
    return df

@st.cache_data
def create_sample_data():
    """Crea datos de ejemplo si no hay Excel"""
    np.random.seed(42)
    fechas = pd.date_range(start='2026-01-01', end='2026-01-31', freq='D')
    
    clientes = ['SECRETS MAROMA', 'GRAND PALLADIUM', 'IBEROSTAR', 'DREAMS', 'HYATT ZIVA']
    vendedores = ['Eduardo Cantillo', 'José Carlos', 'Javier']
    productos = ['TOMATE ENTERO PELADO', 'PENNE MEDITERRANEA', 'SPAGUETTI', 'FUSILLI', 'ARROZ ARBORIO']
    lineas = ['TOMATES', 'PASTAS', 'ARROCES', 'ACEITES Y VINAGRES']
    giros = ['Foodservice', 'B2B', 'Retail']
    
    data = []
    for fecha in fechas:
        for _ in range(np.random.randint(10, 30)):
            producto = np.random.choice(productos)
            cantidad = np.random.randint(10, 500)
            precio_unitario = np.random.choice([96.5, 97.5, 98, 100, 102])
            
            row = {
                'Fecha': fecha,
                'Cliente': np.random.choice(clientes),
                'Vendedor': np.random.choice(vendedores),
                'Giro': np.random.choice(giros),
                'Producto': producto,
                'Descripcion': producto,
                'Marca': 'MEDITERRANEA',
                'Linea': np.random.choice(lineas),
                'Cantidad': cantidad,
                'Importe_Venta': cantidad * precio_unitario,
                'Precio_Unitario': precio_unitario
            }
            data.append(row)
    
    return pd.DataFrame(data)

# ============================================
# FUNCIONES DE ANÁLISIS
# ============================================
@st.cache_data
def analyze_data(df, filters):
    """Realiza todos los análisis en una sola pasada"""
    
    mask = pd.Series(True, index=df.index)
    
    if filters['linea'] != 'Todas':
        mask &= (df['Linea'] == filters['linea'])
    if filters['producto'] != 'Todos':
        mask &= (df['Producto'] == filters['producto'])
    if filters['giro'] != 'Todos':
        mask &= (df['Giro'] == filters['giro'])
    if filters['cliente'] != 'Todos':
        mask &= (df['Cliente'] == filters['cliente'])
    if filters['vendedor'] != 'Todos':
        mask &= (df['Vendedor'] == filters['vendedor'])
    
    mask &= (df['Fecha'].dt.date >= filters['fecha_inicio'])
    mask &= (df['Fecha'].dt.date <= filters['fecha_fin'])
    
    df_filtered = df[mask].copy()
    
    metrics = {
        'total_ventas': df_filtered['Importe_Venta'].sum(),
        'total_cantidad': df_filtered['Cantidad'].sum(),
        'num_transacciones': len(df_filtered),
        'ticket_promedio': df_filtered['Importe_Venta'].mean() if len(df_filtered) > 0 else 0
    }
    
    ventas_por_linea = df_filtered.groupby('Linea').agg({
        'Importe_Venta': 'sum',
        'Cantidad': 'sum'
    }).reset_index().sort_values('Importe_Venta', ascending=False)
    
    ventas_por_producto = df_filtered.groupby(['Producto', 'Descripcion']).agg({
        'Importe_Venta': 'sum',
        'Cantidad': 'sum',
        'Precio_Unitario': lambda x: x.nunique()
    }).reset_index().sort_values('Importe_Venta', ascending=False).head(10)
    
    ventas_por_giro = df_filtered.groupby('Giro').agg({
        'Importe_Venta': 'sum',
        'Cantidad': 'sum'
    }).reset_index().sort_values('Importe_Venta', ascending=False)
    
    ventas_por_cliente = df_filtered.groupby('Cliente').agg({
        'Importe_Venta': 'sum',
        'Cantidad': 'sum'
    }).reset_index().sort_values('Importe_Venta', ascending=False).head(10)
    
    ventas_por_vendedor = df_filtered.groupby('Vendedor').agg({
        'Importe_Venta': 'sum',
        'Cantidad': 'sum'
    }).reset_index().sort_values('Importe_Venta', ascending=False)
    
    ventas_por_dia = df_filtered.groupby(df_filtered['Fecha'].dt.day).agg({
        'Importe_Venta': 'sum',
        'Cantidad': 'sum'
    }).reset_index().rename(columns={'Fecha': 'Dia'})
    
    # ============================================
    # DETECCIÓN DE VARIACIÓN EN PRECIOS DE COMPRA
    # ============================================
    variacion_precios = df_filtered.groupby(['Producto', 'Descripcion']).agg({
        'Precio_Unitario': lambda x: list(set(round(v, 2) for v in x)),
        'Cantidad': 'count'
    }).reset_index()
    
    variacion_precios['num_precios'] = variacion_precios['Precio_Unitario'].apply(len)
    variacion_precios = variacion_precios[
        variacion_precios['num_precios'] > 1
    ].sort_values('Cantidad', ascending=False).head(10)
    
    return {
        'filtered': df_filtered,
        'metrics': metrics,
        'by_linea': ventas_por_linea,
        'by_producto': ventas_por_producto,
        'by_giro': ventas_por_giro,
        'by_cliente': ventas_por_cliente,
        'by_vendedor': ventas_por_vendedor,
        'by_dia': ventas_por_dia,
        'variacion_precios': variacion_precios
    }

# ============================================
# FUNCIONES DE VISUALIZACIÓN MEJORADAS
# ============================================
def format_money(value):
    return f"${value:,.2f}"

def format_number(value):
    return f"{value:,.0f}"

def create_line_chart(data):
    """Gráfico de línea con degradado"""
    fig = px.line(
        data, 
        x='Dia', 
        y='Importe_Venta',
        markers=True
    )
    fig.update_traces(
        line=dict(color='#0EA5E9', width=3),
        marker=dict(size=8, color='#0EA5E9', line=dict(width=2, color='white'))
    )
    fig.update_layout(
        xaxis_title="Día",
        yaxis_title="Importe de Venta ($)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif"),
        height=400,
        showlegend=False,
        title=None
    )
    fig.update_yaxes(tickprefix="$", gridcolor='#E2E8F0', gridwidth=1, title_text="Importe de Venta ($)")
    fig.update_xaxes(gridcolor='#E2E8F0', gridwidth=1)
    return fig

def create_bar_chart_vibrant(data, x, y, orientation='v'):
    """
    Gráfico de barras con colores vibrantes y DIFERENTES para cada barra
    """
    if orientation == 'v':
        fig = go.Figure()
        # Añadir cada barra con un color diferente
        for i, row in data.iterrows():
            fig.add_trace(go.Bar(
                x=[row[x]],
                y=[row[y]],
                name=row[x],
                marker_color=COLOR_PALETTES['vibrant'][i % len(COLOR_PALETTES['vibrant'])],
                hovertemplate=f"<b>{row[x]}</b><br>Importe: ${row[y]:,.2f}<br>Cantidad: {row['Cantidad']:,.0f}<extra></extra>"
            ))
        
        fig.update_layout(
            barmode='group',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter, sans-serif"),
            height=400,
            showlegend=False,
            title=None,
            hovermode='x'
        )
        fig.update_yaxes(gridcolor='#E2E8F0', gridwidth=1, tickprefix="$", title_text="Importe de Venta ($)")
        fig.update_xaxes(gridcolor='#E2E8F0', gridwidth=1)
        
    else:  # horizontal
        fig = go.Figure()
        # Añadir cada barra con un color diferente (ordenadas de mayor a menor)
        data_sorted = data.sort_values(y, ascending=True)
        for i, row in data_sorted.iterrows():
            fig.add_trace(go.Bar(
                y=[row[x]],
                x=[row[y]],
                name=row[x],
                orientation='h',
                marker_color=COLOR_PALETTES['vibrant'][i % len(COLOR_PALETTES['vibrant'])],
                hovertemplate=f"<b>{row[x]}</b><br>Importe: ${row[y]:,.2f}<br>Cantidad: {row['Cantidad']:,.0f}<extra></extra>"
            ))
        
        fig.update_layout(
            barmode='group',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter, sans-serif"),
            height=500,
            showlegend=False,
            title=None,
            hovermode='y'
        )
        fig.update_xaxes(gridcolor='#E2E8F0', gridwidth=1, tickprefix="$", title_text="Importe de Venta ($)")
        fig.update_yaxes(gridcolor='#E2E8F0', gridwidth=1)
    
    return fig

def create_pie_chart_vibrant(data, values, names):
    """Gráfico de pastel con colores vibrantes"""
    fig = go.Figure(data=[go.Pie(
        labels=data[names],
        values=data[values],
        hole=0.4,
        marker=dict(
            colors=COLOR_PALETTES['pie'][:len(data)],
            line=dict(color='white', width=2)
        ),
        textinfo='percent+label',
        textposition='inside',
        hovertemplate="<b>%{label}</b><br>Importe: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif"),
        height=400,
        showlegend=False,
        title=None
    )
    return fig

# ============================================
# INTERFAZ PRINCIPAL
# ============================================
def main():
    df = load_and_clean_data()
    
    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #1E293B;'>🎯 FILTROS</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        lineas = ['Todas'] + sorted(df['Linea'].dropna().unique().tolist())
        productos = ['Todos'] + sorted(df['Producto'].dropna().unique().tolist())
        giros = ['Todos'] + sorted(df['Giro'].dropna().unique().tolist())
        clientes = ['Todos'] + sorted(df['Cliente'].dropna().unique().tolist())
        vendedores = ['Todos'] + sorted(df['Vendedor'].dropna().unique().tolist())
        
        linea = st.selectbox("📌 Línea", lineas, key="filter_linea")
        producto = st.selectbox("📦 Producto", productos, key="filter_producto")
        giro = st.selectbox("🏢 Giro", giros, key="filter_giro")
        cliente = st.selectbox("👥 Cliente", clientes, key="filter_cliente")
        vendedor = st.selectbox("👤 Vendedor", vendedores, key="filter_vendedor")
        
        st.markdown("---")
        st.markdown("### 📅 Rango de Fechas")
        
        fecha_min = df['Fecha'].min().date()
        fecha_max = df['Fecha'].max().date()
        
        fecha_inicio = st.date_input(
            "Fecha Inicio",
            value=fecha_min,
            min_value=fecha_min,
            max_value=fecha_max,
            key="date_start"
        )
        
        fecha_fin = st.date_input(
            "Fecha Fin",
            value=fecha_max,
            min_value=fecha_min,
            max_value=fecha_max,
            key="date_end"
        )
        
        if st.button("🔄 Resetear Filtros", key="reset_button"):
            st.session_state.clear()
            st.rerun()
    
    filters = {
        'linea': linea,
        'producto': producto,
        'giro': giro,
        'cliente': cliente,
        'vendedor': vendedor,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    
    analysis = analyze_data(df, filters)
    df_filtered = analysis['filtered']
    metrics = analysis['metrics']
    
    # Header
    st.markdown('<h1 class="main-header">📊 Dashboard Pasta Mía</h1>', unsafe_allow_html=True)
    
    # Info período
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"**📈 Período:** {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
    with col2:
        st.markdown(f"**💼 Transacciones:** {format_number(metrics['num_transacciones'])}")
    
    
    
    # ============================================
    # MÉTRICAS PRINCIPALES CON COLORES PERSONALIZADOS
    # ============================================
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {COLOR_PALETTES['metrics']['ventas']};">
            <div class="metric-label">VENTAS TOTALES</div>
            <div class="metric-value">{format_money(metrics['total_ventas'])}</div>
            <div style="color: #64748B; font-size: 0.875rem;">{format_number(metrics['num_transacciones'])} transacciones</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {COLOR_PALETTES['metrics']['productos']};">
            <div class="metric-label">PRODUCTOS VENDIDOS</div>
            <div class="metric-value">{format_number(metrics['total_cantidad'])}</div>
            <div style="color: #64748B; font-size: 0.875rem;">unidades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {COLOR_PALETTES['metrics']['transacciones']};">
            <div class="metric-label">TRANSACCIONES</div>
            <div class="metric-value">{format_number(metrics['num_transacciones'])}</div>
            <div style="color: #64748B; font-size: 0.875rem;">{((metrics['num_transacciones']/len(df))*100):.1f}% del total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {COLOR_PALETTES['metrics']['ticket']};">
            <div class="metric-label">TICKET PROMEDIO</div>
            <div class="metric-value">{format_money(metrics['ticket_promedio'])}</div>
            <div style="color: #64748B; font-size: 0.875rem;">por transacción</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # GRÁFICO DE VENTAS DIARIAS
    # ============================================
    st.markdown("---")
    st.subheader("📈 Ventas Diarias")
    
    if not analysis['by_dia'].empty:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_daily = create_line_chart(analysis['by_dia'])
            st.plotly_chart(fig_daily, use_container_width=True, key="chart_daily_sales")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No hay datos para el período seleccionado")
    
    # ============================================
    # GRÁFICOS PRIMERA FILA - COLORES VIBRANTES
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💼 Ventas por Línea")
        if not analysis['by_linea'].empty:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                fig_linea = create_bar_chart_vibrant(
                    analysis['by_linea'], 
                    'Linea', 
                    'Importe_Venta',
                    orientation='v'
                )
                st.plotly_chart(fig_linea, use_container_width=True, key="chart_linea")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎯 Ventas por Giro")
        if not analysis['by_giro'].empty:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                fig_giro = create_pie_chart_vibrant(
                    analysis['by_giro'],
                    'Importe_Venta',
                    'Giro'
                )
                st.plotly_chart(fig_giro, use_container_width=True, key="chart_giro")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # GRÁFICOS SEGUNDA FILA - BARRAS HORIZONTALES CON COLORES DIFERENTES
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Top 10 Productos")
        if not analysis['by_producto'].empty:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                analysis['by_producto']['Display'] = analysis['by_producto'].apply(
                    lambda x: x['Descripcion'][:30] + '...' if len(str(x['Descripcion'])) > 30 else x['Descripcion'],
                    axis=1
                )
                fig_productos = create_bar_chart_vibrant(
                    analysis['by_producto'],
                    'Display',
                    'Importe_Venta',
                    orientation='h'
                )
                st.plotly_chart(fig_productos, use_container_width=True, key="chart_productos")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("👥 Top 10 Clientes")
        if not analysis['by_cliente'].empty:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                fig_clientes = create_bar_chart_vibrant(
                    analysis['by_cliente'],
                    'Cliente',
                    'Importe_Venta',
                    orientation='v'
                )
                st.plotly_chart(fig_clientes, use_container_width=True, key="chart_clientes")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # VENTAS POR VENDEDOR
    # ============================================
    st.markdown("---")
    st.subheader("🎖️ Ventas por Vendedor")
    
    if not analysis['by_vendedor'].empty:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_vendedor = create_bar_chart_vibrant(
                analysis['by_vendedor'],
                'Vendedor',
                'Importe_Venta',
                orientation='v'
            )
            st.plotly_chart(fig_vendedor, use_container_width=True, key="chart_vendedor")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # TABLA DE TRANSACCIONES
    # ============================================
    st.markdown("---")
    st.subheader("📋 Últimas Transacciones")
    
    if not df_filtered.empty:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            table_data = df_filtered.sort_values('Fecha', ascending=False).head(10)[
                ['Fecha', 'Cliente', 'Descripcion', 'Producto', 'Cantidad', 'Importe_Venta', 'Vendedor']
            ].copy()
            
            table_data['Fecha'] = table_data['Fecha'].dt.strftime('%d/%m/%Y')
            table_data['Importe_Venta'] = table_data['Importe_Venta'].apply(lambda x: f"${x:,.2f}")
            table_data['Cantidad'] = table_data['Cantidad'].apply(lambda x: f"{x:,.0f}")
            table_data['Descripcion'] = table_data['Descripcion'].fillna(table_data['Producto'])
            
            st.dataframe(
                table_data.drop('Producto', axis=1),
                column_config={
                    "Fecha": "Fecha",
                    "Cliente": "Cliente",
                    "Descripcion": "Producto",
                    "Cantidad": "Cantidad",
                    "Importe_Venta": "Importe Total",
                    "Vendedor": "Vendedor"
                },
                use_container_width=True,
                hide_index=True,
                key="transactions_table"
            )
            
            if len(df_filtered) > 10:
                st.caption(f"Mostrando 10 de {format_number(len(df_filtered))} transacciones")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # FOOTER
    # ============================================
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Dashboard Pasta Mía**")
    with col2:
        st.markdown(f"**📈 Mostrando:** {format_number(analysis['filtered'].shape[0])} de {format_number(df.shape[0])} transacciones")
    with col3:
        if len(analysis['variacion_precios']) > 0:
            st.markdown(f"**📊 {len(analysis['variacion_precios'])} productos con variación en importes de venta**")
    
    st.caption("Los importes unitarios varían según cliente, volumen y condiciones comerciales")

if __name__ == "__main__":
    main()
