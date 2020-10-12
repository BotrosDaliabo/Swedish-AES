import re

def clear_parenthesis(text):
    """
    Funktionen tar bort text inom parenteser och parenteser då sådan text vanligtvis har liten betydelse för texten eller är referenser. I vissa fall
    finns förkortningar i. Tar även bort kolon, t.ex. 25:th of may blir 25th May, detta görs för att undvika att grammatikkontrollen flaggar fel.
    """
    return re.sub(r"\s\(.*?\)+", '', text)


def correct_possessive_pronouns(text):
    """
    Korrigerar felaktig inläsning av 's, t.ex it's istället för itâs
    """
    return re.sub(r"[â]+", '\'', text)

#en funktion som mäter känneteckens korrelation till andra kännetecken
def calculate_correlation(kappa_values: Dict):
    #df = pd.DataFrame([kappa_values])
    #implementering av Pearsons korrelaiontenstestet
    #for idx in range(len(kappa_values)):
    df = pd.DataFrame().from_dict(kappa_values, orient='index').T
    #    df[key] =df[key].astype({key:'str'}).dtypes
    print(df.corr(method='pearson'))
        #df[df.columns[0:]].corr()[key][:]


def start_experiment() -> tuple:
    SVM_kappas: List[float] = []
    LDAC_kappas = []
    features = Feature.__members__.values()
    features_list: List[Feature] = list(features)
    #features_str = [feature.name for feature in features_list]
    #labels_transformed = LabelEncoder().fit_transform(features_str)
    print("Training the feature: %s, %s, %s" % (Feature.no_of_tokens.name, Feature.no_of_sentences.name, Feature.no_of_nouns.name))
    SVM_grades = (predict_in_svm(essay_collection, [Feature.fourth_root_words, Feature.NR, Feature.no_of_sentences], grade_dict))
    #LDAC_grades = (predict_in_ldac(essay_collection, [features_list[index]], grade_dict))
    SVM_kappas.append(calculate_kappa(grade_dict, SVM_grades))
    print("Kappa: %f" % SVM_kappas[len(SVM_kappas)-1])
    #LDAC_kappas.append(calculate_kappa(grade_dict, LDAC_grades))

    return (SVM_kappas, LDAC_kappas)

"""
def pdf_to_text(pdfname):
    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    device = TextConverter(rsrcmgr, sio, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
      # get text from file
    fp = open(pdfname, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()
      # Get text from StringIO
    text = sio.getvalue()
      # close objects
    device.close()
    sio.close()

    return text
"""

"""
    # trännar i svmClassifier
    print("Training the SVM classifier")
    essays = []
    for essay in essay_collection:
        essays.append(essay[Feature.OVIX])

    array = np.arange(24, dtype=float).reshape(24, 1)
    row = 0
    for essay2 in essay_collection:

        col = 0
        for i in range(1, 2) :
            array[row][col] = essay2[Feature.OVIX]
            col += 1
            row += 1
    for a in array:
        print(array)
    trained_svm = train_svm(essays,1)
    prediction = trained_svm.predict(array)
    print(prediction)
    """

