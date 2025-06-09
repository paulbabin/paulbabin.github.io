import tkinter as tk  # Import du module tkinter pour l'interface graphique
from tkinter import ttk, filedialog, messagebox  # Import de widgets et boîtes de dialogue tkinter
import os  # Pour les opérations sur les fichiers et chemins
import re  # Pour les expressions régulières (nettoyage de texte)
import json  # Pour manipuler des données JSON
import webbrowser  # Pour ouvrir des liens dans le navigateur
import threading  # Pour lancer des tâches en parallèle (thread)
import importlib.util  # Pour vérifier la présence de modules Python
import sys  # Pour accéder à l'interpréteur Python courant
import subprocess  # Pour lancer des commandes système (installation de modules)


def afficher_fenetre_installation(nb_modules: int) -> tuple:
    """
    Objectif :
        Affiche une fenêtre Tkinter avec une barre de progression pour indiquer l'installation des librairies requises.

    Paramètres :
        nb_modules (int) : Nombre total de modules à installer.

    Donnée retournée :
        tuple : (fenetre, barre, label)
            fenetre (tk.Tk) : La fenêtre principale Tkinter.
            barre (ttk.Progressbar) : La barre de progression.
            label (ttk.Label) : Le label affichant le pourcentage d'installation.

    Exemple :
        afficher_fenetre_installation(5) retourne une fenêtre avec une barre de progression pour 5 modules à installer.
    """
    fenetre = tk.Tk()  # Création de la fenêtre principale
    fenetre.title("Installation des librairies requises")  # Titre de la fenêtre
    fenetre.geometry("480x100")  # Taille de la fenêtre
    fenetre.resizable(False, False)  # Fenêtre non redimensionnable
    fenetre.attributes('-toolwindow', True)  # Apparence simplifiée

    progress_text_frame = tk.Frame(fenetre)  # Frame pour le texte de progression
    progress_text_frame.pack(fill='x', padx=10, pady=(0, 5))  # Placement du frame

    label = ttk.Label(progress_text_frame, text="0% terminé", font=("Segoe UI Semibold", 11))  # Label pour le pourcentage
    label.pack(side='left', anchor='w')  # Placement du label

    barre = ttk.Progressbar(fenetre, mode='determinate', maximum=100)  # Barre de progression
    barre.pack(fill='x', padx=10, pady=(0, 5))  # Placement de la barre

    details_frame = tk.Frame(fenetre)  # Frame pour le texte de détail
    details_frame.pack(fill='x', padx=10, pady=(0, 5))  # Placement du frame

    arrow_label = ttk.Label(details_frame, text="> Veuillez patienter", font=("Segoe UI", 10))  # Message d'attente
    arrow_label.pack(side='left')  # Placement du label

    fenetre.update()  # Rafraîchit la fenêtre pour afficher les éléments
    return fenetre, barre, label  # Retourne les objets utiles pour suivre la progression

def installer_si_absent(package:str)->None:
    """
    Installe un package Python via pip s'il n'est pas déjà installé.

    Paramètres:
        package (str): Nom du package à vérifier et installer si besoin.

    Exemple:
        installer_si_absent("pandas") installe le package pandas s'il n'est pas déjà installé.
    """
    # Vérifie si le module est déjà installé, sinon lance pip install
    if importlib.util.find_spec(package) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def lancer_tableau_bord():
    """
    Ouvre le tableau de bord Looker Studio dans le navigateur web par défaut.

    Exemple:
        lancer_tableau_bord() ouvre le tableau de bord dans le navigateur.
    """
    try:
        url = "https://lookerstudio.google.com/u/0/reporting/0d683486-5a0a-4964-9f07-203cb5be0e45/page/p_7ytrog38sd"  # Lien du dashboard
        webbrowser.open(url)  # Ouvre le lien dans le navigateur
        label_statut_traitement.config(text="Tableau de bord ouvert dans le navigateur")  # Mise à jour du statut
    except Exception as e:
        label_statut_traitement.config(text=f"Erreur ouverture navigateur: {str(e)}")  # Affiche une erreur si besoin

def extraire_donnees_nettoyees(df1: any, df2: any, df3: any) -> None:
    """
    Objectif :
        Exporte les DataFrames nettoyés vers un fichier Excel choisi par l'utilisateur.

    Paramètres :
        df1 (pd.DataFrame) : Premier DataFrame à exporter (bdquest).
        df2 (pd.DataFrame) : Deuxième DataFrame à exporter (accident).
        df3 (pd.DataFrame) : Troisième DataFrame à exporter (fusion).

    Exemple :
        extraire_donnees_nettoyees(df1, df2, df3) feit l'export des 3 dataframes vers un fichier Excel.
    """
    try:
        # Ouvre une boîte de dialogue pour choisir où sauvegarder le fichier Excel
        fichier_sortie = filedialog.asksaveasfilename(
            title="Sauvegarder les données nettoyées",
            defaultextension=".xlsx",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")]
        )

        if fichier_sortie:
            # Crée un fichier Excel avec trois feuilles
            with pd.ExcelWriter(fichier_sortie, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='bdquest', index=False)
                df2.to_excel(writer, sheet_name='accident', index=False)
                df3.to_excel(writer, sheet_name='fusion', index=False)
            # Affiche un message de succès
            label_statut_traitement.config(text=f"Données exportées vers {os.path.basename(fichier_sortie)}")
    except Exception as e:
        label_statut_traitement.config(text=f"Erreur export: {str(e)}")

def extraire_donnees_nettoyees_wrapper()->None:
    """
    Wrapper pour l'export des données nettoyées, gère l'animation et les erreurs.

    Exemple:
        extraire_donnees_nettoyees_wrapper() lance l'export des données nettoyées.
    """
    global df1, df2, df_final, phase_traitement

    # Vérifie que les DataFrames existent avant d'exporter
    if 'df1' in globals() and 'df2' in globals() and 'df_final' in globals():
        phase_traitement = "telechargement"  # Change la phase pour l'animation
        demarrer_animation()  # Lance l'animation
        try:
            extraire_donnees_nettoyees(df1, df2, df_final)  # Lance l'export
        finally:
            arreter_animation()  # Arrête l'animation même en cas d'erreur
    else:
        messagebox.showerror("Erreur", "Aucune donnée traitée disponible. Veuillez d'abord traiter un fichier.")

def nettoyer_retours_ligne(valeur:any)->any:
    """
    Nettoie une valeur texte en supprimant les retours à la ligne et espaces superflus.

    Paramètres:
        valeur (str | float | None): Valeur à nettoyer.

    Donnée retourné:
        str | float | None: Valeur nettoyée ou inchangée si NaN.

    Exemple:
        nettoyer_retours_ligne("abc\n def") retourne "abc def"
    """
    if pd.isna(valeur):
        return valeur
    valeur = str(valeur)
    # Remplace tous les retours à la ligne et tabulations par un espace
    valeur = re.sub(r'[\n\r\f\v\t]+', ' ', valeur)
    # Réduit les espaces multiples à un seul espace
    valeur = re.sub(r'\s+', ' ', valeur)
    return valeur.strip()

def retirer_instance(val:float)->(str|int|float):
    """
    Convertit un float entier en int sous forme de chaîne, sinon retourne la valeur d'origine.

    Paramètres:
        val (float): Valeur à convertir.

    Donnée retourné:
        str | any: Chaîne si float entier, sinon valeur d'origine.

    Exemple:
        retirer_instance(3.0)  retourne 3
        retirer_instance(3.5)  retourne 3.5
    """
    # Si la valeur est un float équivalent à un entier, retourne un int sous forme de chaîne
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return val

def extraire_annee(val:any)->(str|None):
    """
    Extrait l'année d'une chaîne représentant une date ou un nombre.

    Paramètres:
        val (str | float | None): Valeur à traiter.

    Donnée retourné:
        str | None: Année extraite sous forme de chaîne, ou None si extraction impossible.

    Exemple:
        extraire_annee("12/05/1990")  # "1990"
        extraire_annee("1990")        # "1990"
    """
    if pd.isna(val):
        return None
    val = str(val)
    # Si la valeur contient un "/", tente de parser la date
    if "/" in val:
        try:
            return str(pd.to_datetime(val, dayfirst=True).year)
        except:
            return None
    elif val.isdigit():
        # Si la valeur est un nombre à 4 chiffres, c'est probablement une année
        if len(val) == 4:
            return val
        # Si la valeur est un nombre à 8 chiffres, tente de parser comme date
        elif len(val) == 8:
            try:
                return str(pd.to_datetime(val, format="%d%m%Y").year)
            except:
                return None
    return None

def nettoyer_colonnes_numeriques(df:any, colonnes:any)->any:
    """
    Convertit les colonnes spécifiées d'un DataFrame en valeurs numériques et applique retirer_instance.

    Paramètres:
        df (pd.DataFrame): DataFrame à traiter.
        colonnes (list[str]): Liste des noms de colonnes à convertir.

    Donnée retourné:
        pd.DataFrame: DataFrame modifié.

    Exemple:
        nettoyer_colonnes_numeriques(df, ['col1', 'col2']) retourne un DataFrame avec les colonnes 'col1' et 'col2' converties en numériques.
    """
    for col in colonnes:
        if col in df.columns:
            # Convertit la colonne en numérique, remplace les erreurs par NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Applique la conversion float->int si possible
            df[col] = df[col].apply(retirer_instance)
    return df

def traiter_taille(valeur:any)->(int|None):
    """
    Traite une valeur de taille pour la convertir en centimètres selon des règles spécifiques.

    Paramètres:
        valeur (float | str | None): Valeur à traiter.

    Donnée retourné:
        int | None: Taille en centimètres ou None si invalide.

    Exemple:
        traiter_taille(1)    retourne 100
        traiter_taille(170)  retourne 170
        traiter_taille(6,5)  retourne None
    """
    try:
        if pd.isna(valeur):
            return None
        val_float = float(valeur)
        # Si la valeur n'est pas un entier, retourne None
        if not val_float.is_integer():
            return None
        val_int = int(val_float)
        # Si la valeur est comprise entre 1 et 3, on suppose que c'est en mètres, donc on multiplie par 100
        if val_int < 1:
            return None
        elif 1 <= val_int <= 3:
            return val_int * 100
        # Si la valeur est entre 3 et 100, ce n'est pas une taille valide
        elif 3 < val_int < 100:
            return None
        # Si la valeur est supérieure ou égale à 100, on considère que c'est déjà en cm
        elif val_int >= 100:
            return val_int
        else:
            return None
    except:
        return None

def analyse_lite_json(chaine:any)->(list|list[str]):
    """
    Passe une chaîne JSON représentant une liste de dictionnaires et retourne une liste formatée.

    Paramètres:
        chaine (str | None): Chaîne JSON à parser.

    Donnée retourné:
        list[str]: Liste de chaînes formatées à partir des dictionnaires.

    Exemple:
        analyse_lite_json('[{"a":1,"b":2}]')  retourne ['a: 1, b: 2']
    """
    try:
        # Si la chaîne est vide ou '[]', retourne une liste vide
        if pd.isna(chaine) or chaine.strip() == '[]':
            return []
        dicts = json.loads(chaine)
        # Vérifie que c'est bien une liste de dictionnaires
        if not isinstance(dicts, list):
            return []
        # Formate chaque dictionnaire en chaîne lisible
        return [", ".join(f"{k}: {v}" for k, v in d.items()) for d in dicts if isinstance(d, dict)]
    except:
        return []

def extraire_donnees_json(df:any, colonnes_a_traiter:any)->any:
    """
    Extrait et déplie les listes de dictionnaires JSON dans les colonnes spécifiées d'un DataFrame.

    Paramètres:
        df (pd.DataFrame): DataFrame source.
        colonnes_a_traiter (list[str]): Colonnes à traiter.

    Donnée retourné:
        pd.DataFrame: DataFrame avec colonnes supplémentaires pour chaque élément extrait.

    Exemple:
        extraire_donnees_json(df, ["colonne_json"]) retourne un DataFrame avec des colonnes supplémentaires pour 
        chaque élément de la liste JSON dans "colonne_json".
    """
    df_resultat = df.copy()
    for col in colonnes_a_traiter:
        # Applique l'analyse JSON sur chaque cellule de la colonne
        listes_format = df_resultat[col].apply(analyse_lite_json)
        max_len = listes_format.apply(len).max()
        # Crée autant de colonnes que le nombre maximum d'éléments trouvés dans les listes
        for i in range(max_len):
            df_resultat[f"{col}_{i+1}"] = listes_format.apply(lambda lst: lst[i] if i < len(lst) else None)
    return df_resultat

def supprimer_colonnes_vides(df:any)->any:
    """
    Supprime les colonnes entièrement vides d'un DataFrame.

    Paramètres:
        df (pd.DataFrame): DataFrame à nettoyer.

    Donnée retournée:
        pd.DataFrame: DataFrame sans colonnes vides.

    Exemple:
        supprimer_colonnes_vides(df) retourne un DataFrame sans colonnes vides.
    """
    return df.dropna(axis=1, how='all')

def choisir_fichier_excel() -> None:
    """
    Objectif :
        Ouvre une boîte de dialogue pour sélectionner un fichier Excel et met à jour l'interface utilisateur avec le fichier choisi.

    Exemple :
        choisir_fichier_excel() ouvre la boîte de dialogue de sélection de fichier et prépare l'interface pour le traitement.
    """
    global nom_fichier_selectionne, chemin_complet_fichier, label_info_fichier, label_statut_traitement, bouton_valider
    # Ouvre une boîte de dialogue pour sélectionner un fichier Excel
    chemin_complet = filedialog.askopenfilename(
        title="Choisir un fichier Excel",
        filetypes=[("Fichiers Excel", "*.xlsx *.xlsm")]
    )

    if chemin_complet:
        # Met à jour les variables et l'interface avec le nom du fichier choisi
        nom_fichier_selectionne = os.path.basename(chemin_complet)
        chemin_complet_fichier = chemin_complet
        label_info_fichier.config(text=f"📁 {nom_fichier_selectionne}")
        bouton_valider.config(state='normal')
        bouton_extraire.config(state="disabled")
        label_statut_traitement.config(text="✅ Fichier prêt à être traité", foreground="#880e4f")
    else:
        nom_fichier_selectionne = None
        chemin_complet_fichier = None
        label_info_fichier.config(text="Aucun fichier sélectionné")
        bouton_valider.config(state='disabled')
        label_statut_traitement.config(text="")

def animer_traitement() -> None:
    """
    Objectif :
        Anime le label de statut pour indiquer le traitement, le téléchargement ou l'envoi en cours.

    Exemple :
        animer_traitement() anime le label de statut en fonction de la phase du traitement.
    """
    global animation_active, animation_id, label_statut_traitement, animation_index, phase_traitement

    if not animation_active:
        return

    # Définit les animations selon la phase du traitement
    if phase_traitement == "traitement":
        animations = [
            "🔄 Traitement en cours", "🔄 Traitement en cours .", "🔄 Traitement en cours . .",
            "🔄 Traitement en cours . . .", "🔄 Traitement en cours . . . .", "🔄 Traitement en cours . . .",
            "🔄 Traitement en cours . .", "🔄 Traitement en cours ."
        ]
        couleur = "#880e4f"
    elif phase_traitement == "fin":
        animations = ["Nettoyage terminé"]
        couleur = "#880e4f"
    elif phase_traitement == "telechargement":
        animations = [
            "🔄 Téléchargement en cours", "🔄 Téléchargement en cours .", "🔄 Téléchargement en cours . .",
            "🔄 Téléchargement en cours . . .", "🔄 Téléchargement en cours . . . .", "🔄 Téléchargement en cours . . .",
            "🔄 Téléchargement en cours . .", "🔄 Téléchargement en cours ."
        ]
        couleur = "#880e4f"
    else:
        animations = [
            "⏫ Import des fichiers sur le dashboard", "⏫ Import des fichiers sur le dashboard .",
            "⏫ Import des fichiers sur le dashboard . .", "⏫ Import des fichiers sur le dashboard . . .",
            "⏫ Import des fichiers sur le dashboard . . . .", "⏫ Import des fichiers sur le dashboard . . .",
            "⏫ Import des fichiers sur le dashboard . .", "⏫ Import des fichiers sur le dashboard ."
        ]
        couleur = "#880e4f"

    # Met à jour le texte du label de statut pour l'animation
    label_statut_traitement.config(text=animations[animation_index], foreground=couleur)
    animation_index = (animation_index + 1) % len(animations)
    animation_id = fenetre_principale.after(500, animer_traitement)

def demarrer_animation()->None:
    """
    Démarre l'animation du label de statut.

    Exemple:
        demarrer_animation() démarre l'animation pour indiquer que le traitement est en cours.
    """
    global animation_active, animation_index
    animation_active = True
    animation_index = 0
    animer_traitement()

def arreter_animation()->None:
    """
    Arrête l'animation du label de statut.

    Exemple:
        arreter_animation() arrête l'animation en cours.
    """
    global animation_active, animation_id
    animation_active = False
    if animation_id:
        fenetre_principale.after_cancel(animation_id)
        animation_id = None

def valider_selection()->None:
    """
    Lance le traitement du fichier sélectionné dans un thread séparé.

    Exemple:
        valider_selection() lance le traitement des données du fichier sélectionné.
    """
    global nom_fichier_selectionne, bouton_valider, bouton_choisir
    if nom_fichier_selectionne:
        bouton_valider.config(state='disabled')
        bouton_choisir.config(state='disabled')
        bouton_dashboard.config(state='disabled')
        bouton_extraire.config(state='disabled')
        bouton_infos_df.config(state='disabled')
        demarrer_animation()
        threading.Thread(target=traitement_donnees, daemon=True).start()

def finaliser_traitement(success:any, message:any, couleur:str="green")->None:
    """
    Finalise le traitement en mettant à jour l'interface selon le succès ou l'échec.

    Paramètres:
        success (bool): Indique si le traitement a réussi.
        message (str): Message à afficher.
        couleur (str): Couleur du texte à afficher (optionnel, défaut: "green").

    Exemple:
        finaliser_traitement(True, "Traitement terminé") affiche "Traitement terminé" en vert.
    """
    global label_statut_traitement, bouton_valider, bouton_choisir
    arreter_animation()
    if success:
        label_statut_traitement.config(text=message, foreground=couleur)
    else:
        label_statut_traitement.config(text="❌ Erreur lors du traitement", foreground="red")
        messagebox.showerror("Erreur", message)
        messagebox.showerror("Erreur", "Erreur lors du traitement : veuillez vérifier le fichier sélectionné.")
    # Réactive tous les boutons
    bouton_valider.config(state='normal')
    bouton_choisir.config(state='normal')
    bouton_dashboard.config(state='normal')
    bouton_extraire.config(state='normal')
    bouton_infos_df.config(state='normal')

def afficher_infos_df_final() -> None:
    """
    Objectif :
        Ouvre une nouvelle fenêtre affichant un aperçu et des informations sur le DataFrame df_final.

    Exemple :
        afficher_infos_df_final() affiche les informations du DataFrame df_final dans une nouvelle fenêtre Tkinter.
    """
    global df_final
    if 'df_final' not in globals() or df_final is None:
        messagebox.showinfo("Information", "Aucune donnée traitée à afficher.")
        return

    fenetre_infos = tk.Toplevel(fenetre_principale)
    fenetre_infos.title("Aperçu des données traitées")
    fenetre_infos.geometry("900x500")
    fenetre_infos.grab_set()

    frame_infos = ttk.Frame(fenetre_infos, padding=10)
    frame_infos.pack(fill='x', anchor='n')

    shape_text = f"Lignes: {df_final.shape[0]}, Colonnes: {df_final.shape[1]}"
    ttk.Label(frame_infos, text=shape_text, font=("Arial", 10, "bold")).pack(anchor='w')

    frame_table = ttk.Frame(fenetre_infos)
    frame_table.pack(fill='both', expand=True)

    colonnes = list(df_final.columns)
    tree = ttk.Treeview(frame_table, columns=colonnes, show='headings', height=20)
    for col in colonnes:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor='center')
    # Affiche les 20 premières lignes du DataFrame
    for _, row in df_final.head(20).iterrows():
        tree.insert('', 'end', values=[row[col] for col in colonnes])
    tree.pack(side='left', fill='both', expand=True)

    scroll_y = ttk.Scrollbar(frame_table, orient='vertical', command=tree.yview)
    scroll_y.pack(side='right', fill='y')
    scroll_x = ttk.Scrollbar(fenetre_infos, orient='horizontal', command=tree.xview)
    scroll_x.pack(fill='x')
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    ttk.Button(fenetre_infos, text="Fermer", command=fenetre_infos.destroy).pack(pady=10)

def creer_fenetre_principale() -> None:
    """
    Objectif :
        Crée et affiche la fenêtre principale de l'application avec tous les widgets et styles.

    Exemple :
        creer_fenetre_principale() crée la fenêtre principale de l'application pour l'analyse de données et la dataviz.
    """
    global fenetre_principale, label_info_fichier, label_statut_traitement, bouton_valider, bouton_choisir, bouton_dashboard, bouton_extraire, bouton_infos_df

    fenetre_principale = tk.Tk()
    fenetre_principale.title("Analyse de données et dataviz - observatoire MaVie")
    fenetre_principale.geometry("800x750")
    fenetre_principale.resizable(True, True)
    fenetre_principale.attributes('-toolwindow', True)

    style = ttk.Style()
    rose_bordure_statut = "#e8d4d5"
    rose_boutons = "#FFB6C1"
    style.configure("TFrame", background="#edc0c1")
    style.configure("TLabel", background="#edc0c1")
    style.configure("TLabelframe", background="#edc0c1")
    style.configure("TButton", background=rose_boutons, foreground="black", font=("Arial", 10, "bold"), width=30, padding=5, anchor="center")
    style.map("TButton", background=[('active', '#D3D3D3'), ('disabled', '#D3D3D3')], foreground=[('active', '#ee5f41'), ('disabled', '#808080')])

    fenetre_principale.grid_columnconfigure(0, weight=1)
    fenetre_principale.grid_rowconfigure(0, weight=1)

    main_frame = ttk.Frame(fenetre_principale, padding="20", style="TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)

    # Chargement des images pour l'interface (logo, boutons, etc.)
    try:
        img_mavie = tk.PhotoImage(file="./outils/mavie.png").subsample(4, 4)
    except:
        img_mavie = None
    try:
        img_sd = tk.PhotoImage(file="./outils/SD.png").subsample(25, 25)
    except:
        img_sd = None

    images_frame = ttk.Frame(main_frame, style="TFrame")
    images_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")
    images_frame.grid_columnconfigure(0, weight=1)
    images_frame.grid_columnconfigure(1, weight=1)

    label_img_mavie = tk.Label(images_frame, image=img_mavie, bg="#edc0c1") if img_mavie else tk.Label(images_frame, text="")
    label_img_mavie.grid(row=0, column=0, padx=10, sticky="w")
    label_img_sd = tk.Label(images_frame, image=img_sd, bg="#edc0c1") if img_sd else tk.Label(images_frame, text="")
    label_img_sd.grid(row=0, column=1, padx=10, sticky="e")
    label_img_mavie.image = img_mavie
    label_img_sd.image = img_sd

    ttk.Label(main_frame, text="Outil dynamique observatoire MaVie", font=("Arial", 20, "bold"), style="TLabel").grid(row=1, column=0, pady=(0, 20))
    ttk.Label(main_frame, text="Sélectionnez un fichier Excel (.xlsx ou .xlsm) à traiter", font=("Arial", 10), style="TLabel").grid(row=2, column=0, pady=(0, 15))

    # Chargement des images pour les boutons
    try:
        img_fichier = tk.PhotoImage(file="./outils/excel.png").subsample(7, 7)
        img_clean = tk.PhotoImage(file="./outils/nettoyer.png").subsample(7, 7)
        img_download = tk.PhotoImage(file="./outils/telecharger.png").subsample(7, 7)
        img_dashboard = tk.PhotoImage(file="./outils/tableaubord.png").subsample(7, 7)
        img_final = tk.PhotoImage(file="./outils/final.png").subsample(7, 7)
    except:
        img_fichier = None
        img_clean = None
        img_download = None
        img_dashboard = None
        img_final = None

    # Création des boutons principaux de l'interface
    boutons_frame = ttk.Frame(main_frame, style="TFrame")
    boutons_frame.grid(row=3, column=0, pady=(0, 20))
    boutons_frame.grid_columnconfigure(0, weight=1)
    boutons_frame.grid_columnconfigure(1, weight=1)

    bouton_choisir = ttk.Button(
        boutons_frame, text="Choisir un fichier Excel", image=img_fichier, compound="left",
        command=choisir_fichier_excel, width=25
    )
    bouton_choisir.grid(row=0, column=0, padx=(0, 10), pady=5)

    label_info_fichier = ttk.Label(main_frame, text="Aucun fichier sélectionné", font=("Arial", 10), foreground="gray", style="TLabel")
    label_info_fichier.grid(row=4, column=0, pady=(0, 15))

    bouton_valider = ttk.Button(
        boutons_frame, text="Nettoyer le fichier", image=img_clean, compound="right",
        command=valider_selection, state='disabled', width=25
    )
    bouton_valider.grid(row=0, column=1, padx=(10, 0), pady=5)

    boutons_frame2 = ttk.Frame(main_frame, style="TFrame")
    boutons_frame2.grid(row=5, column=0, pady=(10, 20))
    boutons_frame2.grid_columnconfigure(0, weight=1)
    boutons_frame2.grid_columnconfigure(1, weight=1)

    bouton_dashboard = ttk.Button(
        boutons_frame2, text="Ouvrir le tableau de bord", image=img_dashboard, compound="left",
        command=lancer_tableau_bord, state='disabled', width=25
    )
    bouton_dashboard.grid(row=0, column=0, padx=(0, 10), pady=5)

    bouton_extraire = ttk.Button(
        boutons_frame2, text="Télécharger le fichier", image=img_download, compound="right",
        command=lambda: extraire_donnees_nettoyees_wrapper(), state='disabled', width=25
    )
    bouton_extraire.grid(row=0, column=1, padx=(10, 0), pady=5)

    boutons_frame3 = ttk.Frame(main_frame, style="TFrame")
    boutons_frame3.grid(row=6, column=0, pady=(10, 20))
    boutons_frame3.grid_columnconfigure(0, weight=1)
    boutons_frame3.grid_columnconfigure(1, weight=1)

    bouton_infos_df = ttk.Button(
        boutons_frame3, text="Voir les données traitées", image=img_final, compound="left",
        command=afficher_infos_df_final, state='disabled', width=25
    )
    bouton_infos_df.grid()

    ttk.Separator(main_frame, orient='horizontal').grid(row=7, column=0, sticky="ew", pady=(0, 15))

    status_border_frame = tk.Frame(main_frame, background=rose_bordure_statut)
    status_border_frame.grid(row=8, column=0, sticky="ew", pady=(0, 10))
    status_border_frame.grid_columnconfigure(0, weight=1)
    status_border_frame.grid_rowconfigure(0, weight=1)

    statut_frame = tk.LabelFrame(
        status_border_frame, text="Statut", bg=rose_bordure_statut, fg="#000",
        font=("Arial", 10, "bold"), labelanchor="nw", bd=0, highlightthickness=0, padx=0, pady=0
    )
    statut_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    statut_frame.grid_columnconfigure(0, weight=1)

    global label_statut_traitement
    label_statut_traitement = tk.Label(
        statut_frame, text="En attente de sélection de fichier...", font=("Arial", 10),
        fg="#880e4f", bg=rose_bordure_statut, anchor="center"
    )
    label_statut_traitement.grid(row=0, column=0, sticky="nsew")

    info_frame = ttk.Frame(main_frame, style="TFrame")
    info_frame.grid(row=9, column=0, sticky="ew", pady=(10, 0))
    info_frame.grid_columnconfigure(0, weight=1)
    ttk.Label(
        info_frame, text="Le traitement peut prendre quelques minutes selon la taille du fichier.",
        font=("Arial", 8), foreground="gray", style="TLabel"
    ).grid(row=0, column=0)

    fenetre_principale.mainloop()

def traitement_donnees() -> None:
    """
    Objectif :
        Effectue le traitement principal : lecture, nettoyage, fusion, et envoi des données vers BigQuery.

    Paramètres :
        Aucun

    Donnée retournée :
        None

    Exemple :
        traitement_donnees()
    """
    global df1, df2, df_final
    try:
        key_path = "./outils/mavie-bigquery.json"
        # Vérifie que la clé d'API BigQuery existe
        if not os.path.exists(key_path):
            finaliser_traitement(False, "Clé BigQuery manquante.")
            return

        credentials = service_account.Credentials.from_service_account_file(key_path)
        fichier_excel = chemin_complet_fichier

        # Lecture des deux feuilles du fichier Excel
        df1 = pd.read_excel(fichier_excel, sheet_name=0)
        df2 = pd.read_excel(fichier_excel, sheet_name=1)

        # Nettoyage et renommage des colonnes
        df2 = df2.drop(columns=["Colonne1"], errors='ignore')
        df2.columns = [
            "id_volontaire", "annee_naissance", "genre", "date_remplissage", "a_eu_accident_recemment", "date_accident",
            "heure_accident", "tiers_responsable", "etat_fatigue_accident", "code_postal_accident", "commune_accident",
            "lieu_accident", "prec_lieu_accident_1", "prec_lieu_accident_2", "prec_lieu_accident_3", "prec_lieu_accident_4",
            "prec_lieu_accident_5", "prec_lieu_accident_6", "prec_lieu_accident_7", "prec_lieu_accident_8",
            "prec_lieu_accident_9", "prec_lieu_accident_10", "activite_au_moment_accident", "prec_activite_1",
            "prec_activite_10", "prec_activite_11", "prec_activite_12", "prec_activite_13", "prec_activite_14",
            "sport_pratique_accident", "prec_sport_1", "prec_sport_15", "prec_sport_16", "prec_sport_17", "prec_sport_18",
            "prec_sport_19", "prec_sport_20", "prec_sport_21", "prec_sport_22", "prec_sport_23", "prec_sport_24",
            "prec_sport_25", "prec_sport_26", "prec_sport_27", "prec_sport_28", "prec_sport_29", "type_accident",
            "direction_chute", "origine_chute", "cause_allergie_intoxication", "moment_surmenage", "a_blessure",
            "types_blessures", "a_recu_soins", "auteur_soins", "jours_hospitalisation", "hospitalisation_encours",
            "arret_travail", "jours_arret_travail", "arret_travail_encours", "limitation_activites_48h", "arret_sport",
            "duree_arret_sport", "arret_sport_encours", "description_accident"
        ]
        df1.columns = [
            "id_volontaire", "annee_naissance", "genre", "date_remplissage", "lieu_naissance", "pays_naissance",
            "age_arrivee_france", "situation_emploi", "profession_actuelle", "diplome_plus_eleve", "activites_pratiquees",
            "a_pratique_activite_physique", "activites_sportives", "situation_familiale", "poids_kg", "taille_cm",
            "sante_physique_score", "sante_mentale_score", "a_eu_accident_12mois", "types_accidents", "handicap",
            "difficultes_mouvement_1", "difficultes_mouvement_2", "difficultes_mouvement_3", "difficultes_mouvement_4",
            "difficultes_mouvement_5", "difficultes_mouvement_6", "fumeur_ou_non", "frequence_cig",
            "a_consomme_cannabis_30j", "frequence_cannabis_30j", "frequence_alcool", "verres_typiques_alcool",
            "frequence_alcool_forte_dose", "date_remplissage_foyer", "nb_personnes_foyer", "mode_vie",
            "personnes_foyer", "revenu_mensuel_net", "animaux_domestiques", "race_chien", "code_postal", "commune",
            "zone_residence", "type_voisinage", "type_habitation", "statut_occupation_logement", "etage_habitation",
            "nb_etages_logement", "surface_logement", "surface_logement_precise", "nb_pieces_logement",
            "escaliers_interieur", "escaliers_exterieur", "a_grenier", "a_cave", "a_balcon", "type_chauffage_principal",
            "sources_energie_chauffage", "appareils_chauffage", "detecteur_fumee", "detecteur_monoxyde", "extincteur",
            "garage_box", "espace_exterieur", "surface_espace_exterieur", "surface_espace_exterieur_precise",
            "abri_jardin", "presence_eau_ou_piscine"
        ]

        # Nettoyage des retours à la ligne dans les colonnes texte
        for col in df1.columns:
            if df1[col].dtype == 'object':
                df1[col] = df1[col].apply(nettoyer_retours_ligne)
        for col in df2.columns:
            if df2[col].dtype == 'object':
                df2[col] = df2[col].apply(nettoyer_retours_ligne)

        # Extraction et conversion de l'année de naissance
        df1["annee_naissance"] = df1["annee_naissance"].apply(extraire_annee)
        df2["annee_naissance"] = df2["annee_naissance"].apply(extraire_annee)

        # Traitement de la taille
        df1["taille_cm"] = df1["taille_cm"].apply(traiter_taille)

        # Nettoyage des colonnes numériques
        df1 = nettoyer_colonnes_numeriques(df1, [
            'age_arrivee_france', 'poids_kg', 'taille_cm', 'sante_physique_score', 'sante_mentale_score',
            'frequence_cig', 'frequence_cannabis_30j', 'nb_personnes_foyer', 'code_postal', 'nb_etages_logement',
            'surface_logement_precise', 'nb_pieces_logement', 'surface_espace_exterieur_precise'
        ])
        df2 = nettoyer_colonnes_numeriques(df2, ['code_postal', 'jours_arret_travail', 'duree_arret_sport'])

        # Création de colonnes booléennes pour chaque activité possible
        activites_possibles = [
            "Activités avec un écran (télévision, ordi+C40:C51", "Lecture (roman, magazine, BD, …)", "Jeu intérieur",
            "Jeu extérieur", "Jardinage", "Bricolage", "Activités ménagères (Lessive, repassage, entretien, cuisine)",
            "Sorties (cinéma, bar, restaurant, shopping, …)", "Activités artistiques (musique, peinture, sculpture, dessin, photographie …)",
            "Activités manuelles (couture, tricot, broderie, …)", "Activité sportive (marche, vélo, sport individuel, sport collectif, …)",
            "Autre activité (précisez)", "Aucune activité"
        ]
        for activite in activites_possibles:
            df1[activite] = df1['activites_pratiquees'].fillna('').apply(lambda x: "oui" if activite in str(x) else "non")

        # Création de colonnes booléennes pour chaque type de handicap possible
        handicaps_possibles = [
            "Aucune", "Qui empêche ou limite ou rend difficile vos déplacements ?", "De vision",
            "De vision des couleurs (daltonisme)", "D'audition", "Mentale, intellectuelle ou psychologique",
            "Une (ou plusieurs) autre(s) déficience(s) (précisez)"
        ]
        for handi in handicaps_possibles:
            nom = "handicap " + handi
            df1[nom] = df1['handicap'].fillna('').apply(lambda x: "oui" if handi in str(x) else "non")

        # Extraction des données JSON dans certaines colonnes
        df1 = extraire_donnees_json(df1, ["activites_sportives", "personnes_foyer", "types_accidents"])
        df2 = extraire_donnees_json(df2, ["types_blessures", "type_accident"])

        # Renommage des colonnes pour plus de clarté
        df1 = df1.rename(columns={
            'Activités avec un écran (télévision, ordi+C40:C51': 'activites_ecran',
            'Lecture (roman, magazine, BD, …)': 'lecture',
            'Jeu intérieur': 'jeu_interieur',
            'Jeu extérieur': 'jeu_exterieur',
            'Activités ménagères (Lessive, repassage, entretien, cuisine)': 'activites_menageres',
            'Sorties (cinéma, bar, restaurant, shopping, …)': 'sorties',
            'Activités artistiques (musique, peinture, sculpture, dessin, photographie …)': 'activites_artistiques',
            'Activités manuelles (couture, tricot, broderie, …)': 'activites_manuelles',
            'Activité sportive (marche, vélo, sport individuel, sport collectif, …)': 'activites_sport',
            'Autre activité (précisez)': 'activites_autres',
            'Aucune activité': 'aucune_act'
        })
        df1 = df1.rename(columns={
            'handicap Qui empêche ou limite ou rend difficile vos déplacements ?': 'empeche_dep',
            'handicap De vision': 'vision',
            'handicap De vision des couleurs (daltonisme)': 'vision_couleurs_daltonisme',
            'handicap Mentale, intellectuelle ou psychologique': 'mentale',
            'handicap Une (ou plusieurs) autre(s) déficience(s) (précisez)': 'autre_deficience'
        })

        # Suppression des colonnes vides
        df1 = supprimer_colonnes_vides(df1)
        df2 = supprimer_colonnes_vides(df2)

        # Suppression des colonnes inutiles après extraction JSON
        df1 = df1.drop(columns=["activites_sportives", "personnes_foyer", "types_accidents", "activites_pratiquees", "handicap"])
        df2 = df2.drop(columns=["type_accident", "types_blessures"])

        # Fusion des deux DataFrames sur la colonne id_volontaire
        colonnes_communes = df1.columns.intersection(df2.columns).difference(['id_volontaire'])
        df2_sans_doublons = df2.drop(columns=colonnes_communes)
        df_final = pd.merge(df1, df2_sans_doublons, on='id_volontaire', how='inner')

        # Nettoyage final des retours à la ligne
        for col in df_final.columns:
            if df_final[col].dtype == 'object':
                df_final[col] = df_final[col].apply(nettoyer_retours_ligne)

        global phase_traitement
        phase_traitement = "envoi"
        fenetre_principale.after(0, animer_traitement)

        # Envoi des données vers BigQuery
        to_gbq(df1, "mon_dataset.bdquest", project_id=credentials.project_id, if_exists="replace", credentials=credentials)
        to_gbq(df2, "mon_dataset.accidents", project_id=credentials.project_id, if_exists="replace", credentials=credentials)
        to_gbq(df_final, "mon_dataset.mavie", project_id=credentials.project_id, if_exists="replace", credentials=credentials)

        finaliser_traitement(True, "✅ Traitement terminé et données envoyées !", couleur="#880e4f")
    except Exception as e:
        finaliser_traitement(False, str(e))

# Point d'entrée principal du programme
if __name__ == "__main__":
    # Liste des modules nécessaires à l'exécution du programme
    modules_requis = ["pandas", "pandas_gbq", "scipy", "google-auth", "openpyxl"]
    nb_modules = len(modules_requis)

    # Affichage de la fenêtre d'installation des modules
    fenetre_install, barre_install, label_install = afficher_fenetre_installation(nb_modules)
    for i, module in enumerate(modules_requis, 1):
        installer_si_absent(module)
        pourcentage = int(i * 100 / nb_modules)
        barre_install['value'] = pourcentage
        label_install.config(text=f"{pourcentage}% terminé")
        fenetre_install.update()

    # Import des modules après installation
    import pandas as pd
    from google.oauth2 import service_account
    from pandas_gbq import to_gbq

    fenetre_install.destroy()

    # Initialisation des variables globales
    nom_fichier_selectionne = None
    chemin_complet_fichier = None
    fenetre_principale = None
    label_info_fichier = None
    label_statut_traitement = None
    bouton_valider = None
    bouton_choisir = None
    animation_active = False
    animation_id = None
    animation_index = 0
    phase_traitement = "traitement"

    # Lancement de l'interface principale
    creer_fenetre_principale()