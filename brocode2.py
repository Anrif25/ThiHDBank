"""a = float(input("Nhap vao so a:" ))
b = float(input("Nhap vao so b:" ))
chon = input("moi nhap phep tinh: ")

if chon == "+":
    c = a+b
elif chon == "-":
    c= a -b
elif chon =="*":
    c=a*b
elif chon =="/":
    c=a/b
else:
    print("khong co phep tinh nay")
    c="?"
   
print(f"c= {c}")
 """
d =5 
#locical operator (and or (and)not) 
Chu_cai= False

if d > 5 and not Chu_cai:
    print("D la so lon hon 5")

#Conditional Expression 
print ("Positive" if d >5 else "Negative")
result = "Even" if d%2==0 else "ODD"
print(result)

#String
name = input("Your name ")
#Str = len(name) #Lenght of string
#Str = name.find("b") #Find how many time a character appear in string
#Str = name.rfind("b") #Find a character LAST appear in string
#Str = name.capitalize() #UpperCase first letter
#Str = name.upper()
#Str = name.lower()
Str = name.isdigit()
Str = name.isalpha()
print(Str)


#idexing
stri = "123abcxyz789"
#print(stri[4])
#print(stri[:4])
#print(stri[-1]) #last index
print(stri[::4]) #take the letter after 4 


#format 
price1 = 3.1412341
print(f"price 1 is {price1:.2f}")

#while
name = input("enter your name: ")

while name =="":
    print("you must enter your name")
    name = input("enter your name: ")

print(f"hello {name}")
    