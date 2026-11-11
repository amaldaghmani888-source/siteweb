from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, json, os
from datetime import date

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
app.jinja_env.filters["fromjson"] = json.loads
DB = os.path.join(os.path.dirname(__file__), "carnet_femme.db")

SECTIONS = {
"identite":{"title":"Informations concernant la femme","ar":"معلومات المرأة","fields":[
("date_naissance","Date de naissance","تاريخ الميلاد","date"),("nationalite","Nationalité","الجنسية","text"),("cin","N° CIN","رقم البطاقة الوطنية","text"),("instruction","Niveau d’instruction","المستوى الدراسي","text"),("profession","Occupation","المهنة","text"),("telephone","Téléphone","الهاتف","tel"),("contact_urgence","Personne à contacter en cas d’urgence","شخص للاتصال به في حالة الطوارئ","text"),("medecin","Médecin traitant","الطبيب المعالج","text"),("groupe_sanguin","Groupe sanguin","فصيلة الدم","select:A,B,AB,O"),("rhesus","Rhésus","عامل ريسوس","select:Positif,Négatif"),("allergies","Allergies / traitement suivi","الحساسية / العلاج الحالي","textarea"),("antecedents","Antécédents médicaux et chirurgicaux","السوابق الطبية والجراحية","textarea"),("antecedents_familiaux","Antécédents familiaux","السوابق العائلية","textarea"),("couverture","Couverture médicale (AMO, RAMED, autre)","التغطية الصحية","text")]},
"vaccination":{"title":"Statut vaccinal","ar":"التلقيح","fields":[("vaccin","Vaccin","اللقاح","select:Antitétanique 1,Antitétanique 2,Antitétanique 3,Antitétanique 4,Antitétanique 5,Rubéole,Autre"),("date","Date d’administration","تاريخ التلقيح","date"),("dose","N° de prise / dose","رقم الجرعة","text"),("lieu","Lieu de vaccination","مكان التلقيح","text"),("prestataire","Prestataire","المهني الصحي","text"),("notes","Observations","ملاحظات","textarea")]},
"prenuptial":{"title":"Examen prénuptial","ar":"الفحص قبل الزواج","fields":[("date","Date de l’examen","تاريخ الفحص","date"),("clinique","Résultats de l’examen clinique","نتائج الفحص السريري","textarea"),("paraclinique","Résultats des examens complémentaires","نتائج الفحوصات التكميلية","textarea"),("medecin","Médecin / cachet","الطبيب / الخاتم","text")]},
"planification":{"title":"Planification familiale","ar":"تنظيم الأسرة","fields":[("date","Date de la visite","تاريخ الزيارة","date"),("methode","Méthode contraceptive utilisée","وسيلة منع الحمل المستعملة","text"),("examen","Synthèse de l’examen clinique","ملخص الفحص السريري","textarea"),("decision","Décisions prises","القرارات المتخذة","textarea"),("prestataire","Nom du prestataire","اسم المهني الصحي","text")]},
"grossesse":{"title":"Suivi de la grossesse","ar":"تتبع الحمل","fields":[("numero","N° de grossesse","رقم الحمل","select:1,2,3,4,5,6+"),("date_regles","Date des dernières règles","تاريخ آخر دورة شهرية","date"),("date_probable","Date probable de l’accouchement","التاريخ المتوقع للولادة","date"),("date_visite","Date de la visite","تاريخ الزيارة","date"),("age_sa","Âge de grossesse (SA)","عمر الحمل بالأسابيع","text"),("poids","Poids (kg)","الوزن (كلغ)","number"),("ta","Tension artérielle","ضغط الدم","text"),("sucre","Sucre","السكر","text"),("albumine","Albumine","الألبومين","text"),("hemoglobine","Hémoglobine","الهيموغلوبين","text"),("bcf","BCF","نبض قلب الجنين","text"),("hu","H.U","ارتفاع الرحم","text"),("clinique","Synthèse clinique","ملخص سريري","textarea"),("biologie","Examens biologiques","الفحوصات البيولوجية","textarea"),("echo","Examens échographiques / radiologiques","الفحوصات بالصدى / الأشعة","textarea"),("fer","Supplémentation en fer","مكملات الحديد","text"),("vitamine_d","Supplémentation en vitamine D","فيتامين د","text"),("decision","Décision prise","القرار المتخذ","textarea"),("etablissement","Établissement sanitaire","المؤسسة الصحية","text"),("prestataire","Prestataire","المهني الصحي","text")]},
"accouchement":{"title":"Accouchement et post-partum","ar":"الولادة وما بعد الولادة","fields":[("date","Date de l’accouchement","تاريخ الولادة","date"),("lieu","Lieu","المكان","text"),("mode","Mode","طريقة الولادة","select:Voie basse,Voie haute"),("complications","Complications","المضاعفات","textarea"),("nouveau_ne","État du nouveau-né","حالة المولود","select:Vivant,Mort-né,Décès inférieur à 24 h"),("poids","Poids du nouveau-né (g)","وزن المولود (غرام)","number"),("anti_d","Immunoglobuline humaine ANTI-D","مضاد D","select:Oui,Non,Non concernée"),("consultations","Consultations post-natales (sortie, J8, J40)","استشارات ما بعد الولادة","textarea"),("observations","Observations / conseils","ملاحظات / نصائح","textarea")]},
"cancers":{"title":"Dépistage des cancers du sein et du col de l’utérus","ar":"الكشف المبكر عن سرطان الثدي وعنق الرحم","fields":[("type","Type de dépistage","نوع الكشف","select:Cancer du sein,Cancer du col de l’utérus"),("date","Date du dépistage","تاريخ الكشف","date"),("resultat","Résultat du test de dépistage","نتيجة الفحص","textarea"),("examens","Examens complémentaires","فحوصات تكميلية","textarea"),("decision","Décisions ou traitements prescrits","القرارات أو العلاجات الموصوفة","textarea"),("prestataire","Nom du prestataire de soins","اسم مقدم الرعاية","text"),("prochain","Date du prochain contrôle","تاريخ المراقبة المقبلة","date")]},
"consultations":{"title":"Synthèse des consultations médicales","ar":"ملخص الاستشارات الطبية","fields":[("date","Date","التاريخ","date"),("examens","Synthèse des examens cliniques et paracliniques","ملخص الفحوصات السريرية والتكميلية","textarea"),("traitement","Traitement et décisions prises","العلاج والقرارات المتخذة","textarea"),("medecin","Médecin / cachet","الطبيب / الخاتم","text")]},
"chirurgie":{"title":"Interventions chirurgicales","ar":"العمليات الجراحية","fields":[("date","Date","التاريخ","date"),("diagnostic","Diagnostic","التشخيص","textarea"),("type","Type d’intervention","نوع العملية","text"),("lieu","Lieu d’intervention","مكان العملية","text"),("medecin","Médecin traitant","الطبيب المعالج","text"),("evolution","Évolution","التطور الصحي","textarea")]},
"chroniques":{"title":"Maladies chroniques","ar":"الأمراض المزمنة","fields":[("date","Date du rendez-vous","تاريخ الموعد","date"),("examens","Synthèse des examens cliniques et paracliniques","ملخص الفحوصات","textarea"),("traitement","Traitement","العلاج","textarea"),("medecin","Médecin","الطبيب","text")]},
"menopause":{"title":"Suivi de la ménopause","ar":"تتبع سن اليأس","fields":[("pre_menopause","Date d’apparition de la pré-ménopause","تاريخ بداية ما قبل انقطاع الطمث","date"),("menopause","Date d’apparition de la ménopause","تاريخ انقطاع الطمث","date"),("date","Date de consultation","تاريخ الاستشارة","date"),("manifestations","Manifestations cliniques","الأعراض السريرية","textarea"),("examens","Examens complémentaires","الفحوصات التكميلية","textarea"),("traitement","Traitement","العلاج","textarea")]}
}
T={
"fr":{"app":"Carnet de santé de la femme","subtitle":"Votre santé, à chaque étape de la vie","woman":"Espace des femmes","staff":"Espace des professionnels de santé","woman_desc":"Consulter et compléter votre carnet personnel, suivre vos rendez-vous et votre prévention.","staff_desc":"Accéder à une vue de suivi, consulter les volumes d’activité et les indicateurs enregistrés.","enter":"Accéder à cet espace","language":"Langue","home":"Accueil","back":"Changer d’espace","profile":"Mon profil","history":"Historique du carnet","new":"Nouvelle entrée","save":"Enregistrer","add":"Ajouter au carnet","delete":"Supprimer","empty":"Aucune entrée pour le moment","records":"Enregistrements","vaccines":"Suivi vaccinal","preg":"Suivi de grossesse","screen":"Dépistages","consult":"Consultations","activity":"Activité enregistrée","indicator_note":"Indicateurs calculés à partir des entrées enregistrées dans cette installation. Ils ne représentent pas une couverture populationnelle sans dénominateur validé.","module":"Rubriques du carnet","privacy":"Les données de santé sont confidentielles. Accès réservé aux personnes autorisées.","welcome":"Bienvenue","intro":"Un espace numérique pour organiser le suivi de santé de la femme.","personal":"Espace personnel","staffview":"Espace professionnel","no_data":"Aucune donnée enregistrée","save_profile":"Enregistrer la fiche","date":"Date d’enregistrement","details":"Détails","women":"Bénéficiaires suivies*","countnote":"*Le carnet actuel stocke un dossier local unique. Le multi-dossier nominatif nécessite une authentification et une base sécurisée."},
"ar":{"app":"الدفتر الصحي للمرأة","subtitle":"صحتك في كل مراحل الحياة","woman":"فضاء النساء","staff":"فضاء مهنيي الصحة","woman_desc":"الاطلاع على الدفتر الصحي الشخصي وتحيينه وتتبع المواعيد والوقاية.","staff_desc":"الاطلاع على مؤشرات التتبع وحجم الأنشطة والتسجيلات المتاحة.","enter":"الدخول إلى هذا الفضاء","language":"اللغة","home":"الرئيسية","back":"تغيير الفضاء","profile":"ملفي الشخصي","history":"السجل الصحي","new":"إضافة معلومات جديدة","save":"حفظ","add":"إضافة إلى الدفتر","delete":"حذف","empty":"لا توجد معلومات مسجلة حاليا","records":"التسجيلات","vaccines":"التلقيح","preg":"تتبع الحمل","screen":"الكشف المبكر","consult":"الاستشارات","activity":"النشاط المسجل","indicator_note":"المؤشرات محسوبة انطلاقا من التسجيلات الموجودة في هذه النسخة. لا تمثل التغطية السكانية دون مقام إحصائي معتمد.","module":"أقسام الدفتر","privacy":"المعطيات الصحية سرية. الولوج مقتصر على الأشخاص المرخص لهم.","welcome":"مرحبا بكم","intro":"فضاء رقمي لتنظيم وتتبع صحة المرأة.","personal":"الفضاء الشخصي","staffview":"الفضاء المهني","no_data":"لا توجد بيانات مسجلة","save_profile":"حفظ المعلومات","date":"تاريخ التسجيل","details":"التفاصيل","women":"المستفيدات المتتبعات*","countnote":"*تخزن النسخة الحالية ملفا محليا واحدا. يتطلب تدبير عدة ملفات بأسماء أصحابها نظام مصادقة وقاعدة بيانات مؤمنة."}
}
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 with db() as c:
  c.execute("CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1),nom TEXT,prenom TEXT,date_ouverture TEXT,adresse TEXT,telephone TEXT)")
  c.execute("CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY AUTOINCREMENT,section TEXT NOT NULL,payload TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
  c.execute("INSERT OR IGNORE INTO profile(id) VALUES(1)")
@app.context_processor
def inject():
 lang=session.get("lang","fr"); return {"lang":lang,"t":T[lang],"rtl":lang=="ar"}
@app.get("/")
def index():
 init_db()
 lang=request.args.get("lang")
 if lang in T: session["lang"]=lang
 return render_template("index.html",mode="landing",sections=SECTIONS)
@app.get("/space/<role>")
def space(role):
 if role not in ("woman","staff"): return redirect(url_for("index"))
 init_db()
 active=request.args.get("section","identite")
 if active not in SECTIONS: active="identite"
 with db() as c:
  profile=c.execute("SELECT * FROM profile WHERE id=1").fetchone()
  records=c.execute("SELECT * FROM records ORDER BY created_at DESC").fetchall()
 counts={k:sum(1 for r in records if r["section"]==k) for k in SECTIONS}
 total=len(records)
 stats={"total":total,"vaccination":counts["vaccination"],"grossesse":counts["grossesse"],"cancers":counts["cancers"],"consultations":counts["consultations"]}
 return render_template("index.html",mode=role,sections=SECTIONS,profile=profile,records=records,counts=counts,active=active,stats=stats)
@app.get("/language/<lang>")
def language(lang):
 if lang in T: session["lang"]=lang
 return redirect(request.referrer or url_for("index"))
@app.post("/profile")
def save_profile():
 vals=[request.form.get(k,"").strip() for k in ("nom","prenom","date_ouverture","adresse","telephone")]
 with db() as c: c.execute("UPDATE profile SET nom=?,prenom=?,date_ouverture=?,adresse=?,telephone=? WHERE id=1",vals)
 flash("Fiche enregistrée." if session.get("lang","fr")=="fr" else "تم حفظ المعلومات.")
 return redirect(url_for("space",role="woman",section="identite"))
@app.post("/add/<section>")
def add_record(section):
 if section not in SECTIONS: return redirect(url_for("space",role="woman"))
 payload={f[0]:request.form.get(f[0],"").strip() for f in SECTIONS[section]["fields"]}
 if not any(payload.values()):
  flash("Veuillez renseigner au moins un champ." if session.get("lang","fr")=="fr" else "يرجى إدخال معلومة واحدة على الأقل.")
  return redirect(url_for("space",role=request.form.get("role","woman"),section=section))
 with db() as c: c.execute("INSERT INTO records(section,payload) VALUES(?,?)",(section,json.dumps(payload,ensure_ascii=False)))
 flash("Information ajoutée." if session.get("lang","fr")=="fr" else "تمت إضافة المعلومات.")
 return redirect(url_for("space",role=request.form.get("role","woman"),section=section))
@app.post("/delete/<int:record_id>")
def delete_record(record_id):
 with db() as c: c.execute("DELETE FROM records WHERE id=?",(record_id,))
 return redirect(url_for("space",role="woman"))
if __name__=="__main__":
 init_db(); app.run(debug=False)
