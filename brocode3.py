#python compound interest caculator

principle = 0
rate = 0
time = 0
while principle <=0:
    principle = float(input("enter the principle amount: "))
    if principle <=0:
        print("Principle can't be less or equal zero!")
        


while rate<=0:
    rate = float(input("enter the rate amount: "))
    if rate <=0:
        print("rate can't be less or equal zero!")

while time<=0:
    time = int(input("enter the time amount: "))
    if time <=0:
        print("time can't be less or equal zero!")
        
print(principle)
print(rate)
print(time)

total = principle * pow((1+rate/100),time)

print(f"balance after {time} years: ${total:.2f}")