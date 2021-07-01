"""
Name: Qiu Ying Zhong
CS230: Section 2
Data: Airbnb
URL: N/A
Description: This program runs a streamlit application to display Airbnb listings in Massachusetts. Users can filter the
listings by neighborhoods, room types and prices. The filtered listings will be showcased in a table. If users filter by
neighborhoods and room types, they can filter the listings by ascending or descending price or most recommended. There
is also a chart to show how many listings are in each neighborhood as well as one to show how many of each room types
there are. The second query includes a map which shows the listings (filtered by neighborhoods the user selects) on a
map based on its latitude and longitude.

"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from PIL import Image
import pydeck as pdk
import mapbox

datafile = "listings.csv"
df = pd.read_csv(datafile)

def getdata(column): #retrieves data from the column
    dfdata = df[f"{column}"]
    return dfdata

#Neighborhood Filter data
def neighborlist (dfdata): #creates list of all the neighborhoods
    location = []
    for neighborhood in dfdata:
        if neighborhood not in location:
            location.append(neighborhood)
    return location

def secondFilter (dfdata, location): #filters listings
    filter = st.sidebar.selectbox(
        "Sort by: ",
        ("Lowest to Highest Price", "Highest to Lowest Price", "Recommended"))
    if filter == "Lowest to Highest Price":
        df_list = df[dfdata == location]
        df_ascending = df_list.sort_values(by=["price"], ascending=[True])
        st.write(df_ascending)
    elif filter == "Highest to Lowest Price":
        df_list = df[dfdata == location]
        df_descending = df_list.sort_values(by=["price"], ascending=[False])
        st.write(df_descending)
    else:
        df_list = df[dfdata == location]
        df_descending = df_list.sort_values(by=["number_of_reviews"], ascending=[False])
        st.write(df_descending)

def barChart(column, list):
    #count # of listings in each neighborhood
    Num = []
    for neighborhood in list:
        dfneighbor = df[df[column] == neighborhood]
        a = len(dfneighbor)
        Num.append(a)

    #creating dictionary
    dict = {}
    count = 0
    for neighbor in list:
        dict[neighbor] = Num[count]
        count += 1

    x = dict.keys()
    y = dict.values()

    #plot chart
    plt.xlabel("Neighbourhoods",fontweight="bold")
    plt.xticks(rotation=90)
    plt.ylabel("Number of Listings", fontweight="bold")
    plt.bar(x, y, color="darkseagreen")
    return plt

#Room Filter Data
def pieChart(column, list): #displays # of each room type
   #count how many of each room types there are
    Num = []
    for room in list:
        dfroom = df[df[column] == room]
        a = len(dfroom)
        Num.append(a)

    #plot chart
    colors = ["darksalmon", "darkseagreen", "thistle", "lightblue"]
    plt.axis("equal")
    plt.pie(Num, explode=None, labels=list, autopct="%1.2f%%", colors=colors)
    return plt

#Price Filter Data
def MaxMinAvgPrices(data): #displays max, min and avg prices of all listings
    if st.sidebar.button("Max Price"):
        maxPrice = data.max()
        st.write(f"The maximum price is ${maxPrice:,.2f}")
    if st.sidebar.button("Min Price"):
        minPrice = data.min()
        st.write(f"The minimum price is ${minPrice:,.2f}")
    if st.sidebar.button("Average Price"):
        avgPrice = data.mean()
        st.write(f"The average price is ${avgPrice:,.2f}")

def PriceFilter(pricerange): #filters for listings in the price range selected
    max = pricerange[0]
    min = pricerange[1]
    dfrange = df[df["price"] <= min]
    dfrange = dfrange[df["price"] >= max]
    st.write(dfrange)

#Maps Data
def read_data(datafile):
    df = pd.read_csv(datafile)

    list= []
    columns = ["name", "neighbourhood", "latitude", "longitude", "price"]

    #retrieves name, neighbourhood, latitude, longitude and price from df
    #each listing is put into a list
    for index, row in df.iterrows():
        sub = []
        for col in columns:
            index_no = df.columns.get_loc(col)
            sub.append(row[index_no])
        list.append(sub)
    return list

#list of all the neighborhoods
def neighbourhoods_list(data):
    neighbourhoods = []

    for i in range(len(data)):
        if data[i][1] not in neighbourhoods:
            neighbourhoods.append(data[i][1])
    return neighbourhoods

#counts how many listings in each neighbourhood
def freq_data(data, neighbourhoods, price):
    freq_dict = {}

    for neighbourhood in neighbourhoods:
        freq = 0
        for i in range(len(data)):
            if data[i][1] == neighbourhood and price >= data[i][4]:
                freq += 1
        freq_dict[neighbourhood] = freq
    return freq_dict

#map function
def display_map(data, neighbourhoods, price):
    loc = []
    for i in range(len(data)):
        if data[i][1] in neighbourhoods and price >= data[i][4]:
            loc.append([data[i][0], data[i][2], data[i][3]])
    map_df = pd.DataFrame(loc, columns=["Listing", "lat", "long"])

    view_state = pdk.ViewState(latitude=map_df["lat"].mean(), longitude=map_df["long"].mean(), zoom=10, pitch=0)
    layer = pdk.Layer("ScatterplotLayer", data=map_df, get_position="[long, lat]",
                      get_radius=50, get_color=[0,255,200], pickable=True)
    tool_tip = {"html":"Listing:<br/>{Listing}", "style": {"backgroundColor": "steelblue", "color":"white"}}

    map = pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                   initial_view_state=view_state, layers=[layer], tooltip=tool_tip)
    st.pydeck_chart(map)

#main function
def main():
    #image
    img = Image.open("airbnb3.jpg")
    st.image(img, width = 700)

    #title and header
    st.title("Massachusetts Airbnb Listings")

    #Filter selectbox
    st.sidebar.subheader("Filters")
    filter = st.sidebar.selectbox(
        "Filter Option: ",
        ("Home", "Neighbourhood", "Room Type", "Price", "Map"))

    #filter options
    if filter == "Home":
        pass
    if filter == "Neighbourhood":
        data = getdata(filter.lower())
        neighbor_list = neighborlist(data)
        neighborhood_filter = st.sidebar.selectbox("Select neighbourhoods:", neighbor_list)
        if st.sidebar.button("Bar Chart"):
            st.pyplot(barChart("neighbourhood",neighbor_list))
        secondFilter(data,neighborhood_filter)

    if filter == "Room Type":
        data = getdata("room_type")
        st.subheader("Room Types")
        rooms = ["Private room","Shared room", "Entire home/apt", "Hotel room"]
        room = st.sidebar.radio("Select a room type: ", rooms)
        if st.sidebar.button("Pie Chart"):
            st.pyplot(pieChart("room_type", rooms))
        secondFilter(data, room)

    if filter == "Price":
        data = getdata(filter.lower())
        minvalue = float(min(data))
        maxvalue = float(max(data))
        prices = st.slider(
            "Price ranges", minvalue, maxvalue,(0.00, 1000.00))
        st.write("Prices range:", prices)
        PriceFilter(prices)
        MaxMinAvgPrices(data)

    if filter == "Map":
        data = read_data("listings.csv")

        neighbourhoods = st.sidebar.multiselect("Select neighbourhoods", neighbourhoods_list(data))
        data1 = getdata("price")
        minvalue = float(min(data1))
        maxvalue = float(max(data1))
        priceLimit = st.sidebar.slider("Price limit", minvalue, maxvalue, 100.00)

        if len(neighbourhoods) > 0:
            st.write("Map of Listings")
            display_map(data, neighbourhoods, priceLimit)

main()
