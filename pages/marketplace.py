import time
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

st.set_page_config(
    page_title="Flo: Marketplace",
    page_icon="assets/favicon/flo_favicon.png",
    initial_sidebar_state="expanded",
    layout="wide",
)

st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 1.75rem;
                    padding-bottom: 1rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)


@st.experimental_dialog("Your Cart")
def display_wishlist():
    # Display the items in cart
    for i in [1, 2, 3]:
        cola, colb, colc, cold = st.columns([0.75, 2.5, 1.4, 0.5])
        with cola:
            st.image(
                Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                use_column_width=True,
            )
        
        with colb:
            st.markdown("<B>Secure XL Sanitary Pad(Pa...</B><BR>Saved on: January 31, 2024", unsafe_allow_html=True)
        
        with colc:
            st.button("Add to Cart", use_container_width=True, key=f"_remove_from_cart_{i}")
        
        with cold:
            st.button("❌", use_container_width=True, key=f"_remove_from_wishlist_{i}")


@st.experimental_dialog("Your Cart")
def display_cart():
    # Display the items in cart
    for i in [1, 2, 3]:
        cola, colb, colc = st.columns([0.75, 3.5, 1.25])
        with cola:
            st.image(
                Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                use_column_width=True,
            )
        
        with colb:
            st.markdown("<B>Secure XL Sanitary Pad(Pack of 80)</B><BR><B>Qty:</B> 2 (Total Price: 160)", unsafe_allow_html=True)
        
        with colc:
            st.button("Remove", use_container_width=True, key=f"_remove_from_cart_{i}")

    #Select Address
    address_type = st.selectbox("Select Address", ("This is my saved address", "Enter differet address"), placeholder="Select Address")
    if address_type == "Enter differet address":
        delivery_address = st.text_area("Enter the delivery address", placeholder="Enter the delivery address", label_visibility='collapsed')

    st.markdown("<B>Delivery Charge: </B> Rs 40 (Free delivery on orders above Rs 750)", unsafe_allow_html=True)

    cola, colb = st.columns([4.5, 2])
    with colb:
        st.write(" ")
        st.button("Place Order", use_container_width=True, type="primary")

    with cola:
        st.markdown("<H1>Rs 480</H1>", unsafe_allow_html=True)


@st.experimental_dialog("Product Summary")
def display_product_popup(product_name, product_brand, product_price, product_ratings, product_offer, product_delivered_in_days, product_description, product_image_url=None):
    cola, colb = st.columns([2, 4])
    with cola:
        st.image(
            Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
            use_column_width=True,
        )

    with colb:
        st.markdown("<B>Secure XL Sanitary Pad(Pack of 80)</B><BR>Stayfree", unsafe_allow_html=True)
        
        colx, coly = st.columns([1, 1.1])
        with colx:
            sac.rate(half=True, value=2.0, align='start')
        with coly:
            st.markdown("(24 Reviews)", unsafe_allow_html=True)

        st.markdown("<P style='font-size: 26px;'><B>Rs 500</B> <span style='font-size: 16px;'><S>Rs 400</S></span><span style='font-size: 16px;'> • 20% off applied</span></P>", unsafe_allow_html=True)
    
    st.number_input("Select Quantity (Max 10)", min_value=1, max_value=10)
    
    cola, colb = st.columns([2, 4])
    with cola:
        st.button("🛍️ Add to Cart", use_container_width=True)
    with colb:
        st.button("🧡")

if __name__ == "__main__":
    with st.sidebar:
        selected_menu_item = sac.menu(
            [
                sac.MenuItem(
                    "Flo's Marketplace",
                    icon="grid",
                ),
                sac.MenuItem(
                    "Purchase History",
                    icon="clipboard-pulse",
                ),
                sac.MenuItem(" ", disabled=True),
                sac.MenuItem(type="divider"),
            ],
            open_all=True,
        )

    if selected_menu_item == "Flo's Marketplace":
        with st.sidebar:
            with st.container(height=350, border=False):
                #with st.expander("Get Help with FloAI", expanded=False):
                #    st.text_area("Enter your Query", placeholder="Enter your query", label_visibility="collapsed")
                #    st.button("Ask FloAI", use_container_width=True)

                with st.expander("Apply Filter on Results", expanded=False):
                    sac.checkbox(
                        items=[
                            'Products Under Rs.500',
                            'Sanitary Products',
                            'Minimum 15% Discount',
                            'Reusable Material',
                            'Budget Friendly Items'
                        ],
                    )

            if st.button("Return to Dashboard", use_container_width=True):
                st.switch_page("main.py")

        st.markdown(
            """
            <style>
                .custom-h6-bmi {
                    font-size: 16px; /* Adjust the font size as needed */
                    margin-bottom: 0px;
                    padding: 0px;
                }
                .custom-font-size-bmi {
                    font-size: 16px; /* Adjust the font size as needed */
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Homepage - top ribbon
        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Flo's Marketplace</H4>", unsafe_allow_html=True)
        
        with ribbon_col_2:
            if st.button("🛍️ Your Cart", use_container_width=True):
                display_cart()

        with ribbon_col_3:
            if st.button("🧡", use_container_width=True):
                display_wishlist()

        st.write(" ")
        cola, colb = st.columns([1, 4])

        with cola:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_1.png").resize((500, 500)),
                    use_column_width=True,
                )

            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_3.png").resize((500, 500)),
                    use_column_width=True,
                )
        
        with colb:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 240)),
                    use_column_width=True,
                )

        reports_and_plans_ribbon_1, reports_and_plans_ribbon_2, reports_and_plans_ribbon_3 = st.columns(3)

        with reports_and_plans_ribbon_1:
            with st.container(border=True):
                cola, colb = st.columns([1, 3])

                with cola:
                    st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">An Offer Banner</span><BR><span class="custom-font-size-bmi"><B>Describe brief of the offer</span></B>',
                        unsafe_allow_html=True,
                    )

        with reports_and_plans_ribbon_2:
            with st.container(border=True):
                cola, colb = st.columns([1, 3])

                with cola:
                    st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">An Offer Banner</span><BR><span class="custom-font-size-bmi"><B>Describe brief of the offer</span></B>',
                        unsafe_allow_html=True,
                    )

        with reports_and_plans_ribbon_3:
            with st.container(border=True):
                cola, colb = st.columns([1, 3])

                with cola:
                    st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">An Offer Banner</span><BR><span class="custom-font-size-bmi"><B>Describe brief of the offer</span></B>',
                        unsafe_allow_html=True,
                    )
        
        st.markdown("<H4>Popular Picks</H4>", unsafe_allow_html=True)
        cola, colb, colc, cold = st.columns(4)

        with cola:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_1.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                if st.button("Add to Cart", use_container_width=True, key="_add_to_cart_1_"):
                    display_product_popup(1,1,1,1,1,1,1)
 
        with colb:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_2_")

        with colc:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_3.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_3_")

        with cold:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_4_")

        st.markdown("<H4>Deals of the Day</H4>", unsafe_allow_html=True)
        cola, colb, colc, cold = st.columns(4)

        with cola:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_1.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_1_popular_picks")
        
        with colb:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_2_popular_picks")

        with colc:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_3.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_3_popular_picks")

        with cold:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_4_popular_picks")

        st.markdown("<H4>Deals of the Day</H4>", unsafe_allow_html=True)
        cola, colb, colc, cold = st.columns(4)

        with cola:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_1.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_1_deals_of_the_day")
        
        with colb:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_2_deals_of_the_day")

        with colc:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_3.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_3_deals_of_the_day")

        with cold:
            with st.container(border=True):
                st.image(
                    Image.open("assets/application/blog_banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )
                st.markdown("<B>Product's Name</B><BR>Lorem ipsum dolor mitda", unsafe_allow_html=True)
                st.button("Add to Cart", use_container_width=True, key="_add_to_cart_4_deals_of_the_day")

        st.write(" ")
        sac.pagination(total=60, page_size=12, align='center', variant='light', jump=True, show_total=True)

    elif selected_menu_item == "Purchase History":
        with st.sidebar:
            with st.container(height=350, border=False):
                #with st.expander("Get Help with FloAI", expanded=False):
                #    st.text_area("Enter your Query", placeholder="Enter your query", label_visibility="collapsed")
                #    st.button("Ask FloAI", use_container_width=True)

                with st.expander("Get Help", expanded=False):
                    st.text_area("Write your query", placeholder="Enter your query, and we'll respond back within an hour", label_visibility='collapsed')
                    st.button("Get Help", use_container_width=True)

            if st.button("Return to Dashboard", use_container_width=True):
                st.switch_page("main.py")

        st.markdown(
            """
            <style>
                .custom-h6-bmi {
                    font-size: 16px; /* Adjust the font size as needed */
                    margin-bottom: 0px;
                    padding: 0px;
                }
                .custom-font-size-bmi {
                    font-size: 16px; /* Adjust the font size as needed */
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Purchase History</H4>", unsafe_allow_html=True)
        
        with ribbon_col_2:
            if st.button("🛍️ Your Cart", use_container_width=True):
                display_cart()

        with ribbon_col_3:
            notificatons_button = st.button("🧡", use_container_width=True)
        st.write(" ")

        for order in [0, 1, 2, 3]:
            with st.container(border=True):
                cola, colb, colc = st.columns([0.95, 3.8, 1])
                with cola:
                    st.image(
                        Image.open("assets/application/blog_banner_1.png").resize((500, 500)),
                        use_column_width=True,
                    )

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">An Offer Banner</span><BR><span class="custom-font-size-bmi"><B>Describe brief of the offer</span></B><BR><BR>Delivered on: June 24, 2024<BR>Delivered at: Lorem Ipsum Dolor mit',
                        unsafe_allow_html=True,
                    )

                with colc:
                    st.write(" ")
                    st.markdown("<BR>", unsafe_allow_html=True)

                    st.markdown("<H3 align='right'>Rs 300</H3>", unsafe_allow_html=True)
                    sac.rate(half=True, value=2.0, align='start', key=f'_rate_{order}')
