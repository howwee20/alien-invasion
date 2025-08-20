bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0].upper())
print(bicycles[-2].title())
bicycles.append('brompton')

bicycles[1] = 'giant'
bicycles.insert(1, 'scott')
print(bicycles)

message = f"My first bicycle was a {bicycles[1].title()}."
print(message)




