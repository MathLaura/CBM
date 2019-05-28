import numpy as np
from datascience import *
from datetime import datetime

def first_row_sum(table):
    table = table.drop(0)
    sum_ = 0
    for i in np.arange(table.num_columns):
        sum_ += table[i].item(0)
    return sum_

def count_class_major_year(class_, major, year, major_col, year_col,census):
    subset = census.where(major_col, are.equal_to(major)).where(year_col, are.equal_to(year))
    count = 0
    for i in np.arange(subset.num_rows):
        for k in np.arange(subset.num_columns):
            if subset.column(k).item(i) == class_:
                count += 1
    return count

def census_to_perc(major_col, year_col, census_filename, classes_filename, majors_filename, years_filename):
    print(str(datetime.now()))
    census = Table.read_table(census_filename)
    classes = Table.read_table(classes_filename)
    majors = Table.read_table(majors_filename)
    #years = Table().with_column("Years", make_array("1_fros", "2_soph", "3_juno", "4_seno", "5_grad"))
    years = Table.read_table(years_filename)
    counts = census.pivot(major_col, year_col)
    table_majors_in_census = census.group(major_col)
    for i in np.arange(len(years.column("Years"))): 
        year = years.column("Years").item(i)
        status_message = "Working on year "+str(year)
        print(status_message)
        for major in majors.column("Majors"):
            col_title = major+" count for "+str(year)
            col_counts = make_array()    
            for j in np.arange(classes.num_rows):
                class_ = classes.column("Classes").item(j)
                col_counts = np.append(col_counts,count_class_major_year(class_, major, year, major_col, year_col,census))
            classes = classes.with_column(col_title, col_counts)
            if sum(table_majors_in_census.column(0)==major) == 0:
                col_counts = col_counts*0
            elif counts.column(major).item(i) == 0:
                col_counts = col_counts*0
            else: 
                col_counts = col_counts/counts.column(major).item(i)
            classes = classes.with_column(col_title, col_counts)
    print(str(datetime.now()))
    return classes

previous_semesters = int(input("How many previous semesters of data are you using?\n"))
rounding_var = 2
census_perc_list = list()
for i in np.arange(previous_semesters):
    if i == 0:
        filename = str(input("What is the filename of the first census file, including .csv?\n"))
    else: 
        filename = str(input("What is the filename of the next census file, including .csv?\n"))
    major_col = int(input("What column has the information about major, as a number?\n")) 
    major_col = major_col - 1
    year_col = int(input("What column has the information about the year students are in, as a number?\n")) 
    year_col = year_col - 1
    census_perc = census_to_perc(major_col, year_col, filename, "classes.csv", "majors.csv", "years.csv")
    census_perc_list.append(census_perc)

header = census_perc_list[0].where(0, are.equal_to(0)).drop("Classes")        
header.to_df().to_csv('StudentData.csv', index = False)                
print("The file Student_Data.csv has just been created. Please enter the anticipated number of students in each major and year.")
complete_flag = str(input("When you have saved StudentData.csv, type C and press enter."))

classes = Table.read_table("classes.csv").column("Classes")
students = Table.read_table("StudentData.csv")
results = Table().with_columns(["Course", [], "Nonzero Min", [], "Nonzero Average", [],"Nonzero Max", []])
                                
for class_ in classes:
    class_table = header
    for i in np.arange(previous_semesters):
        census_perc_for_class = census_perc_list[i].where("Classes", are.equal_to(class_)).drop("Classes")
        if first_row_sum(census_perc_for_class) != 0:
            class_table = class_table.with_row(census_perc_for_class.item(0))
    max_perc = make_array()
    min_perc = make_array()
    ave_perc = make_array()
    max_ = 0
    min_ = 0
    ave_ = 0
    for i in np.arange(class_table.num_columns):
        if class_table.num_rows == 0:
            max_ += 0
            ave_ += 0
            min_ += 0
        else: 
            max_col = max(class_table.column(i))
            max_perc = np.append(max_perc, max_col)
            max_ += max_col*students.column(i).item(0) 
            min_col = min(class_table.column(i))
            min_perc = np.append(min_perc, min_col)
            min_ += min_col*students.column(i).item(0) 
            ave_col = np.average(class_table.column(i))
            ave_perc = np.append(ave_perc, ave_col)
            ave_ += ave_col*students.column(i).item(0) 
    new_row = [class_, round(min_,rounding_var), round(ave_,rounding_var), round(max_,rounding_var)]
    results = results.with_row(new_row)
                            
results.to_df().to_csv('results.csv', index = False)