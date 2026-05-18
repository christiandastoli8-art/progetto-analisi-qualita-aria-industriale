import csv  
import numpy as np  
import matplotlib.pyplot as plt 
import streamlit as st
from datetime import datetime 

st.set_page_config(page_title = "404 Brain Not Found", layout = "wide") 

c1, c2, c3 = st.columns([1, 5, 1]) 
with c2: 
    st.title("Centralina di Sicurezza - Qualità dell'Aria", anchor = False) 

st.divider() 

if "autenticato" not in st.session_state:    
    st.session_state["autenticato"] = False 
   
if not st.session_state["autenticato"]:
    st.write("") 
    st.write("")

    col_sx, col_cen, col_dx = st.columns([1.5, 1, 1.5])
    
    with col_cen:
        st.subheader("ACCESSO OPERATORE", anchor = False)
        
        with st.form("login_nativo"):
            password_inserita = st.text_input("Password", type = "password", placeholder = "Password Aziendale...", label_visibility = "collapsed")
            pulsante_accesso = st.form_submit_button("LOGIN", width = 'stretch')

            if pulsante_accesso:
                if password_inserita == "abc":
                    st.session_state["autenticato"] = True 
                    st.rerun()
                elif password_inserita != "": 
                    st.error("Password errata.")

else:  
    if "soglia_pm" not in st.session_state: 
        st.session_state["soglia_pm"] = 25.0 
    if "soglia_co2" not in st.session_state:
        st.session_state["soglia_co2"] = 1000 
    
    @st.cache_data 
    def carica_e_pulisci_dati(nome_file):
        misurazioni = [] 
        anomalie_rilevate = [] 
        
        with open(nome_file, mode = "r", encoding = "utf-8-sig") as file:
            reader = csv.reader(file, delimiter = ",")
            next(reader) 
            pos = 2  
            for riga in reader: 
                pm = float(riga[3])
                co2 = int(riga[4])
                temp = float(riga[5])
                umidità = float(riga[6])
                
                if temp > 50: anomalie_rilevate.append(f"Riga {pos}: Temp anomala ({temp}°C)")
                if pm < 0: anomalie_rilevate.append(f"riga {pos}: PM2.5 negativo ({pm})")
                if co2 > 2000: anomalie_rilevate.append(f"riga {pos}: CO2 fuori scala ({co2}ppm)")
                if umidità > 75 or umidità < 15: anomalie_rilevate.append(f"riga {pos}: Umidità sospetta ({umidità}%)") 
                
                nuova_misurazione = [riga[0], riga[1], riga[2], pm, co2, temp, umidità]
                misurazioni.append(nuova_misurazione)
                pos += 1  
        return misurazioni, anomalie_rilevate 

    dati, report_anomalie = carica_e_pulisci_dati("qualita_aria.csv") 
    zone_estratte = [r[2] for r in dati]
    zone_uniche = sorted(list(set(zone_estratte)))

    # BARRA LATERALE 
    st.sidebar.header("Menu Principale", anchor = False)
    pagina = st.sidebar.radio("Seleziona area:", ["Home e Statistiche", "Gestione Allarmi", "Analisi Grafica"])
    
    st.sidebar.divider()
    st.sidebar.subheader("Impostazioni Visive", anchor = False)
    tema_grafici = st.sidebar.radio("Testi Grafici:", ["Chiari (Dark Mode)", "Scuri (Light Mode)"])

    st.sidebar.divider()
    if st.sidebar.button("Disconetti"):
        st.session_state["autenticato"] = False  
        st.rerun() 

    st.sidebar.divider() 
    st.sidebar.write("#### Team di Sviluppo")
    st.sidebar.write("""
    - ***Antonio Astorino***
    - ***Christian Dastoli***
    - ***Francesco Graziano***
    - ***Simone Sauro***
    """)

    # PAGINA 1 - HOME 
    if pagina == "Home e Statistiche":
        st.header("Statistiche Generali", anchor = False)
        st.success("Sistema sbloccato. Accesso ai dati consentito.")
        
        with st.expander("Visualizza Log di Sitema"):
            if report_anomalie:
                for anomalia in report_anomalie:
                    st.warning(anomalia)
            else:
                st.success("Nessuna anomalia strutturale rilevata nei sensori.")
        
        col = st.columns(len(zone_uniche))
        for i, zona in enumerate(zone_uniche):
            temp_zona = [r[5] for r in dati if r[2] == zona]
            pm_zona = [r[3] for r in dati if r[2] == zona]
            co2_zona = [r[4] for r in dati if r[2] == zona]
            umid_zona = [r[6] for r in dati if r[2] == zona]
            
            with col[i]:
                st.subheader(zona, anchor=False)
                
                st.metric("Temperatura Media", f"{np.mean(temp_zona):.1f} °C")
                st.caption(f"Max: {np.max(temp_zona):.1f}°C | Min: {np.min(temp_zona):.1f}°C")
                
                st.metric("PM2.5 Medio", f"{np.mean(pm_zona):.1f} µg/m³")
                st.caption(f"Max: {np.max(pm_zona):.1f} | Min: {np.min(pm_zona):.1f}")
                
                st.metric("CO2 Media", f"{np.mean(co2_zona):.0f} ppm")
                st.caption(f"Max: {np.max(co2_zona)} | Min: {np.min(co2_zona)}")
                
                st.metric("Umidità Media", f"{np.mean(umid_zona):.1f} %")
                st.caption(f"Max: {np.max(umid_zona):.1f}% | Min: {np.min(umid_zona):.1f}%")

    # PAGINA 2 - ALLARMI
    elif pagina == "Gestione Allarmi":
        st.header("Controllo Soglie", anchor = False)
        
        if "temp_pm" not in st.session_state:
            st.session_state["temp_pm"] = st.session_state["soglia_pm"]
        if "temp_co2" not in st.session_state:
            st.session_state["temp_co2"] = st.session_state["soglia_co2"]
            
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Imposta soglia massima PM2.5:", min_value = 0.0, step = 1.0, key = "temp_pm")
        with c2:
            st.number_input("Imposta soglia massima CO2 (ppm):", min_value = 0, step = 50, key = "temp_co2")

        st.session_state["soglia_pm"] = st.session_state["temp_pm"]
        st.session_state["soglia_co2"] = st.session_state["temp_co2"]

        soglia_pm = st.session_state["soglia_pm"]
        soglia_co2 = st.session_state["soglia_co2"]

        allarmi_trovati = []
        for riga in dati:
            if riga[3] > soglia_pm or riga[4] > soglia_co2:
                allarmi_trovati.append({
                    "Data": riga[0], "Ora": riga[1], "Zona": riga[2],
                    "PM2.5": riga[3], "CO2": riga[4]
                })

        if len(allarmi_trovati) > 0:
            st.error(f"ATTENZIONE: Rilevati {len(allarmi_trovati)} superamenti delle soglie di sicurezza!")
            st.dataframe(allarmi_trovati, width = 'stretch') 
            
            testo_file = "======================================================================\n"
            testo_file += "REGISTRO ALLARMI - CENTRALINA DI SICUREZZA\n"
            testo_file += "======================================================================\n"
            testo_file += f"{'DATA':<12} | {'ORA':<6} | {'ZONA':<6} | {'PM2.5':<8} | {'CO2':<8}\n"
            testo_file += "-" * 70 + "\n"
            for a in allarmi_trovati:
                testo_file += f"{a['Data']:<12} | {a['Ora']:<6} | {a['Zona']:<6} | {a['PM2.5']:<8} | {a['CO2']:<8}\n"
            testo_file += "-" * 70 + "\n"
            testo_file += f"Totale anomalie: {len(allarmi_trovati)}\n"
            
            st.download_button("Scarica Registro Allarmi (.txt)", data = testo_file, file_name = "registro_allarmi.txt", mime = "text/plain")
        else:
            st.success("Nessun superamento delle soglie rilevato. Valori nella norma.")

    # PAGINA 3 - GRAFICI  
    elif pagina == "Analisi Grafica":
        st.header("Analisi Visiva Aria", anchor=False)
        date_ore = [f"{r[0][5:]} {r[1]}" for r in dati] 
        valori_pm = [r[3] for r in dati]
        
        colore_testo = 'white' if tema_grafici == "Chiari (Dark Mode)" else 'black'
        plt.rcParams.update({'text.color': colore_testo, 'axes.labelcolor': colore_testo, 
                             'xtick.color': colore_testo, 'ytick.color': colore_testo})

        tab1, tab2, tab3 = st.tabs(["Grafico Multi-Panel", "HeatMap", "Planimetria"])

        with tab1:
            st.info("Grafico multi-panel per il monitoraggio simultaneo dei 4 parametri ambientali.")
            
            fig1, axs = plt.subplots(2, 2, figsize=(14, 8))
            fig1.patch.set_alpha(0)
            
            y_pm = [r[3] for r in dati]
            y_co2 = [r[4] for r in dati]
            y_temp = [r[5] for r in dati]
            y_umid = [r[6] for r in dati]
        
            axs[0, 0].plot(y_pm, color = '#E74C3C', marker = '.', linewidth = 1)
            axs[0, 0].set_title("Andamento PM2.5 (µg/m³)", fontweight = 'bold', color = colore_testo)
            axs[0, 0].axhline(y = st.session_state.get("soglia_pm", 25.0), color='red', linestyle = '--', alpha = 0.5)
            
            axs[0, 1].plot(y_co2, color = '#8E44AD', marker = '.', linewidth = 1)
            axs[0, 1].set_title("Andamento CO2 (ppm)", fontweight='bold', color=colore_testo)
            axs[0, 1].axhline(y = st.session_state.get("soglia_co2", 1000), color = 'red', linestyle = '--', alpha = 0.5)
            
            axs[1, 0].plot(y_temp, color = '#F39C12', marker = '.', linewidth = 1)
            axs[1, 0].set_title("Andamento Temperatura (°C)", fontweight = 'bold', color = colore_testo)
            
            axs[1, 1].plot(y_umid, color = '#3498DB', marker = '.', linewidth = 1)
            axs[1, 1].set_title("Andamento Umidità (%)", fontweight = 'bold', color = colore_testo)

            etichette_temporali = [f"{r[0][-2:]}-{r[0][5:7]} {r[1]}" for r in dati]
            
            passo = max(1, len(dati) // 10) 
            
            for ax in axs.flat:
                ax.patch.set_alpha(0)

                for spine in ax.spines.values(): spine.set_visible(False)
                
                ax.tick_params(axis = 'x', rotation = 45, colors = colore_testo)
                ax.tick_params(axis = 'y', colors = colore_testo)
                ax.grid(True, linestyle = '--', alpha = 0.15, color = colore_testo)
                
                ax.set_xticks(range(0, len(dati), passo))
                ax.set_xticklabels([etichette_temporali[i] for i in range(0, len(dati), passo)])

            plt.tight_layout()
            st.pyplot(fig1, transparent=True)

        with tab2:
            st.info("Mappa di calore dinamica per individuare i picchi ambientali.")
            
            parametro_scelto = st.selectbox("Seleziona il parametro da analizzare:", 
                                            ["PM2.5 (µg/m³)", "CO2 (ppm)", "Temperatura (°C)", "Umidità (%)"])
            
            if "PM2.5" in parametro_scelto:
                valori_heatmap = [r[3] for r in dati]
                mappa_colori = 'Reds'
            elif "CO2" in parametro_scelto:
                valori_heatmap = [r[4] for r in dati]
                mappa_colori = 'Purples'
            elif "Temperatura" in parametro_scelto:
                valori_heatmap = [r[5] for r in dati]
                mappa_colori = 'Oranges'
            else:
                valori_heatmap = [r[6] for r in dati]
                mappa_colori = 'Blues'

            fig2, ax1 = plt.subplots(figsize=(10, 5))
            fig2.patch.set_alpha(0)
            ax1.patch.set_alpha(0)
            for spine in ax1.spines.values(): spine.set_visible(False)
            
            asse_y = [zone_uniche.index(z) for z in zone_estratte]
            
            mappa = ax1.scatter(date_ore, asse_y, c = valori_heatmap, cmap = mappa_colori, s = 250, edgecolors = 'gray', linewidth = 1)
            
            cbar = plt.colorbar(mappa)
            cbar.set_label(parametro_scelto) 
            cbar.outline.set_visible(False)
            cbar.ax.yaxis.set_tick_params(color=colore_testo)
            
            plt.yticks(range(len(zone_uniche)), zone_uniche)
            plt.xticks(rotation = 45)
            
            nome_breve = parametro_scelto.split(' ')[0]
            ax1.set_title(f"HeatMap: Criticità {nome_breve} per Area", fontweight = 'bold', color = colore_testo)
            
            plt.grid(True, linestyle = '--', alpha = 0.15, color = colore_testo)
            plt.tight_layout()
            
            st.pyplot(fig2, transparent = True)

        with tab3:
            st.info("Mappa del Capannone Industriale")

            s_pm = st.session_state.get("soglia_pm", 25.0)
            s_co2 = st.session_state.get("soglia_co2", 1000)
            
            ora_reale = datetime.now()

            ultimi_dati = {}
            for z in zone_uniche:
                dati_zona = [r for r in dati if r[2] == z]
    
                if dati_zona:
                    record_piu_vicino = min(
                        dati_zona,
                        key=lambda r: abs(ora_reale - datetime.strptime(f"{r[0]} {r[1]}", "%Y-%m-%d %H:%M"))
                    )
                    ultimi_dati[z] = record_piu_vicino 

            c_mappa, c_isp = st.columns([1.5, 1])

            with c_mappa:
                fig_p, ax_p = plt.subplots(figsize=(11, 6))
                fig_p.patch.set_alpha(0)
                ax_p.patch.set_alpha(0)
                
                for spine in ax_p.spines.values():
                    spine.set_visible(False)

                ax_p.plot([0, 80], [60, 60], color = colore_testo, linewidth = 3, alpha = 0.6)    
                ax_p.plot([80, 80], [40, 60], color = colore_testo, linewidth = 3, alpha = 0.6)   
                ax_p.plot([80, 130], [40, 40], color = colore_testo, linewidth = 3, alpha = 0.6)  
                ax_p.plot([130, 130], [0, 40], color = colore_testo, linewidth = 3, alpha = 0.6)  
                ax_p.plot([60, 130], [0, 0], color = colore_testo, linewidth = 3, alpha = 0.6)    
                ax_p.plot([60, 60], [0, 20], color = colore_testo, linewidth = 3, alpha = 0.6)    
                ax_p.plot([0, 80], [20, 20], color = colore_testo, linewidth = 3, alpha = 0.6)    
                
                ax_p.plot([0, 0], [20, 35], color = colore_testo, linewidth = 3, alpha = 0.6)     
                ax_p.plot([0, 0], [45, 60], color = colore_testo, linewidth = 3, alpha = 0.6)    

                ax_p.plot([40, 40], [20, 33], color = colore_testo, linewidth = 2, linestyle = '--')
                ax_p.plot([40, 40], [47, 60], color = colore_testo, linewidth = 2, linestyle = '--')
                
                ax_p.plot([80, 80], [21, 26], color = colore_testo, linewidth = 2, linestyle = '--')
                ax_p.plot([80, 80], [34, 40], color = colore_testo, linewidth = 2, linestyle = '--')
                
                coords_sensori = {'Zona A': (20, 40), 'Zona B': (60, 42), 'Zona C': (95, 20)}
                etichette_aree = {'Zona A': 'AREA PRODUZIONE (A)', 'Zona B': 'ASSEMBLAGGIO (B)', 'Zona C': 'LOGISTICA (C)'}

                for zona, coords in coords_sensori.items():
                    if zona in ultimi_dati:
                        val_pm = ultimi_dati[zona][3]
                        val_co2 = ultimi_dati[zona][4] 
                        
                        if val_pm > s_pm or val_co2 > s_co2:
                            col_allarme = '#E74C3C' 
                        elif val_pm > (s_pm * 0.7) or val_co2 > (s_co2 * 0.8):
                            col_allarme = '#F39C12' 
                        else:
                            col_allarme = '#2ECC71' 

                        ax_p.scatter(coords[0], coords[1], s = 1800, color=col_allarme, alpha = 0.15, zorder = 1)
                        ax_p.scatter(coords[0], coords[1], s = 500, color=col_allarme, edgecolors=colore_testo, linewidth=2, zorder=3)
                        
                        ax_p.text(coords[0], coords[1], "SENSORE", color='white', fontsize = 8, ha = 'center', va = 'center', fontweight = 'bold', zorder = 10)
                        ax_p.text(coords[0], coords[1]+10, etichette_aree[zona], color = colore_testo, fontsize = 9, fontweight = 'bold', ha = 'center', va = 'bottom')

                ax_p.set_xlim(-10, 140)
                ax_p.set_ylim(-10, 70)
                ax_p.set_title("STATO SENSORI", color = colore_testo, fontweight = 'bold')
                ax_p.axis('off')
                st.pyplot(fig_p, transparent = True)

            with c_isp:
                st.subheader("Pannello Ispezione", anchor = False)
                scelta = st.radio("Seleziona zona:", zone_uniche, label_visibility = "collapsed")
                
                if scelta in ultimi_dati:
                    d_z = ultimi_dati[scelta]
                    pm_val, co2_val, temp_val, umid_val = d_z[3], d_z[4], d_z[5], d_z[6]
                    
                    if pm_val > s_pm:
                        stato_pm = "CRITICO"
                        colore_delta_pm = "red" 
                    elif pm_val > (s_pm * 0.7):
                        stato_pm = "PRE-ALLARME"
                        colore_delta_pm = "yellow" 
                    else:
                        stato_pm = "OK"
                        colore_delta_pm = "green" 

                    if co2_val > s_co2:
                        stato_co2 = "CRITICO"
                        colore_delta_co2 = "red"
                    elif co2_val > (s_co2 * 0.8):
                        stato_co2 = "PRE-ALLARME"
                        colore_delta_co2 = "yellow"
                    else:
                        stato_co2 = "OK"
                        colore_delta_co2 = "green"
                    
                    st.metric(label="PM2.5", value = f"{pm_val} µg/m³", delta = stato_pm, delta_color = colore_delta_pm)
                    st.metric(label="CO2", value = f"{co2_val} ppm", delta = stato_co2, delta_color = colore_delta_co2)
                    
                    st.divider()
                    col_met1, col_met2 = st.columns(2)
                    col_met1.metric("Temp", f"{temp_val} °C")
                    col_met2.metric("Umidità", f"{umid_val} %")