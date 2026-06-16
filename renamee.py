import os

count = 1
for file in os.listdir("D:/html-projects/pilot-study-2/images"):

    path = os.path.join("D:/html-projects/pilot-study-2/images",file)
    os.rename(path,f"D:/html-projects/pilot-study-2/images/P{count:02d}.jpg")
    count+=1
