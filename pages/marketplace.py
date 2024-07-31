import time
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

from backend.send_mail import MailUtils
from backend.database import (
    ProductsDB,
    WishlistDB,
    RatingsDB,
    CartDB,
    OrdersDB,
    UserDB,
    NotificationsDB,
)


st.set_page_config(
    page_title="WingIt: Marketplace",
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


@st.experimental_dialog("Purchase Details")
def display_purchase_details(
    order_id, product_id, quantity, total_amount, ordered_on, status, delivered_to
):
    st.markdown(
        f"Order placed on {ordered_on}",
        unsafe_allow_html=True,
    )

    all_products_price = []

    for i in range(len(product_id)):
        productsdb = ProductsDB()
        product = productsdb.get_product(product_id[i])

        cola, colb, colc = st.columns([0.75, 3.25, 1.5])
        with cola:
            st.image(
                Image.open(product[7]).resize((500, 500)),
                use_column_width=True,
            )

        with colb:
            total_item_price = product[5] * quantity[i]
            st.markdown(
                f"<B>{product[1]}</B><BR><B>Quantity:</B> {quantity[i]} (Price: {total_item_price})",
                unsafe_allow_html=True,
            )
            all_products_price.append(total_item_price)

        with colc:
            button_wishlist = st.button(
                "🧡 Wishlist", use_container_width=True, key=f"_remove_from_cart_{i}"
            )

        if button_wishlist:
            wishlistdb = WishlistDB()
            wishlistdb.add_wishlist_item(logged_in_username, product_id[i])

            st.success("Product added to your wishlist", icon="✔️")
            time.sleep(2)
            st.rerun()

    sac.divider(align="center", color="dark")

    if sum(all_products_price) > 499:
        st.markdown(
            f"<B>Delivery to:</B> {delivered_to}<BR><BR><B>Total Amount:</B> Rs {total_amount} (This order is eligible for free delivery)",
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            f"<B>Delivery to:</B> {delivered_to}<BR><BR><B>Total Amount:</B> Rs {total_amount} (Price inclusive of Rs 40 Delivery Charge)",
            unsafe_allow_html=True,
        )


@st.experimental_dialog("Your Cart")
def display_wishlist():
    wishlistdb = WishlistDB()
    wishlisted_items = wishlistdb.get_wishlist_by_userid(logged_in_username)

    if len(wishlisted_items) < 1:
        sac.result(
            label="No Products Wishlisted",
            description="Your wishlisted items will be shown here",
            status="empty",
        )

    for item in wishlisted_items:
        cola, colb, colc, cold = st.columns([0.75, 2.5, 1.6, 0.65])

        productsdb = ProductsDB()
        product = productsdb.get_product(item[2])

        with cola:
            st.image(
                Image.open(product[7]).resize((500, 500)),
                use_column_width=True,
            )

        product_name = product[1]
        if len(product_name) > 24:
            product_name = product_name[:22] + "..."

        with colb:
            st.markdown(f"<B>{product_name}</B><BR>{item[3]}", unsafe_allow_html=True)

        with colc:
            st.button(
                "Add to Cart",
                use_container_width=True,
                key=f"_remove_from_cart_{item[0]}",
            )

        with cold:
            button_discard = st.button(
                "❌", use_container_width=True, key=f"_remove_from_wishlist_{item[0]}"
            )

        if button_discard:
            wishlistdb = WishlistDB()
            wishlistdb.remove_product_from_wishlist(product[0], logged_in_username)

            st.success("Item removed from your wishlist", icon="✔️")
            time.sleep(5)
            st.rerun()


@st.experimental_dialog("Your Cart")
def display_cart():
    cartdb = CartDB()
    cart = cartdb.get_cart_from_userid(logged_in_username)

    if len(cart) < 1:
        sac.result(
            label="No Items in Your Cart",
            description="Items added to your cart will appear here",
            status="empty",
        )

    else:
        combined_price_list = []
        cart_productid = []
        cart_quantity = []

        for item in cart:
            productsdb = ProductsDB()
            product = productsdb.get_product(item[2])

            cola, colb, colc = st.columns([0.75, 3.5, 1.25])
            with cola:
                st.image(
                    Image.open(product[7]).resize((500, 500)),
                    use_column_width=True,
                )

            with colb:
                total_item_price = (product[5] - (product[5] * (product[6] / 100))) * item[3]

                st.markdown(
                    f"<B>{product[1]}</B><BR><B>Quantity:</B> {item[3]} (Total Price: {total_item_price})",
                    unsafe_allow_html=True,
                )

                cart_productid.append(item[2])
                cart_quantity.append(item[3])
                combined_price_list.append(int(total_item_price))

            with colc:
                button_remove_item = st.button(
                    "Remove",
                    use_container_width=True,
                    key=f"_remove_from_cart_{item[0]}",
                )

            if button_remove_item:
                cartdb = CartDB()
                cartdb.delete_cart_item(logged_in_username, item[2])

                msg = st.info("Item removed from your cart")
                time.sleep(5)
                st.rerun()

        total_cart_amount = int(sum(combined_price_list))

        address_type = st.selectbox(
            "Select Your Delivery Address",
            ("Deliver to my registered address", "Deliver to a differet address"),
            placeholder="Select Address",
        )

        if address_type == "Deliver to a differet address":
            delivery_address = st.text_area(
                "Enter your delivery address",
                placeholder="Enter your delivery address",
                label_visibility="collapsed",
            )

        if total_cart_amount < 499:
            st.markdown(
                "<B>Delivery Charge: </B> Rs 40 (Free delivery on orders above Rs 499)",
                unsafe_allow_html=True,
            )
            total_cart_amount = total_cart_amount + 40
        else:
            st.markdown(
                "<B>Free Delivery</B> (Orders above Rs 499 are eligible for free delivery)",
                unsafe_allow_html=True,
            )

        cola, colb = st.columns([4.5, 2])
        with cola:
            st.markdown(f"<H1>Rs {total_cart_amount}</H1>", unsafe_allow_html=True)

        with colb:
            st.write(" ")
            button_place_order = st.button(
                "Place Order", use_container_width=True, type="primary"
            )

        if button_place_order:
            if address_type == "Deliver to my registered address":
                userdb = UserDB()
                _, _, _, _, _, _, address_type, _, _, _, _, _, _ = userdb.get_user(
                    logged_in_username
                )

            ordersdb = OrdersDB()
            ordersdb.add_order(
                logged_in_username,
                cart_productid,
                cart_quantity,
                total_cart_amount,
                address_type,
                "pending",
            )

            cartdb = CartDB()
            for product_id in cart_productid:
                cartdb.delete_cart_item(logged_in_username, product_id)

            st.success("Your order has been placed successfully", icon="✔️")
            try:
                notifdb = NotificationsDB()
                message = "Your order has been placed successfully"
                notifdb.add_notification(
                    logged_in_username, datetime.datetime.today().date(), message
                )
            except:
                pass

            time.sleep(5)
            st.rerun()


@st.experimental_dialog("Product Summary")
def display_product_popup(
    product_id,
    product_name,
    product_brand,
    product_price,
    product_offer,
    product_type,
    product_image_url=None,
):
    cola, colb = st.columns([2, 4])
    with cola:
        st.image(
            Image.open(product_image_url).resize((500, 500)),
            use_column_width=True,
        )

    with colb:
        st.markdown(f"<B>{product_name}</B><BR>{product_brand}", unsafe_allow_html=True)

        colx, coly = st.columns([1, 1.1])

        ratingsdb = RatingsDB()
        average_rating, rating_count = ratingsdb.get_product_rating_info(product_id)[0]
        rounded_average_rating = round(average_rating * 2) / 2

        with colx:
            sac.rate(
                half=True, value=rounded_average_rating, align="start", color="yellow"
            )
        with coly:
            st.markdown(f"({rating_count:02} Reviews)", unsafe_allow_html=True)

        st.markdown(
            f"<P style='font-size: 26px;'><B>Rs {int(product_price - (product_price * (product_offer / 100)))}</B> <span style='font-size: 16px;'><S>Rs {int(product_price)}</S></span><span style='font-size: 16px;'> • {product_offer}% off applied</span></P>",
            unsafe_allow_html=True,
        )

    item_quantity = st.number_input(
        "Select Quantity (Max 10)", min_value=1, max_value=10
    )

    cola, colb = st.columns([2, 4])
    with cola:
        button_add_to_cart = st.button("🛍️ Add to Cart", use_container_width=True)
    with colb:
        button_wishlist = st.button("🧡")

    if button_add_to_cart:
        cartdb = CartDB()
        cartdb.add_cart_item(logged_in_username, product_id, item_quantity)

        st.success("Product added to your cart successfully", icon="✔️")
        time.sleep(5)
        st.rerun()

    if button_wishlist:
        wishlistdb = WishlistDB()
        wishlistdb.add_wishlist_item(logged_in_username, product_id)

        st.success("Product added to your wishlist", icon="✔️")
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    logged_in_username = st.session_state.logged_in_username

    with st.sidebar:
        selected_menu_item = sac.menu(
            [
                sac.MenuItem(
                    "WingIt's Marketplace",
                    icon="shop-window",
                ),
                sac.MenuItem(
                    "My Purchase History",
                    icon="clock-history",
                ),
                sac.MenuItem(" ", disabled=True),
                sac.MenuItem(type="divider"),
            ],
            open_all=True,
        )

    if selected_menu_item == "WingIt's Marketplace":
        with st.sidebar:
            with st.container(height=365, border=False):
                with st.expander("🛠️ Apply Filter on Results", expanded=False):
                    filter_container = st.container(border=False)

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
            st.markdown("<H4>WingIt's Marketplace</H4>", unsafe_allow_html=True)

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
                    Image.open("assets/app_graphics/banner_1.png").resize((500, 500)),
                    use_column_width=True,
                )

            with st.container(border=True):
                st.image(
                    Image.open("assets/app_graphics/banner_2.png").resize((500, 500)),
                    use_column_width=True,
                )

        with colb:
            with st.container(border=True):
                st.image(
                    Image.open("assets/app_graphics/banner_master.png").resize(
                        (500, 240)
                    ),
                    use_column_width=True,
                )

        (
            reports_and_plans_ribbon_1,
            reports_and_plans_ribbon_2,
            reports_and_plans_ribbon_3,
        ) = st.columns(3)

        with reports_and_plans_ribbon_1:
            with st.container(border=True):
                cola, colb = st.columns([1, 3])

                with cola:
                    st.image(
                        Image.open("assets/app_graphics/trident_red.png").resize(
                            (50, 50)
                        )
                    )

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">Sanitary Savings</span><BR><span class="custom-font-size-bmi"><B>Min. 15% Off Essentials</span></B>',
                        unsafe_allow_html=True,
                    )

        with reports_and_plans_ribbon_2:
            with st.container(border=True):
                cola, colb = st.columns([1, 3])

                with cola:
                    st.image(
                        Image.open("assets/app_graphics/trident_yellow.png").resize(
                            (50, 50)
                        )
                    )

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">Bio Week is Live</span><BR><span class="custom-font-size-bmi"><B>Save Big on Bio Products</span></B>',
                        unsafe_allow_html=True,
                    )

        with reports_and_plans_ribbon_3:
            with st.container(border=True):
                cola, colb = st.columns([1, 3])

                with cola:
                    st.image(
                        Image.open("assets/app_graphics/trident_green.png").resize(
                            (50, 50)
                        )
                    )

                with colb:
                    st.markdown(
                        '<span class="custom-h6-bmi">Free Delivery</span><BR><span class="custom-font-size-bmi"><B>Only on orders above 499 </span></B>',
                        unsafe_allow_html=True,
                    )

        products_listing = st.container(border=False)
        products_per_page = 12

        with filter_container:
            selected_filters = sac.checkbox(
                items=[
                    "Products Under Rs.500",
                    "Sanitary Products",
                    "Minimum 15% Discount",
                    "Reusable Material",
                    "Budget Friendly Items",
                ],
            )

        productsdb = ProductsDB()
        total_products = productsdb.get_number_of_products(selected_filters)

        st.write(" ")
        current_page_number = sac.pagination(
            total=total_products,
            page_size=products_per_page,
            align="center",
            variant="light",
            jump=True,
            show_total=True,
        )

        with products_listing:
            products = productsdb.get_products_for_given_range(
                current_page_number, products_per_page, selected_filters
            )

            if len(products) < 1:
                st.markdown("<BR>" * 2, unsafe_allow_html=True)
                sac.result(
                    label="No Products Available",
                    description="We couldn't find any products matching your selected filters",
                    status="empty",
                )

            top_row = st.container(border=False)
            cola, colb, colc, cold = st.columns(4)

            try:
                product_0 = products[0]
                with cola:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_0[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_0[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_0[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        with top_row:
                            st.markdown(
                                "<H4>Most Popular Picks</H4>", unsafe_allow_html=True
                            )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_0[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_0[0],
                                    product_0[1],
                                    product_0[2],
                                    int(product_0[5]),
                                    int(product_0[6]),
                                    product_0[4],
                                    product_0[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_1 = products[1]
                with colb:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_1[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_1[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_1[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_1[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_1[0],
                                    product_1[1],
                                    product_1[2],
                                    int(product_1[5]),
                                    int(product_1[6]),
                                    product_1[4],
                                    product_1[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_2 = products[2]
                with colc:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_2[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_2[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_2[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_2[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_2[0],
                                    product_2[1],
                                    product_2[2],
                                    int(product_2[5]),
                                    int(product_2[6]),
                                    product_2[4],
                                    product_2[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_3 = products[3]
                with cold:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_3[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_3[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_3[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_3[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_3[0],
                                    product_3[1],
                                    product_3[2],
                                    int(product_3[5]),
                                    int(product_3[6]),
                                    product_3[4],
                                    product_3[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            mid_row = st.container(border=False)
            cola, colb, colc, cold = st.columns(4)

            try:
                product_4 = products[4]
                with cola:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_4[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_4[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_4[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        with mid_row:
                            st.markdown(
                                "<H4>Deals of the Day</H4>", unsafe_allow_html=True
                            )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_4[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_4[0],
                                    product_4[1],
                                    product_4[2],
                                    int(product_4[5]),
                                    int(product_4[6]),
                                    product_4[4],
                                    product_4[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_5 = products[5]
                with colb:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_5[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_5[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_5[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_5[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_5[0],
                                    product_5[1],
                                    product_5[2],
                                    int(product_5[5]),
                                    int(product_5[6]),
                                    product_5[4],
                                    product_5[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_6 = products[6]
                with colc:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_6[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_6[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_6[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_6[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_6[0],
                                    product_6[1],
                                    product_6[2],
                                    int(product_6[5]),
                                    int(product_6[6]),
                                    product_6[4],
                                    product_6[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_7 = products[7]
                with cold:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_7[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_7[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_7[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_7[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_7[0],
                                    product_7[1],
                                    product_7[2],
                                    int(product_7[5]),
                                    int(product_7[6]),
                                    product_7[4],
                                    product_7[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            bottom_row = st.container(border=False)
            cola, colb, colc, cold = st.columns(4)

            try:
                product_8 = products[8]
                with cola:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_8[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_8[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_8[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        with bottom_row:
                            st.markdown(
                                "<H4>Items You Can't Miss</H4>", unsafe_allow_html=True
                            )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_8[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_8[0],
                                    product_8[1],
                                    product_8[2],
                                    int(product_8[5]),
                                    int(product_8[6]),
                                    product_8[4],
                                    product_4[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_9 = products[9]
                with colb:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_9[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_9[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_9[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_9[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_9[0],
                                    product_9[1],
                                    product_9[2],
                                    int(product_9[5]),
                                    int(product_9[6]),
                                    product_9[4],
                                    product_9[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_10 = products[10]
                with colc:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_10[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_10[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_10[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_10[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_10[0],
                                    product_10[1],
                                    product_10[2],
                                    int(product_10[5]),
                                    int(product_10[6]),
                                    product_10[4],
                                    product_10[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

            try:
                product_11 = products[11]
                with cold:
                    with st.container(border=True):
                        st.image(
                            Image.open(product_11[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                        product_name = product_11[1]
                        if len(product_name) > 23:
                            product_name = product_name[:21] + "..."

                        product_description = product_11[3]
                        if len(product_description) > 25:
                            product_description = product_description[:22] + "..."

                        st.markdown(
                            f"<B>{product_name}</B><BR>{product_description}",
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "Add to Cart",
                            use_container_width=True,
                            key=f"_add_to_cart_{product_11[0]}",
                        ):
                            try:
                                display_product_popup(
                                    product_11[0],
                                    product_11[1],
                                    product_11[2],
                                    int(product_11[5]),
                                    int(product_11[6]),
                                    product_11[4],
                                    product_11[7],
                                )
                            except Exception as error:
                                st.toast(error)

            except Exception as error:
                pass

    elif selected_menu_item == "My Purchase History":
        with st.sidebar:
            with st.container(height=365, border=False):
                with st.expander("🚨 Get Help with Orders", expanded=False):
                    try:
                        ordersdb = OrdersDB()
                        placed_orderids = ordersdb.get_orderid_for_userid(
                            logged_in_username
                        )[:]

                        orderid = st.selectbox(
                            "Order Id:",
                            placed_orderids,
                            placeholder="Select Order Id",
                            index=None,
                            label_visibility="collapsed",
                        )
                        query = st.text_area(
                            "Write your query",
                            placeholder="Enter your query, and we'll respond back within an hour",
                            label_visibility="collapsed",
                        )

                        if st.button(
                            "📧 Send Request", use_container_width=True, disabled=not (query)
                        ):
                            try:
                                if orderid is None:
                                    orderid = "General Ticket"

                                mail_utils = MailUtils()
                                mail_utils.get_help_with_orders(
                                    logged_in_username, orderid, query
                                )

                                success_msg = st.success("Request registered", icon="✔️")
                                st.toast("Our support team will soon reach out to you.")

                                time.sleep(2)
                                success_msg.empty()

                            except Exception as err:
                                st.toast(err)
                                st.warning("Unable to register your request", icon="⚠️")

                    except Exception as err: pass

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
            st.markdown("<H4>My Purchase History</H4>", unsafe_allow_html=True)

        with ribbon_col_2:
            if st.button("🛍️ Your Cart", use_container_width=True):
                display_cart()

        with ribbon_col_3:
            if st.button("🧡", use_container_width=True):
                display_wishlist()
        st.write(" ")

        ordersdb = OrdersDB()
        placed_orders = ordersdb.get_order_for_userid(logged_in_username)

        if len(placed_orders) < 1:
            st.markdown("<BR>" * 2, unsafe_allow_html=True)
            sac.result(
                label="No Orders Placed",
                description="Orders placed by you will be shown here",
                status="empty",
            )

        else:
            for order in placed_orders:
                with st.container(border=True):
                    cola, colb, colc = st.columns([0.95, 3.8, 1])

                    product_id_per_product = [
                        int(prod_id) for prod_id in order[2].split(",")
                    ]

                    productsdb = ProductsDB()
                    product = productsdb.get_product(product_id_per_product[0])

                    with cola:
                        st.image(
                            Image.open(product[7]).resize((500, 500)),
                            use_column_width=True,
                        )

                    quantity_per_product = [
                        int(item_quantity) for item_quantity in order[3].split(",")
                    ]

                    with colb:
                        st.markdown(
                            f'<span class="custom-h6-bmi">Order Id: {order[0]} • Status: {order[8].title()}</span><BR><span class="custom-font-size-bmi"><B>Delivered {int(sum(quantity_per_product)):02} items to @{order[1]}</span></B><BR><BR>Order placed on {order[7]}<BR>Delivery to: {order[5][:55]}...',
                            unsafe_allow_html=True,
                        )

                    with colc:
                        st.write(" ")
                        st.markdown("<BR>" * 2, unsafe_allow_html=True)

                        if st.button(
                            "View Details",
                            use_container_width=True,
                            type="primary",
                            key=f"_view_details_{order[0]}",
                        ):
                            display_purchase_details(
                                order[0],
                                product_id_per_product,
                                quantity_per_product,
                                order[4],
                                order[7],
                                order[8],
                                order[5],
                            )
