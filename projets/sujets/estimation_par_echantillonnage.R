library(sampling)
#import des données
table = read.csv2(file ="population_francaise_communes3.csv",sep = ";",dec=",",header=TRUE) 

##################### -- Partie 1.1 -- #####################
#filtrage des données sur la région PACA
donnees = table[table$Nom.de.la.région == "Provence-Alpes-Côte d'Azur",c("Code.département","Commune","Population.totale")]
head(donnees)

#ensemble des communes de la région
U = donnees$Commune
head(U)
N = length(U)

#filtrage et calcul du nombre exact T d'habitants de la région PACA
donnees$Population.totale = as.numeric(gsub(" ","",donnees$Population.totale))
T = sum(donnees$Population.totale)
T
#création d'un échantillon(sample) de 100 communes
n = 100
E = sample(U,n)
#création d'une table données1 contenant les communes de l'échantillon aléatoire,
#leur département et leur nombre d'habitants
donnees1= donnees[donnees$Commune %in% E, ]
head(donnees1)

#calcul du nombre moyen d'habitants
xbar= mean(donnees1$Population.totale)
#calcul d'un IDC à 95% du nombre moyen d'habitants
idcmoy = t.test(donnees1$Population.totale)$conf.int

#valeur estimée du nombre d'habitants
T_est = N*xbar
T_est

#intervalle de confiance pour T
idcT = idcmoy*N
idcT

#marge d'erreur pour pour l'IDC de T
marge=(idcT[2]-idcT[1])/2
marge

#création d'un dataframe qui servira à récolter les résultats pour plusieurs échantillons
#(ici dix échantillons)
resultats <- data.frame()

#boucle qui permet d'automatiser les calculs présents au dessus pour un gain de temps
#pour 10 itérations 
for (i in 1:10) {
  E = sample(U, n)
  donnees1 = donnees[donnees$Commune %in% E, ]
  xbar = mean(donnees1$Population.totale)
  idcmoy = t.test(donnees1$Population.totale)$conf.int
  T_est = N * xbar
  idcT = idcmoy * N
  marge = (idcT[2] - idcT[1]) / 2
  
  resultats <- rbind(resultats, data.frame(
    T = T,
    T_est = T_est,
    Borne_inf = idcT[1],
    Borne_sup = idcT[2],
    Marge = marge
  ))
}

#création d'un fichier csv ouvrable sur excel comprenant les résultats des 10 itérations
write.csv2(resultats, file = "resultats_estimations.csv", row.names = FALSE)

##################### -- Partie 1.2 -- #####################
summary(donnees$Population.totale)

# Paramètres personnalisables
k <- 6              #nombre de strates
n <- 100            #taille de l'échantillon

#création des strates
bornes <- quantile(donnees$Population.totale, probs = seq(0, 1, length.out = k + 1), na.rm = TRUE)
#découpage la population en strates
donnees$strate <- cut(donnees$Population.totale, breaks = bornes, labels = 1:k, include.lowest = TRUE)
head(donnees)
# Préparation de la table ordonnée avec l'effectif des strates
datastrat <- donnees[, c("Commune", "Population.totale", "strate")]
data <- datastrat[order(datastrat$strate), ]
Nh <- table(data$strate)
N <- sum(Nh)
#poids des strates
gh <- Nh / N
#tirage d'un échantillon stratifié
nh <- round(n * Nh / N)
#tux de sondage dans les strates
fh <- nh / Nh

#création d'un dataframe qui servira à récolter les résultats
resultats_stratifie <- data.frame()

#on répète l'expérience dix fois grâce à une boucle
for (i in 1:10) {
  st <- strata(data, stratanames = c("strate"), size = nh, method = "srswr")
  data1 <- getdata(data, st)
  
  moyennes <- numeric(k)
  variances <- numeric(k)
  
  for (j in 1:k) {
    ech <- data1[data1$strate == j, ]
    moyennes[j] <- mean(ech$Population.totale)
    variances[j] <- var(ech$Population.totale)
  }
  
  # Estimation moyenne et variance
  Xbarst <- sum(Nh * moyennes) / N
  varXbarst <- sum((gh^2) * (1 - fh) * variances / nh)
  
  # IDC
  alpha <- 0.05
  binf <- Xbarst - qnorm(1 - alpha / 2) * sqrt(varXbarst)
  bsup <- Xbarst + qnorm(1 - alpha / 2) * sqrt(varXbarst)
  idcmoy <- c(binf, bsup)
  
  # Estimations totales
  Tstr <- Xbarst * N
  idcT <- idcmoy * N
  marge <- (idcT[2] - idcT[1]) / 2
  
  # Stockage des résultats
  resultats_stratifie <- rbind(resultats_stratifie, data.frame(
    T = T,
    T_est = Tstr,
    Borne_inf = idcT[1],
    Borne_sup = idcT[2],
    Marge = marge
  ))
}

# Export CSV
write.csv2(resultats_stratifie, file = paste0("resultats_stratifie_k", k, ".csv"), row.names = FALSE)

resultats$Methode <- "Simple"
resultats_stratifie$Methode <- "Stratifie"
resultats_fusionnes <- rbind(resultats, resultats_stratifie)

#création du fichier contenant les réslutats des sondages simple et stratifés afin de faire les graphiques
write.csv2(resultats_fusionnes, file = "comparaison_methodes.csv", row.names = FALSE)

##################### -- Partie 2 -- #####################

tablesport = read.csv2("C:/Users/eguena01/OneDrive - Université de Poitiers/SEMESTRE 2/Stat inf/SAÉ/EnqueteSportEtudiant2024.csv", 
                       sep = ";", dec = ";", header = TRUE)
head(tablesport)

#4 : on croise la variable sport avec 8 variables qualitatives
# Tableaux croisés dynamiques entre le sport et chaque variable qualitative
TCD_Sexe = table(tablesport$sport, tablesport$sexe)
TCD_Alternant = table(tablesport$sport, tablesport$alternant)
TCD_Dept = table(tablesport$sport, tablesport$deptformation)
TCD_niveau = table(tablesport$sport, tablesport$niveau)
TCD_logement = table(tablesport$sport, tablesport$logement)
TCD_fumer = table(tablesport$sport, tablesport$fumer)
TCD_alimentation = table(tablesport$sport, tablesport$alimentation)
TCD_sante = table(tablesport$sport, tablesport$sante)

TCD_Sexe
TCD_Alternant
TCD_Dept
TCD_niveau
TCD_logement
TCD_fumer
TCD_alimentation
TCD_sante

# Test du khi2 pour chaque variable/TCD
khideux_Sexe= chisq.test(TCD_Sexe)
khideux_Sexe #p-value = 0.0006292 --> relation significative

khideux_Alternant= chisq.test(TCD_Alternant)
khideux_Alternant #p-value = 0,14 --> preuve modérée contre l'hypothèse nulle, peut-être que c'est dû au hasard

khideux_Dept= chisq.test(TCD_Dept)
khideux_Dept #p-value = 0.004557 --> relation significative

khideux_niveau= chisq.test(TCD_niveau)
khideux_niveau #p-value = 0.1238 --> preuve modérée contre l'hypothèse nulle

khideux_logement= chisq.test(TCD_logement)
khideux_logement #p-value = 0.3084 --> preuve plus que modérée pour l'hypothèse nulle

khideux_fumer= chisq.test(TCD_fumer)
khideux_fumer #p-value = 0.6666 --> très élevé, il n'y a quasiment pas de lien

khideux_alimentation= chisq.test(TCD_alimentation)
khideux_alimentation #p-value = 0.000241 --> relation significative

khideux_sante= chisq.test(TCD_sante)
khideux_sante #p-value = 0.7028 --> très élevé, il n'y a quasiment pas de lien

# V de Cramer pour chaque variable 
n<-dim(tablesport)[1]
p <- nrow(TCD_Sexe)
q <- ncol(TCD_Sexe)
m <- min(p-1, q-1)
V_Sexe =sqrt(khideux_Sexe$statistic/(n*m))
V_Sexe 

n<-dim(tablesport)[1]
p <- nrow(TCD_alimentation)
q <- ncol(TCD_alimentation)
m <- min(p-1, q-1)
V_alimentation =sqrt(khideux_alimentation$statistic/(n*m))
V_alimentation 

n<-dim(tablesport)[1]
p <- nrow(TCD_Dept)
q <- ncol(TCD_Dept)
m <- min(p-1, q-1)
V_Dept =sqrt(khideux_Dept$statistic/(n*m))
V_Dept 

n<-dim(tablesport)[1]
p <- nrow(TCD_Alternant)
q <- ncol(TCD_Alternant)
m <- min(p-1, q-1)
V_Alternant =sqrt(khideux_Alternant$statistic/(n*m))
V_Alternant 

n<-dim(tablesport)[1]
p <- nrow(TCD_niveau)
q <- ncol(TCD_niveau)
m <- min(p-1, q-1)
V_niveau =sqrt(khideux_niveau$statistic/(n*m))
V_niveau 

n<-dim(tablesport)[1]
p <- nrow(TCD_logement)
q <- ncol(TCD_logement)
m <- min(p-1, q-1)
V_logement =sqrt(khideux_logement$statistic/(n*m))
V_logement 

n<-dim(tablesport)[1]
p <- nrow(TCD_fumer)
q <- ncol(TCD_fumer)
m <- min(p-1, q-1)
V_fumer =sqrt(khideux_fumer$statistic/(n*m))
V_fumer

n<-dim(tablesport)[1]
p <- nrow(TCD_sante)
q <- ncol(TCD_sante)
m <- min(p-1, q-1)
V_sante =sqrt(khideux_sante$statistic/(n*m))
V_sante






