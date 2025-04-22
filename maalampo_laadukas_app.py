import streamlit as st
import matplotlib.pyplot as plt

def laske_kustannukset_50v(investointi, omaisuuden_myynti, korko, sahkon_hinta, sahkon_kulutus_kwh,
                            korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio):

    vuodet = 50
    lainan_maara = investointi - omaisuuden_myynti
    lyhennys = lainan_maara / 20  # pääasiallisen investointilainan maksuaika = 20 v
    jaljella_oleva_laina = lainan_maara
    sahkon_hinta_vuosi = sahkon_hinta

    kustannukset = []
    korjauslainat = []  # lista aktiivisista korjauslainoista

    for vuosi in range(1, vuodet + 1):
        # alkuperäisen investointilainan lyhennys ja korko (vain 20 vuotta)
        lyh = lyhennys if vuosi <= 20 else 0
        korko_investointi = jaljella_oleva_laina * (korko / 100) if vuosi <= 20 else 0
        jaljella_oleva_laina -= lyh

        sahkolasku = sahkon_hinta_vuosi * sahkon_kulutus_kwh

        # Uusi korjauslaina aloitetaan tietyin välein
        if (vuosi - 1) % korjaus_vali == 0:
            uusi_korjaus = {
                "jaljella": korjaus_hinta,
                "lyhennys": korjaus_hinta / korjaus_laina_aika,
                "vuosia_jaljella": korjaus_laina_aika
            }
            korjauslainat.append(uusi_korjaus)

        # Korjauslainojen vuosikustannus
        korjaus_korko_yht = 0
        korjaus_lyhennys_yht = 0
        for laina in korjauslainat:
            if laina["vuosia_jaljella"] > 0:
                korko_tama = laina["jaljella"] * (korko / 100)
                korjaus_korko_yht += korko_tama
                korjaus_lyhennys_yht += laina["lyhennys"]
                laina["jaljella"] -= laina["lyhennys"]
                laina["vuosia_jaljella"] -= 1

        kokonais = lyh + korko_investointi + sahkolasku + korjaus_lyhennys_yht + korjaus_korko_yht
        kustannukset.append(kokonais)

        sahkon_hinta_vuosi *= (1 + sahkon_inflaatio / 100)

    return kustannukset

# Streamlit-sovellus
def main():
    st.title("Maalämpö vs Kaukolämpö – 50 vuoden malli korjauksilla ja inflaatiolla")

    with st.sidebar:
        st.header("Syötteet")
        investointi = st.number_input("Investoinnin suuruus (€)", value=650000.0)
        omaisuuden_myynti = st.number_input("Omaisuuden myyntitulo (€)", value=100000.0)
        korko = st.number_input("Lainan korko (% / vuosi)", value=3.0)
        sahkon_hinta = st.number_input("Sähkön hinta (€/kWh)", value=0.12)
        sahkon_inflaatio = st.number_input("Sähkön hinnan nousu (% / vuosi)", value=2.0)
        sahkon_kulutus = st.number_input("Maalämmön sähkönkulutus (kWh/v)", value=180000.0)
        kaukolampo_kustannus = st.number_input("Kaukolämmön vuosikustannus (€)", value=85000.0)

        maksavat_neliot = st.number_input("Maksavat neliöt (m²)", value=1000.0)

        st.markdown("### Korjaukset")
        korjaus_vali = st.slider("Korjausväli (vuotta)", 5, 30, value=15)
        korjaus_hinta = st.number_input("Yksittäisen korjauksen hinta (€)", value=20000.0)
        korjaus_laina_aika = st.slider("Korjauslainan maksuaika (vuotta)", 1, 30, value=10)

    # Laskenta
    maalampo = laske_kustannukset_50v(investointi, omaisuuden_myynti, korko, sahkon_hinta, sahkon_kulutus,
                                      korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio)

    kaukolampo = [kaukolampo_kustannus] * 50
    vuodet = list(range(1, 51))

    # Kaavio
    fig, ax = plt.subplots()
    ax.plot(vuodet, kaukolampo, label="Kaukolämpö (vakio)", linestyle="--")
    ax.plot(vuodet, maalampo, label="Maalämpö + korjaukset")
    ax.set_title("Lämmityskustannukset 50 vuoden ajalta")
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Kustannus (€)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

if __name__ == "__main__":
    main()
