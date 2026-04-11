# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title
st.title(":cup_with_straw: Customize your smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")

# User input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas
pd_df = my_dataframe.to_pandas()

# Multiselect dropdown
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

# If user selected ingredients
if ingredients_list:

    # Create comma-separated string
    ingredients_string = ','.join(ingredients_list)

    # Loop through selected fruits
    for fruit_chosen in ingredients_list:

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.write('The search value for', fruit_chosen, 'is', search_on)

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API call
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

    # ✅ Submit button OUTSIDE loop
    if st.button('Submit Order'):

        if name_on_order:  # basic validation

            # Prevent SQL breaking from quotes
            safe_name = name_on_order.replace("'", "''")

            insert_sql = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{safe_name}')
            """

            session.sql(insert_sql).collect()

            st.success('Your Smoothie is ordered!', icon="✅")

        else:
            st.warning("Please enter a name before submitting.")
