import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Comparador Dólar vs USDT", layout="centered", page_icon="💸")

st.title("💸 Comparador Dólar Oficial vs USDT")
st.markdown("Busca cotizaciones de USDT cuya venta tenga una diferencia de **10 pesos o menos** con el Dólar Oficial / 0.96.")

def obtener_datos():
    url_usd = "https://api.comparadolar.ar/usd"
    url_usdt = "https://api.comparadolar.ar/usdt"
    
    try:
        # Traer Dólar Oficial
        res_usd = requests.get(url_usd).json()
        oficial = next((item for item in res_usd if item.get('slug') == 'banco-nacion'), None)
        
        if not oficial or not oficial.get('ask'):
            st.error("No se encontró la cotización de venta del Banco Nación.")
            return
            
        precio_oficial = oficial.get('ask')
        precio_objetivo = precio_oficial / 0.96
        
        st.info(f"**Dólar Oficial Venta:** ${precio_oficial:,.2f}  |  **Valor Objetivo (Oficial / 0.96):** ${precio_objetivo:,.2f}")
        
        # Traer USDT
        res_usdt = requests.get(url_usdt).json()
        
        resultados = []
        for quote in res_usdt:
            nombre = quote.get('prettyName') or quote.get('slug')
            usdt_venta = quote.get('totalAsk') or quote.get('ask')
            
            if usdt_venta:
                diferencia = abs(precio_objetivo - usdt_venta)
                
                # Filtrar los que tengan 10 pesos o menos de diferencia
                if diferencia <= 10:
                    resultados.append({
                        "Exchange": nombre,
                        "USDT Venta": f"${usdt_venta:,.2f}",
                        "Diferencia": f"${diferencia:,.2f}"
                    })
                    
        if resultados:
            st.success("¡Oportunidades encontradas!")
            # Crear un DataFrame para mostrarlo lindo en Streamlit
            df = pd.DataFrame(resultados)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Ningún exchange cumple con la condición de diferencia de $10 en este momento.")
            
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")

# Botón para actualizar manualmente
if st.button("🔄 Actualizar Cotizaciones"):
    st.cache_data.clear()

obtener_datos()
