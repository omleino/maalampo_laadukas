import streamlit as st
import matplotlib.pyplot as plt

def laske_kustannukset(investointi, omaisuuden_myynti, korko, sahkon_hinta, sahkon_kulutus_kwh,
                        laina_aika, korjaus_vuosi, korjaus_kustannus, sahkon_inflaatio):

    lainan_maara = investointi - omaisuuden_myynti
    lyhennys = lainan_maara / laina_aika
    jaljella_oleva_laina = lainan_maara
    sahkon_hinta_vuosi = sahkon_hinta

    kustannukset = []
    korjaus_laina_jaljella = 0
    korjaus_lyhennys = 0

    for vuosi in range(1, laina_aika + 1):
        korko_vuodelta = jaljella_oleva_laina * (korko / 100)
        sahkolasku = sahkon_hinta_vuosi * sahkon_kulutus_kwh

        # Korjauslaina aktivoituu valittuna vuonna
        if vuosi == korjaus_vuosi:
            korjaus_laina_jaljella = korjaus_kustannus
            vuodet_jaljella = laina_aika - vuosi + 1
            korjaus_lyhennys = korjaus_kustannus / vuodet_jaljella

        korjaus_korko = korjaus_laina_jaljella * (korko / 100) if korjaus_laina_jaljella > 0 else 0

        kokonais = lyhennys + korko_vuodelta + sahkolasku + korjaus_lyhennys + korjaus_korko
        kustannukset.append(kokonais)

        jaljella_oleva_laina -= lyhennys
        if korjaus_laina_jaljella > 0:
            korjaus_laina_jaljella -= korjaus_lyhennys

        sahkon_hinta_vuosi *= (1 + sahkon_inflaatio / 100)

    return kustannukset


# Streamlit-sovellus
def main():
    st.title("Maalämpö vs Kaukolämpö - Laskuri (korjaukset & inflaatio mukana)")

    with st.sidebar:
        st.header("Syötteet")
        investointi = st.number_input("Investoinnin suuruus (€)", value=650000.0)
        omaisuuden_myynti = st.number_input("Omaisuuden myyntitulo (€)", value=100000.0)
        korko = st.number_input("Lainan korko (% / vuosi)", value=3.0)
        sahkon_hinta = st.number_input("Sähkön hinta (€/kWh)", value=0.12)
        sahkon_inflaatio = st.number_input("Sähkön hinnan nousu (% / vuosi)", value=2.0)
        sahkon_kulutus = st.number_input("Maalämmön sähkönkulutus (kWh/vuosi)", value=180000.0)
        kaukolampo_kustannus = st.number_input("Kaukolämmön vuosikustannus (€)", value=85000.0)
        laina_aika = st.slider("Laina-aika (vuotta)", 5, 40, value=20)
        maksavat_neliot = st.number_input("Maksavat neliöt (m²)", value=1000.0)
        korjaus_vuosi = st.slider("Maalämmön korjausvuosi", 1, laina_aika, value=15)
        korjaus_kustannus = st.number_input("Korjauksen hinta (€)", value=20000.0)

    vuodet = list(range(1, laina_aika + 1))
    kaukolampo = [kaukolampo_kustannus] * laina_aika

    maalampo_ilman = laske_kustannukset(investointi, 0, korko, sahkon_hinta, sahkon_kulutus,
                                        laina_aika, korjaus_vuosi, korjaus_kustannus, sahkon_inflaatio)

    maalampo_myynnilla = laske_kustannukset(investointi, omaisuuden_myynti, korko, sahkon_hinta, sahkon_kulutus,
                                            laina_aika, korjaus_vuosi, korjaus_kustannus, sahkon_inflaatio)

    # Ensimmäisen vuoden vastikelaskelma per m²
    lainan_maara = investointi - omaisuuden_myynti
    lyhennys = lainan_maara / laina_aika
    korko_vuosi = lainan_maara * (korko / 100)
    sahko_vuosi = sahkon_hinta * sahkon_kulutus
    kokonais_vuosi = lyhennys + korko_vuosi + sahko_vuosi

    lyh_m2 = lyhennys / maksavat_neliot
    korko_m2 = korko_vuosi / maksavat_neliot
    sahko_m2 = sahko_vuosi / maksavat_neliot
    yhteensa_m2_vuosi = lyh_m2 + korko_m2 + sahko_m2
    yhteensa_m2_kk = yhteensa_m2_vuosi / 12

    kaukolampo_m2 = kaukolampo_kustannus / maksavat_neliot
    kaukolampo_kk = kaukolampo_m2 / 12

    st.subheader("Ensimmäisen vuoden vastikelaskelma per m²")
    st.markdown(f"- **Lyhennys:** {lyh_m2:.2f} €/m²/vuosi")
    st.markdown(f"- **Korko:** {korko_m2:.2f} €/m²/vuosi")
    st.markdown(f"- **Sähkö:** {sahko_m2:.2f} €/m²/vuosi")
    st.markdown(f"**Yhteensä:** {yhteensa_m2_vuosi:.2f} €/m²/v eli {yhteensa_m2_kk:.2f} €/m²/kk")

    st.markdown("---")
    st.markdown(f"**Kaukolämpövastike:** {kaukolampo_m2:.2f} €/m²/v eli {kaukolampo_kk:.2f} €/m²/kk")
    st.markdown(f"**Erotus:** {kaukolampo_m2 - yhteensa_m2_vuosi:.2f} €/m²/v")

    # Kaavio
    fig, ax = plt.subplots()
    ax.plot(vuodet, kaukolampo, label="Kaukolämpö", linestyle="--")
    ax.plot(vuodet, maalampo_ilman, label="Maalämpö (ilman omaisuuden myyntiä)")
    ax.plot(vuodet, maalampo_myynnilla, label="Maalämpö (myynnillä)")
    ax.axvline(korjaus_vuosi, color='red', linestyle=':', label="Korjausvuosi")
    ax.set_title("Lämmityskustannusten kehitys")
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Kustannus (€)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

if __name__ == "__main__":
    main()
