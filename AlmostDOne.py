#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load and clean the data
leave_data = pd.read_csv('Leave List.csv')
leave_data.columns = leave_data.iloc[0]
leave_data = leave_data[1:]  # Drop the first row now that headers are set
# Set the correct column headers
leave_data.columns = ['ID', 'Surname', 'First Name', 'Job Title', 'Leave Type', 'Start', 'Finish']
leave_data = leave_data.dropna(subset=['Surname'])



# Clean 'Start' and 'Finish' columns to ensure uniform format by removing any additional spaces
#leave_data['Start'] = leave_data['Start'].str.strip()
#leave_data['Finish'] = leave_data['Finish'].str.strip()

# Convert 'Start' and 'Finish' dates to datetime format
leave_data['Start'] = pd.to_datetime(leave_data['Start'], format='%d/%m/%Y')
leave_data['Finish'] = pd.to_datetime(leave_data['Finish'], format='%d/%m/%Y')

# Retry converting 'Start' and 'Finish' columns to datetime format with more flexible parsing
#leave_data['Start'] = pd.to_datetime(leave_data['Start'], errors='coerce')
#leave_data['Finish'] = pd.to_datetime(leave_data['Finish'], errors='coerce')





# Check for any rows where dates could not be converted to ensure we don't have missing data
leave_data[leave_data['Start'].isnull() | leave_data['Finish'].isnull()]



# In[2]:


# Re-attempt to expand the dates between Start and Finish for each leave record
leave_data_expanded = leave_data.apply(lambda row: pd.date_range(start=row['Start'], end=row['Finish']), axis=1)
leave_data_expanded = leave_data_expanded.explode().reset_index()

# Merge the expanded dates back with the original dataframe to get job titles
leave_data_final = leave_data_expanded[['index', 0]].merge(leave_data[['Job Title']], left_on='index', right_index=True)
leave_data_final = leave_data_final.rename(columns={0: 'Date'})

# Group by Job Title and Date
leave_data_grouped = leave_data_final.groupby(['Job Title', 'Date']).size().unstack(fill_value=0).T

leave_data_grouped.head()


# In[3]:


# Find dates where the count reaches 4 or above for each job title
high_leave_counts = leave_data_grouped[leave_data_grouped >= 4].dropna(how='all').stack().reset_index()
high_leave_counts.columns = ['Date', 'Job Title', 'Count']

# Merge with the original data to get the surnames of individuals on leave for these dates and job titles
high_leave_details = high_leave_counts.merge(leave_data_final, on='Date').merge(leave_data[['Surname', 'Job Title']], left_index=True, right_index=True)
high_leave_details = high_leave_details[high_leave_details['Job Title_x'] == high_leave_details['Job Title_y']][['Date', 'Job Title_x', 'Surname']].drop_duplicates()

colors = ['blue', 'green', 'red', 'purple']
# Plotting
plt.figure(figsize=(14, 9))

plt.figure(figsize=(14, 9))
for index, job_title in enumerate(leave_data_grouped.columns):
    plt.plot(leave_data_grouped.index, leave_data_grouped[job_title], label=job_title, color=colors[index])
    # Annotating surnames where the count is 4 or above
    for _, row in high_leave_details[high_leave_details['Job Title_x'] == job_title].iterrows():
        plt.annotate(row['Surname'], (row['Date'], 4), textcoords="offset points", xytext=(0,10), ha='center', color=colors[index])

plt.title('Leave Patterns by Job Title (Specified Period)')
plt.xlabel('Date')
plt.ylabel('Number of People on Leave')
plt.xticks(rotation=45)
plt.xlim(leave_data['Start'].min(), leave_data['Finish'].max())
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
plt.legend(title='Job Title')
plt.grid(True)
plt.tight_layout()

# Save the plot with annotations
annotated_plot_path = 'leave_patterns_by_job_title_annotated.png'
plt.savefig(annotated_plot_path)

plt.show()


# In[ ]:




