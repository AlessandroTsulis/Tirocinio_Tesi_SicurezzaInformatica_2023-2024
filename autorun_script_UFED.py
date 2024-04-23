import mouse
#le coordinate in cui muovere il mouse valgono solo negli schermi dell'ufficio, non anche dal tuo PC

mouse.move(2347, 54, absolute=True, duration=0.01) #muovi il mouse sulle coordinate assolute dello schermo x=2347, y=54 
mouse.click('left') #fai click sinistro del mouse
#mouse.move(2347, 120, absolute=False, duration=0.01)
mouse.move(0, 70, absolute=False, duration=0.01) #muovi il mouse di 70 sull'asse y rispetto alla posizione attuale del mouse
#mouse.move(2600, 120, absolute=True, duration=0.7)
mouse.move(250, 0, absolute=False, duration=0.8)
mouse.click('left')
#mouse.move(2600, 330, absolute=True, duration=0.06)
mouse.move(0, 220, absolute=False, duration=0.08) 
for i in range(2): #fai doppio click
    mouse.click('left')

#print(mouse.get_position())