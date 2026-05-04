import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Comparador Dólar vs USDT", layout="centered", page_icon="💸")

st.title("💸 Comparador Dólar Oficial vs USDT")
st.markdown("Busca cotizaciones de USDT, compara contra el Dólar Oficial / 0.96 y revisa cotizaciones bancarias.")

def obtener_datos():
    url_usd = "https://api.comparadolar.ar/usd"
    url_usdt = "https://api.comparadolar.ar/usdt"
    
    try:
        # --- 1. DÓLAR OFICIAL Y BANCOS ---
        res_usd = requests.get(url_usd).json()
        
        # Buscar el Dólar Oficial (Banco Nación)
        oficial = next((item for item in res_usd if item.get('slug') == 'banco-nacion'), None)
        
        if not oficial or not oficial.get('ask'):
            st.error("No se encontró la cotización de venta del Banco Nación.")
            return
            
        precio_oficial = oficial.get('ask')
        precio_objetivo = precio_oficial / 0.96
        
        st.info(f"**Dólar Oficial Venta (Nación):** ${precio_oficial:,.2f}  |  **Valor Objetivo (Oficial / 0.96):** ${precio_objetivo:,.2f}")
        
        # Filtrar solo bancos
        st.subheader("🏦 Dónde comprar Dólares Oficiales")
        bancos = [b for b in res_usd if b.get('isBank') == True and b.get('ask')]
        
        if bancos:
            # Ordenar del más barato al más caro
            bancos = sorted(bancos, key=lambda x: x['ask'])
            datos_bancos = [{
                "Banco": b.get('prettyName') or b.get('name'),
                "Compra": f"${b.get('bid'):,.2f}" if b.get('bid') else "-",
                "Venta": f"${b.get('ask'):,.2f}"
            } for b in bancos]
            
            df_bancos = pd.DataFrame(datos_bancos)
            st.dataframe(df_bancos, use_container_width=True, hide_index=True)
        else:
            st.warning("No hay cotizaciones de bancos disponibles en este momento.")

        # --- 2. OPORTUNIDADES USDT ---
        st.divider()
        st.subheader("🪙 USDT con diferencia ≤ $10 al objetivo")
        res_usdt = requests.get(url_usdt).json()
        
        resultados = []
        info_nexo = None

        for quote in res_usdt:
            nombre = quote.get('prettyName') or quote.get('slug')
            slug = quote.get('slug')
            usdt_venta = quote.get('totalAsk') or quote.get('ask')
            
            if usdt_venta:
                # Calculamos la diferencia
                diferencia_absoluta = abs(precio_objetivo - usdt_venta)
                diferencia_real = usdt_venta - precio_objetivo
                
                # Guardamos Nexo si lo encontramos en el bucle
                if slug == 'nexo':
                    info_nexo = {
                        "venta": usdt_venta,
                        "diferencia": diferencia_real
                    }
                
                # Filtramos los que cumplen la condición de los 10 pesos
                if diferencia_absoluta <= 10:
                    resultados.append({
                        "Exchange": nombre,
                        "USDT Venta": f"${usdt_venta:,.2f}",
                        "Diferencia": f"${diferencia_absoluta:,.2f}"
                    })
                    
        if resultados:
            df_usdt = pd.DataFrame(resultados).sort_values(by="Diferencia")
            st.dataframe(df_usdt, use_container_width=True, hide_index=True)
        else:
            st.warning("Ningún exchange cumple con la condición de diferencia de $10.")
            
        # --- 3. COTIZACIÓN EN NEXO ---
        st.divider()
        st.subheader("🔵 Cotización particular en Nexo")
        if info_nexo:
            st.metric(
                label="USDT Venta (Nexo)", 
                value=f"${info_nexo['venta']:,.2f}", 
                delta=f"${info_nexo['diferencia']:,.2f} vs Objetivo",
                delta_color="inverse" # Muestra rojo si está por encima del objetivo, verde si está por debajo
            )
        else:
            st.info("La cotización de Nexo no está disponible en este momento.")
            
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")

# Botón para actualizar la pantalla sin recargar la página entera
if st.button("🔄 Actualizar Cotizaciones"):
    st.cache_data.clear()

obtener_datos()
