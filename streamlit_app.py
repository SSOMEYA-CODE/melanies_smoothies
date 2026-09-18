import streamlit as st
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

st.write("Choose the fruits you want in your custom smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options once and convert to a Python list
@st.cache_data
def get_fruit_options(session):
    df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
    return df.to_pandas()["FRUIT_NAME"].tolist()

fruit_options = get_fruit_options(session)

with st.form("smoothie_order_form", clear_on_submit=True):
    name_on_order = st.text_input("Name on Smoothie:", placeholder="e.g. Alex")
    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        options=fruit_options,
        max_selections=5,
        default=[],
    )

    submitted = st.form_submit_button("Submit Order")

if submitted:
    name_on_order = name_on_order.strip()

    if not name_on_order:
        st.warning("Please enter a name for the smoothie.")
    elif len(ingredients_list) == 0:
        st.warning("Please choose at least one ingredient.")
    else:
        ingredients_string = ", ".join(ingredients_list)

        # Safer insert method
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            [ingredients_string, name_on_order],
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
