## Projekat je napravljen sa ciljem prepoznavanja šake preko Raspberry Pi kamere,pa bi robot na osnovu toga da li je šaka otvorena ili zatvorena pomerao svoj Gripper prikljucak.


### Funkcionalnosti su raspoređene u nekoliko Python i Jupyter Notebook skripti. Glavne kontrole za robota se nalaze u control folderu, gde gripper.py sadrži funkcije za pomeranje odgovarajućeg motora, dok se kontrola onoga što kamera prepoznaje nalazi u vision folderu (hand_open_close.py util samo prebacuje sliku u format koji je lakši za program da prepozna, dok je za logiku ruke korisćena cvzone biblioteka HandTrackingModule). Takođe smo implementirali debounce.py kao util, čija je funkcija da stabilizuje sliku, kako se program ne bi zbunio ako se ruka previse brzo pomera. 
###  Ovde smo imali problema najvise sa mediapipe, zato sto on jedino radi na Python verzijama 3.9-3.12. Pošto Raspberry Pi koristi verziju 3.7, a uređaji koje smo koristili logično koriste najnoviju verziju, morali smo da svedemo rad na samo jedan laptop koji je imao instalirano Python 3.12.
#

### Glavni program se nalazi u app folderu. Imali smo dosta muka sa testiranjem koda, najviše zbog prethodno spomenutih problema sa Python verzijama, ali smo na kraju uspeli da smislimo sistem koji uspešno koristi mediapipe. Posto Raspberry Pi povezan na Poppy funkcioniše kao hotspot, napravili smo da u isto vreme radi kao server koji komunicira sa povezanim klijentom (u ovom slucaju uređaj koji pokreće kod). Nakon što se pokrene, Raspberry serijalizuje i lepo spakuje trenutni frejm sa svoje kamere, i pošalje ga svom klijentu. Odatle, klijent ima slobodu da koristi cvzone biblioteke, pošto one imaju mediapipe u svojoj osnovi.
###  U prvom trenutku smo hteli da Raspberry Pi i uređaj budu povezani na treću WiFi mrezu, i nismo mogli da shvatimo zašto Raspberry nije mogao da se poveže, iako je znao da mreža postoji, ali smo ubrzo shvatili da ne može da se ponaša kao hotspot i povezan uređaj u isto vreme.
#
