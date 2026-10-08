import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Explorador de operación",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Carga los datos que utilizará la aplicación."""
    datos = pd.read_csv("datos_ejemplo.csv")
    datos["Fecha"] = pd.to_datetime(datos["Fecha"])
    return datos


df = cargar_datos()

st.title("Explorador de operación")
st.caption("Aplicación inicial para explorar resultados por área y región.")

# TODO OBLIGATORIO: escribe tu nombre completo.
st.write("**Desarrollado por:** José Carlos Granados García")

st.sidebar.header("Filtros")

areas_disponibles = sorted(df["Área"].unique())
areas_seleccionadas = st.sidebar.multiselect(
    "Área",
    options=areas_disponibles,
    default=areas_disponibles,
)

# Filtro 2 (OPCIÓN A): Rango de fechas
fecha_min = df["Fecha"].min().date()
fecha_max = df["Fecha"].max().date()
rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)
# Mientras el usuario elige, date_input puede devolver solo una fecha
if isinstance(rango_fechas, (tuple, list)) and len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
else:
    fecha_inicio = fecha_fin = (
        rango_fechas[0] if isinstance(rango_fechas, (tuple, list)) else rango_fechas
    )

# Aplicar ambos filtros
df_filtrado = df[
    (df["Área"].isin(areas_seleccionadas))
    & (df["Fecha"].dt.date >= fecha_inicio)
    & (df["Fecha"].dt.date <= fecha_fin)
].copy()

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados. Ajusta el área o las fechas.")
    st.stop()
 
 
# ================================================================
# INDICADORES (OPCIÓN A: st.metric)
# ================================================================
total_casos = int(df_filtrado["Casos"].sum())
casos_por_fecha = (
    df_filtrado.groupby("Fecha", as_index=False)["Casos"]
    .sum()
    .sort_values("Fecha")
)
promedio_diario = casos_por_fecha["Casos"].mean()
dia_maximo = casos_por_fecha.loc[casos_por_fecha["Casos"].idxmax()]
num_areas = df_filtrado["Área"].nunique()
 
# Delta: último registro vs. el anterior
if len(casos_por_fecha) >= 2:
    ultimo = int(casos_por_fecha["Casos"].iloc[-1])
    penultimo = int(casos_por_fecha["Casos"].iloc[-2])
    delta_ultimo = ultimo - penultimo
else:
    ultimo = int(casos_por_fecha["Casos"].iloc[-1])
    delta_ultimo = None
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de casos", f"{total_casos:,}")
col2.metric("Promedio por fecha", f"{promedio_diario:,.1f}")
col3.metric(
    "Último registro",
    f"{ultimo:,}",
    delta=delta_ultimo,
    help="Cambio respecto a la fecha anterior",
)
col4.metric(
    "Día con más casos",
    dia_maximo["Fecha"].strftime("%d/%m/%Y"),
    help=f"{int(dia_maximo['Casos']):,} casos",
)
 
st.caption(f"Áreas incluidas: {num_areas} · Periodo: {fecha_inicio} a {fecha_fin}")
 
 
# ================================================================
# VISTAS (OPCIÓN A: st.tabs)
# ================================================================
tab_resumen, tab_datos = st.tabs(["📈 Resumen gráfico", "📋 Detalle de datos"])
 
with tab_resumen:
    fig_linea = px.line(
        casos_por_fecha,
        x="Fecha",
        y="Casos",
        markers=True,
        title="Casos por fecha",
    )
    st.plotly_chart(fig_linea, width="stretch")
 
    casos_por_area = (
        df_filtrado.groupby("Área", as_index=False)["Casos"]
        .sum()
        .sort_values("Casos", ascending=False)
    )
    fig_barras = px.bar(
        casos_por_area,
        x="Área",
        y="Casos",
        text_auto=True,
        title="Casos por área",
    )
    st.plotly_chart(fig_barras, width="stretch")
 
with tab_datos:
    st.subheader("Datos filtrados")
    st.dataframe(df_filtrado, width="stretch", hide_index=True)
    st.download_button(
        "Descargar CSV filtrado",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name="datos_filtrados.csv",
        mime="text/csv",
    )

