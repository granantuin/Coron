import streamlit as st
import pandas as pd
import time
import numpy as np
import random

# Create a DataFrame with some initial values
df = pd.DataFrame({
    'time': pd.date_range(start='2023-05-06', freq='1H', periods=4),
    'dir': np.full((4,), 240),
    'dir_std': np.full((4,), 10)
})

# Define a Streamlit app function
def main():
    # Add a title to the app
    st.title("Random Numbers App")

    # Create an infinite loop to update the DataFrame and display it in real-time
    while True:
        # Generate random numbers for the dir_d column
        df["dir_d"] = [round(random.random() * df.dir_std[i] + df.dir[i]) for i in range (0,4)] 
        
        # Display the updated DataFrame in a Streamlit table
        st.table(df[["time",'dir_d']])

        # Wait for 1 second before displaying the next set of random numbers
        time.sleep(1)

# Call the app function
if __name__ == "__main__":
    main()
