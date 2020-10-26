import xlsxwriter

def retrieve_data():
    mFile = open("experiment_results_0-5_error_pkt_size.txt", "r")
    Lines = mFile.readlines()
    list_of_lines = []
    for line in Lines:
        list_of_lines.append(line)
    
    # create file (workbook) and worksheet
    outWorkbook = xlsxwriter.Workbook("parsed_results_2.xlsx")
    outSheet = outWorkbook.add_worksheet()

    row_pointer = 0
    for i in range(len(list_of_lines)):
        if i % 3 != 0:
            continue
        error_probability = list_of_lines[i].split(" ")[0]
        outSheet.write(row_pointer, 0, error_probability)
        col_pointer = 1
        for j in range(3):
            print(f"val of i: {i}")
            curr_line = list_of_lines[i]
            transfer_time = curr_line.split(" ")[1]
            through_put = curr_line.split(" ")[2]
            outSheet.write(row_pointer, col_pointer, transfer_time)
            outSheet.write(row_pointer, col_pointer + 1, through_put)
            col_pointer += 2
            i += 1
        row_pointer += 1
    outWorkbook.close()

retrieve_data()