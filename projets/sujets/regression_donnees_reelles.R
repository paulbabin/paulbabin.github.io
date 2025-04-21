setwd("/Users/babinou/cours/saereg")

##### IMPORT #####
train <- read.csv2("train.csv")
test <- read.csv2("test.csv")

######################
### PARTIE 1 : MAISONS
######################
# Filtre des maisons valides
maisons_train <- train[train$Type.local == "Maison" & train$Surface.reelle.bati > 0 & train$Valeur.fonciere > 0, ]
maisons_train$prix_m2 <- maisons_train$Valeur.fonciere / maisons_train$Surface.reelle.bati

# Villes uniques
villes_maisons <- unique(maisons_train$Commune)

# Création du tableau des prix moyens par ville
Commune <- c()
prix_moyen_m2 <- c()
for (ville in villes_maisons) {
  prixs <- maisons_train$prix_m2[maisons_train$Commune == ville]
  moyenne <- mean(prixs, na.rm = TRUE)
  Commune <- c(Commune, ville)
  prix_moyen_m2 <- c(prix_moyen_m2, moyenne)
}
prix_moyen_maison <- data.frame(Commune, prix_moyen_m2)

# Fusion avec test
test <- merge(test, prix_moyen_maison, by = "Commune", all.x = TRUE)

# Prédiction pour les maisons uniquement
maisons_test_index <- which(test$Type.local == "Maison")
test$Valeur.fonciere[maisons_test_index] <- test$prix_moyen_m2[maisons_test_index] * test$Surface.reelle.bati[maisons_test_index]

###########################
### PARTIE 2 : APPARTEMENTS
###########################
# Filtre des appartements valides
appartements_train <- train[train$Type.local == "Appartement" & train$Surface.reelle.bati > 0 & train$Valeur.fonciere > 0, ]
appartements_train$prix_m2 <- appartements_train$Valeur.fonciere / appartements_train$Surface.reelle.bati

# Forcer les types à correspondre pour eviter les erreurs
appartements_train$Nombre.pieces.principales <- as.integer(appartements_train$Nombre.pieces.principales)

# Prix moyen global pour les appartements 
prix_moyen_appartement_global <- mean(appartements_train$prix_m2, na.rm = TRUE)

# Identification des appartements dans le jeu de test
appartements_test_index <- which(test$Type.local == "Appartement")
appartements_test <- test[appartements_test_index, ]

# Créer un nouveau dataframe pour la prédiction des appartements
appartements_prediction <- data.frame(
  id = appartements_test$id,
  Commune = appartements_test$Commune,
  Nombre.pieces.principales = as.integer(appartements_test$Nombre.pieces.principales),
  Surface.reelle.bati = appartements_test$Surface.reelle.bati
)

# Initialiser la colonne prix_moyen_m2 avec le prix moyen global
appartements_prediction$prix_moyen_m2 <- prix_moyen_appartement_global

# Générer un prix moyen par ville et nombre de pièces
prix_moyen_par_ville_pieces <- aggregate(
  prix_m2 ~ Commune + Nombre.pieces.principales, 
  data = appartements_train, 
  FUN = function(x) mean(x, na.rm = TRUE)
)

# Générer un prix moyen par ville seulement si le bon nombre de piece n'existe pas 
prix_moyen_par_ville <- aggregate(
  prix_m2 ~ Commune, 
  data = appartements_train, 
  FUN = function(x) mean(x, na.rm = TRUE)
)

# Appliquer la stratégie en cascade pour déterminer le prix par m²
for (i in 1:nrow(appartements_prediction)) {
  ville <- appartements_prediction$Commune[i]
  pieces <- appartements_prediction$Nombre.pieces.principales[i]
  
  # Chercher d'abord dans le tableau par ville et pièces
  prix_specifique <- prix_moyen_par_ville_pieces[
    prix_moyen_par_ville_pieces$Commune == ville & 
      prix_moyen_par_ville_pieces$Nombre.pieces.principales == pieces, 
    "prix_m2"
  ]
  
  if (length(prix_specifique) > 0 && !is.na(prix_specifique)) {
    appartements_prediction$prix_moyen_m2[i] <- prix_specifique
    next
  }
  
  # Sinon chercher seulement par ville
  prix_ville <- prix_moyen_par_ville[
    prix_moyen_par_ville$Commune == ville, 
    "prix_m2"
  ]
  
  if (length(prix_ville) > 0 && !is.na(prix_ville)) {
    appartements_prediction$prix_moyen_m2[i] <- prix_ville
  }
  # Sinon on garde le prix moyen global déjà assigné
}

# Calculer le prix pour chaque appartement
appartements_prediction$Valeur.fonciere <- appartements_prediction$prix_moyen_m2 * appartements_prediction$Surface.reelle.bati

# Réintégrer les résultats dans le jeu de test
for (i in 1:nrow(appartements_prediction)) {
  idx <- which(test$id == appartements_prediction$id[i])
  if (length(idx) > 0) {
    test$Valeur.fonciere[idx] <- appartements_prediction$Valeur.fonciere[i]
  }
}

###########################
### EXPORT FINAL
###########################
# Garder les deux colonnes
prediction <- test[, c("id", "Valeur.fonciere")]

# Export du csv prediction
write.csv2(prediction, "prediction.csv", row.names = FALSE)



