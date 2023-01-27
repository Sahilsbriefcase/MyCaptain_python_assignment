filename = input("Enter Your Filename: ")
text = filename.split(".")
if text[1]=="py":
    print("python")
if text[1]=="txt":
    print("text")
if text[1]=="pdf":
    print("pdf")
if text[1]=="docx":
    print("Word")    

