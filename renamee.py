import os

count = 1
for file in os.listdir("D:/html-projects/pilot-study-2/images-hover"):

    path = os.path.join("D:/html-projects/pilot-study-2/images-hover",file)
    os.rename(path,f"D:/html-projects/pilot-study-2/images-hover/PQ{count:02d}.jpg")

    count+=1
