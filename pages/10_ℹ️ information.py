import streamlit as st


st.title('ℹ️ \u2003info ')
st.write('---')
st.markdown('### Application for ***piping class*** definition'  )
st.write('')
st.write('**Scope**')
st.write('This software performs the thickness calculation of several piping groups (max = 4) made up of different materials and diameter ranges under load conditions of internal pressure and temperature. It also let the user to define three component groups in order to give the evaluation of the rating of the piping system.')
#st.write('It is also possible to define three component groups and evaluate the rating of the piping system.')
st.write('Calculations are according to ASME B31.3-2024')         
st.write('' )
st.write('**Program Flow**')

st.write('**Main**: select new or stored project and press ***start*** ... ➡️ **General Data**: input data and tick the checkbox to confirm ... ➡️ **Piping Groups**: define piping groups or change the existing ones...  ➡️ **Component Groups**: define component groups or change the existing ones... ➡️ **Piping thk calculation**: calculate thikness... ➡️ **Rating Evaluation**: Evaluate rating ...    🏁 End of calculation')
st.write('')

st.write('**Other menu voices**')
st.write('**Piping Allowables**: Shows piping material allowables as per ASME B 31.3-2024')
st.write('**Components Rating**: Shows components pressure rating as per ASME B16.34 and B16.5 - 2025')
st.write('**Temperatures**: Shows the temperature table used in the calculations. It is possible to change the values.')
st.write('**Save Project**: You can save the project on your local drive and recall it in a second time.')
st.write('**Units of measurement**: Shows the table of the used units.')

st.markdown('')

st.markdown('')
st.markdown('')
st.info("-- ©️ App developed by ing. Pasquale Aurelio Cirillo - Release 1.0 2025 --")

#st.markdown('<p style="color:red;">ℹ️ Questo è un messaggio di informazione in rosso</p>', unsafe_allow_html=True)
