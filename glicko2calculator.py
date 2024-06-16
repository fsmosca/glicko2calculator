"""
glicko2calculator.py

A streamlit web app used to calculate glicko2 rating between two players.

"""

__version__ = '1.4.0'
__author__ = 'fsmosca'
__script_name__ = 'glicko2calculator'
__about__ = 'A streamlit web app used to calculate glicko2 rating between two players.'


import streamlit as st
from glicko2 import Glicko2


APP_NAME = 'Glicko v2 Rating Calculator'
APP_LINK = 'https://github.com/fsmosca/glicko2calculator'


st.set_page_config(
    page_title="Glicko v2 Rating Calculator",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'about': f'[{APP_NAME} v{__version__}]({APP_LINK})'
    }
)


Z_SCORES = {'90%': 1.645, '95%': 1.96, '99%': 2.576}


if 'vola1' not in st.session_state:
    st.session_state.vola1 = 0.06
if 'vola2' not in st.session_state:
    st.session_state.vola2 = 0.06

if 'tau' not in st.session_state:
    st.session_state.tau = 0.5
if 'rating1' not in st.session_state:
    st.session_state.rating1 = 1500
if 'rating2' not in st.session_state:
    st.session_state.rating2 = 1500
if 'rd1' not in st.session_state:
    st.session_state.rd1 = 350
if 'rd2' not in st.session_state:
    st.session_state.rd2 = 350


def data_input(num):
    """Builds widgets."""
    st.markdown(f'''
    ##### Player #{num}
    ''')
    st.number_input(
        label='Rating',
        min_value=500,
        max_value=5000,
        key=f'rating{num}'
    )
    st.number_input(
        label='Rating Deviation',
        min_value=0,
        max_value=1000,
        key=f'rd{num}'
    )
    st.number_input(
        label='Rating Volatility',
        min_value=0.001,
        max_value=1.,
        step=0.00001,
        format="%.8f",
        key=f'vola{num}'
    )


def rating_update(p, num, confidence_level):
    """Shows rating calculation results."""
    lower_rating = round(p.mu - Z_SCORES[confidence_level]*p.phi)
    upper_rating = round(p.mu + Z_SCORES[confidence_level]*p.phi)

    st.markdown(f'''
    ##### New Rating: :green[{round(p.mu)}]
    New RD: **{round(p.phi)}**  
    New Volatility: **{round(p.sigma, 8)}**  
    Gain: **{round(p.mu - st.session_state[f'rating{num}'], 2):+0.2f}**  
    Rating Interval: **[{lower_rating}, {upper_rating}]**
    ''')


def main():
    """App main entry point."""
    st.header('Glicko v2 Rating Calculator')

    calculation_tab, setting_tab, credits_tab = st.tabs(
        [':chart: CALCULATION', ':hammer_and_wrench: SETTING', ':heavy_dollar_sign: CREDITS'])

    with setting_tab:
        st.slider(
            label='Input TAU',
            min_value=0.1,
            max_value=3.0,
            key='tau',
            help='''Smaller values prevent the volatility measures
            from changing by large amounts which in turn prevents enormous
            changes in ratings based on very imporbable results'''
        )

        confidence_level = st.selectbox(
            'Confidence Level',
            options=['90%', '95%', '99%'],
            index=1,
            key='confidence_level_k'
        )

    with calculation_tab:
        col1, col2 = st.columns(2)
        with col1:
            data_input(1)
        with col2:
            data_input(2)

        result = st.selectbox(
            label=':triangular_flag_on_post: Select result',
            options=['#1 wins', '#2 wins', 'draw'],
        )

        env = Glicko2(tau=float(st.session_state.tau))
        r1 = env.create_rating(
            st.session_state.rating1,
            st.session_state.rd1,
            st.session_state.vola1
        )
        r2 = env.create_rating(
            st.session_state.rating2,
            st.session_state.rd2,
            st.session_state.vola2
        )

        p = [None, None]
        if result == '#1 wins':
            p[0], p[1] = env.rate_1vs1(r1, r2, drawn=False)
        elif result == '#2 wins':
            p[1], p[0] = env.rate_1vs1(r2, r1, drawn=False)
        else:
            p[0], p[1] = env.rate_1vs1(r1, r2, drawn=True)

        for i, col in enumerate(st.columns(len(p))):
            with col:
                rating_update(p[i], i+1, confidence_level)

        with st.expander('**Definitions**', expanded=False):
            st.markdown('''**Volatility**<br>
The volatility measure indicates the degree of expected fluctuation in a player's
rating. The volatility measure is high when a player has erratic performances (e.g., when
the player has had exceptionally strong results after a period of stability), and the volatility
measure is low when the player performs at a consistent level.

**Rating deviation**<br>
RD is a numerical value that represents the confidence level in a player's rating. A lower RD indicates higher confidence in the rating, meaning the rating is more accurate.
A higher RD indicates less confidence in the rating, meaning the rating is more volatile or uncertain.
                        ''', unsafe_allow_html=True)

    with credits_tab:
        st.markdown('''
        [Mark Glickman](http://www.glicko.net/glicko.html)<br>
        [Sublee Glicko2 Library](https://github.com/sublee/glicko2)<br>
        [Streamlit](https://streamlit.io/)
        ''', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
