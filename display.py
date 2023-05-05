import streamlit as st
import random
import time

def get_random_number(mean, std):
    return round(random.random() * std + mean)

def get_random_color():
    letters = "0123456789ABCDEF"
    color = "#"
    for i in range(6):
        color += letters[random.randint(0, 15)]
    return color

st.title("Random Numbers")

st.write("Number 1: ")
number1 = st.empty()

st.write("Number 2: ")
number2 = st.empty()

while True:
    random_number1 = get_random_number(10, 3)
    random_number2 = get_random_number(240, 30)
    color1 = get_random_color()
    color2 = get_random_color()

    number1.write(f"<span style='color:{color1};'>{random_number1}</span>", unsafe_allow_html=True)
    number2.write(f"<span style='color:{color2};'>{random_number2}</span>", unsafe_allow_html=True)

    # Wait for 1 second before displaying the next set of random numbers
    time.sleep(1)
