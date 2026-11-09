# Entrepôt décisionnel pour un essai d’avoine

Un schéma en étoile sépare les mesures de rendement et leurs trois dimensions (bloc, variété et dose d’azote). Une requête SQL agrège 72 parcelles en 12 combinaisons variété–dose. Le tableau HTML compare moyenne, minimum, maximum et effectif.

## Reproduction

Télécharger [Oats.csv](https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/nlme/Oats.csv) à côté de warehouse.py puis lancer `python warehouse.py`. Ouvrir dashboard.html. Python 3 et sa bibliothèque standard suffisent.

La [documentation de nlme](https://stat.ethz.ch/R-manual/R-devel/library/nlme/html/Oats.html) cite l’expérience de Yates (1935), organisée en six blocs, trois variétés et quatre doses. Les résultats sont descriptifs. Le tableau compare des moyennes observées sur un essai historique.
