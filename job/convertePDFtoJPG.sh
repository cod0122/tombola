#!/bin/bash
#
##--- Converte (da PDF a JPG) e copia i file della cartella PUBBLICA 
#--- Prima installare il programmino:
#--- sudo apt-get install imagemagick

cd $HOME/tombola

rm ./pubblica/*

cd $HOME/tombola/job

cd appoggio

#--- Converte file PDF in JPEG e li copia nella cartella 'pubblica'
for i in `ls *.pdf`; do convert -quality 100 "$i" "../../pubblica/$i".jpg; done
#for i in `ls *.pdf`; do convert -density 1024x768 "$i" "../../pubblica/$i".jpg; done
if [ $? != 0 ]; then
   exit 1
fi

# se si vuole usare ghostscript allora:
# sudo apt-get install ghostscript
# gs -dNOPAUSE -sDEVICE=jpeg -dFirstPage=1 -dLastPage=5 -sOutputFile=output%d.jpg -dJPEGQ=100 -r500 -q intput.pdf -c quit

#--- copia file non PDF nella cartella 'pubblica'
for i in `ls *.*`; 
   do 
      if [ $i != *.pdf ]; then
         echo $i;
         cp "$i" "../../pubblica/$i";
      fi;
done
if [ $? != 0 ]; then
   exit 1
fi

