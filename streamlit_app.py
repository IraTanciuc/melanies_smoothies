# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customise Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# add name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
# create a dataframe with fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowpark Dataframe to a Pandas df, so we can use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# get the search_on value
search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

# Create a dropdown with fruit names allowing max 5 selections
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections = 5
)

# add a submit button
time_to_insert = st.button('Submit Order')

# if there's fruits selected, add them all to ingredients_string
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # display fruityvice nutrition information
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # create an insert statment with the fruits and name on order
    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

# if someone clicked on the submit button, execute the insert sql statement and display a success message
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
