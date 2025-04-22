import streamlit as st
import matplotlib.pyplot as plt

def laske_kustannukset_50v(investointi, omaisuuden_myynti, investointi_laina_aika, korko,
                            sahkon_hinta, sahkon_kulutus_kwh,
                            korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio):

    vuodet = 50
    lainan_maara = investointi - omaisuuden_myynti
    lyhennys = lainan_maara / investointi_laina_aika
    jaljella_oleva_laina = lainan_maara
    sahkon_hinta_vuosi = sahkon_hinta

    kustannukset = []
    korjauslainat = []

    for vuosi in range(1, vuodet + 1):
        # Investointilaina
        if vuosi <= investointi_laina_aika:
            lyh = lyhennys
            korko_investointi = jaljella_oleva_laina * (korko / 100)
            jaljella_oleva_laina -= lyh
        else:
            lyh = 0
            korko_investointi = 0

        sahkolasku = sahkon_hinta_vuosi * sahkon_kulutus_kwh

        # Uusi korjauslaina
        if vuosi > 1 and (vuosi - 1) % korjaus_vali == 0:
            uusi_korjaus = {
                "jaljella": korjaus_hinta,
                "lyhennys": korjaus_hinta / korjaus_laina_aika,
                "vuosia_jaljella": korjaus_laina_aika
            }
            korjauslainat.append(uusi_korjaus)

        # Korjauslainojen kustannukset
        korjaus_korko_yht = 0
        korjaus_lyhennys_yht = 0
        for laina in korjauslainat:
            if laina["vuosia_jaljella"] > 0:
                korko_tama = laina["jaljella"] * (korko / 100)
                korjaus_korko_yht += korko_tama
                korjaus_lyhennys_yht += laina["lyhennys"]
                laina["jaljella"] -= laina["lyhennys"]
                laina["vuosia_jaljella"] -= 1

        # Poista maksetut korjauslainat
        korjauslainat = [laina for laina in korjauslainat if laina["vuosia_jaljella"] > 0]

        # Vuoden kokonaiskustannus
        kokonais = lyh + korko_investointi + sahkolasku + korjaus_lyhennys_yht + korjaus_korko_yht
        kustannukset.append(kokonais)

        sahkon_hinta_vuosi *= (1 + sahkon_inflaatio / 100)

    return kustannukset

def laske_kaukolampo_kustannukset(kustannus, inflaatio):
    nykyinen = kustannus
    tulos = []
    for _ in range(50):
        tulos.append(nykyinen)
        nykyinen *= (1 + inflaatio / 100)
    return tulos

def main():
    st.title("Maalämpö vs Kaukolämpö – 50 vuoden vertailu (kaikki vaihtoehdot)")

    with st.sidebar:
        st.header("Perustiedot")
        investointi = st.number_input("Investoinnin suuruus (€)", value=650000.0)
        omaisuuden_myynti = st.number_input("Omaisuuden myyntitulo (€)", value=100000.0)
        investointi_laina_aika = st.slider("Investointilainan maksuaika (vuotta)", 5, 40, value=20)
        korko = st.number_input("Lainan korko (% / vuosi)", value=3.0)
        sahkon_hinta = st.number_input("Sähkön hinta (€/kWh)", value=0.12)
        sahkon_inflaatio = st.number_input("Sähkön hinnan nousu (% / vuosi)", value=2.0)
        sahkon_kulutus = st.number_input("Maalämmön sähkönkulutus (kWh/v)", value=180000.0)
        kaukolampo_kustannus = st.number_input("Kaukolämmön vuosikustannus (€)", value=85000.0)
        kaukolampo_inflaatio = st.number_input("Kaukolämmön hinnan nousu (% / vuosi)", value=2.0)
        menetetty_kassavirta_kk = st.number_input("Menetetyn omaisuuden kassavirta (€ / kk)", value=0.0)
        maksavat_neliot = st.number_input("Maksavat neliöt (m²)", value=1000.0)

        st.header("Korjaukset")
        korjaus_vali = st.slider("Korjausväli (vuotta)", 5, 30, value=15)
        korjaus_hinta = st.number_input("Yksittäisen korjauksen hinta (€)", value=20000.0)
        korjaus_laina_aika = st.slider("Korjauslainan maksuaika (vuotta)", 1, 30, value=10)

    vuodet = list(range(1, 51))

    kaukolampo = laske_kaukolampo_kustannukset(kaukolampo_kustannus, kaukolampo_inflaatio)

    maalampo_ilman = laske_kustannukset_50v(
        investointi, 0, investointi_laina_aika, korko,
        sahkon_hinta, sahkon_kulutus,
        korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio
    )

    maalampo_myynnilla = laske_kustannukset_50v(
        investointi, omaisuuden_myynti, investointi_laina_aika, korko,
        sahkon_hinta, sahkon_kulutus,
        korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio
    )

    # Menetetty kassavirta
    kassavirta_vuosi = menetetty_kassavirta_kk * 12
    kassavirrat = [kassavirta_vuosi] * 50
    maalampo_myynnilla = [m + k for m, k in zip(maalampo_myynnilla, kassavirrat)]

    # Kaavio
    fig, ax = plt.subplots()
    ax.plot(vuodet, kaukolampo, label="Kaukolämpö", linestyle="--")
    ax.plot(vuodet, maalampo_ilman, label="Maalämpö (ilman myyntiä)")
    ax.plot(vuodet, maalampo_myynnilla, label="Maalämpö (myynnillä + kassavirta)")
    ax.set_title("Lämmityskustannukset 50 vuoden ajalla")
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Kustannus (€)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Vastikevertailu
    st.markdown("### Ensimmäisen vuoden vastikevertailu per m²")

    def laske_vastike(kustannus_lista, neliot):
        vuosikustannus = kustannus_lista[0]
        per_m2_vuosi = vuosikustannus / neliot
        per_m2_kk = per_m2_vuosi / 12
        return per_m2_vuosi, per_m2_kk

    kaukolampo_vuosi, kaukolampo_kk = laske_vastike(kaukolampo, maksavat_neliot)
    maalampo_ilman_vuosi, maalampo_ilman_kk = laske_vastike(maalampo_ilman, maksavat_neliot)
    maalampo_myynnilla_vuosi, maalampo_myynnilla_kk = laske_vastike(maalampo_myynnilla, maksavat_neliot)

    st.markdown(f"**Kaukolämpö:** {kaukolampo_vuosi:.2f} €/m²/v | {kaukolampo_kk:.2f} €/m²/kk")
    st.markdown(f"**Maalämpö ilman omaisuuden myyntiä:** {maalampo_ilman_vuosi:.2f} €/m²/v | {maalampo_ilman_kk:.2f} €/m²/kk")
    st.markdown(f"**Maalämpö omaisuuden myynnillä:** {maalampo_myynnilla_vuosi:.2f} €/m²/v | {maalampo_myynnilla_kk:.2f} €/m²/kk")

    st.markdown("---")
    st.markdown(f"**Erotus (kaukolämpö vs ilman myyntiä): {kaukolampo_vuosi - maalampo_ilman_vuosi:.2f} €/m²/v**")
    st.markdown(f"**Erotus (kaukolämpö vs myynnillä): {kaukolampo_vuosi - maalampo_myynnilla_vuosi:.2f} €/m²/v**")

if __name__ == "__main__":
    main()
