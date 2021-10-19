fo = open("movie.txt","wb")
for i in range(0, 30000):
	stri=str(i)
	strframe = "F" *1019+stri.zfill(5)
	#strframe = stri.zfill(5)
	fo.write(strframe)
fo.close()