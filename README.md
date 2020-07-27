Explication du programme : 

Nous générons tout d’abord un monde Wumpus de taille n = 10 pour illustrer le
fonctionnement de notre programme. Ce nombre est modifiable. Tout d’abord,
un « chronomètre » est lancé avant le parcours. Puis nous lançons notre fonction
de parcours qui va permettre de probe les cases adjacentes à partir de la case
initiale puis va déduire de cases en cases les nouvelles clauses à retenir tout en
mettant à jour le budget initial. Le coût est directement affiché après que les
cases d’or ont été trouvées par le programme. Le programme comporte une
fonction qui permet de vérifier qu’il y ait un bien un wumpus à la génération
ainsi que des puits.
Dans la variable parcours_time, il est stocké la différence entre le temps actuel
et le temps enregistré avant la lancée du programme de parcours. Parcours_time
est ensuite affiché.
A l’aide de notre fonction afficherMap, nous montrons ensuite la carte qui avait
été initialement générée afin de comparer avec le résultat de notre algorithme de
parcours. Les coordonnées des Gold ainsi que le chemin final parcouru par notre
algorithme de parcours sont également affichés après le dévoilement de la carte.


Lancement du programme :

Nous compilons notre programme via Spyder. Attention, pensez à bien raccorder
le bon pathway pour retrouver l’application gophersat-1.1.6. Comme dit
précédemment, la taille du monde Wumpus à générer est configurable dans la
fonction main. L’affichage final des résultats prend en général entre 50s et 80s
en fonction des cartes générées. 
