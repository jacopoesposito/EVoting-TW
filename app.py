from flask import Flask, render_template, request, flash, redirect, url_for, g, session
from flask_bootstrap import Bootstrap
from db import engine, Users, Lista, Candidato, Elezioni, Voto, conteggio_voti_c, conteggio_voti_l
from sqlalchemy.orm import sessionmaker, query
from flask_wtf.csrf import CSRFProtect
import hashlib, uuid, os
from base64 import b64encode
from datetime import datetime, timedelta

app = Flask(__name__)
Bootstrap(app)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '9b94a3ade9e1593d388c93cf72e25985'
checkLogin = False


@app.route('/')
def index():
    #if session.get('user') == True:
        print(session['user'])
        g.user = Users.get_user_by_id(session['user'])
        print(g.user.ADMIN)

        elezioni_list = ritornaElelezioni()
        return render_template('index.html', elezioni_list=elezioni_list)
    #else:
        #return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html', message='')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', message='')


@app.route('/inserisciCandidato/<message>', methods=['GET', 'POST'])
def inserisciCandidato(message):
    user = Users.get_user_by_id(session['user'])
    g.user = user
    Session = sessionmaker(bind=engine)
    sessione = Session()
    users_list = sessione.query(Users).all()
    liste_list = sessione.query(Lista).all()

    for u in liste_list:
        print(u.NOME_LISTA)
    return render_template('inserisciCandidato.html', message=message, user_list=users_list, liste_list=liste_list)


@app.route('/inserisciLista/<message>', methods=['GET', 'POST'])
def inserisciLista(message):
    print(session['user'])
    user = Users.get_user_by_id(session['user'])
    print(user.ADMIN)
    g.user = user
    print(g.user.NOME)
    return render_template('inserisciLista.html', message=message)


@app.route('/inserisciElezione/<message>', methods=['GET', 'POST'])
def inserisciElezione(message):
    user = Users.get_user_by_id(session['user'])
    g.user = user
    return render_template('inserisciElezione.html', message=message)


@app.route('/presentaCandidatoElezione/<message>', methods=['GET', 'POST'])
def presentaCandidatoElezione(message):
    user = Users.get_user_by_id(session['user'])
    g.user = user
    Session = sessionmaker(bind=engine)
    sessione = Session()
    candidato_list = sessione.query(Candidato, Users).filter(Candidato.FK_ID_UTENTE == Users.CODICE_UTENTE) #JOIN
    liste_list = sessione.query(Lista).all()
    elezione_list = sessione.query(Elezioni).all()

    return render_template('inserisciCandidatoElezione.html', message=message, candidato_list=candidato_list, liste_list=liste_list, elezione_list=elezione_list)


@app.route('/presentaListaElezione/<message>', methods=['GET', 'POST'])
def presentaListaElezione(message):
    user = Users.get_user_by_id(session['user'])
    g.user = user
    Session = sessionmaker(bind=engine)
    sessione = Session()
    liste_list = sessione.query(Lista).all()
    elezione_list = sessione.query(Elezioni).all()

    return render_template('inserisciListaElezione.html', message=message, liste_list=liste_list, elezione_list=elezione_list)

@app.route('/elezione/<id_elezione>', methods=['GET', 'POST'])
def elezione(id_elezione):
    user = Users.get_user_by_id(session['user'])
    g.user = user

    Session = sessionmaker(bind=engine)
    sessione = Session()
    g.elezione=Elezioni.get_elezione_by_id(id_elezione)
    session['elezione'] = g.elezione.ID_ELEZIONE
    present = datetime.now()
    if g.elezione.DATA_IN <= present <= g.elezione.DATA_FIN:
        candidati=sessione.query(Candidato, Users.NOME, Users.COGNOME, Users.CODICE_UTENTE, conteggio_voti_c).distinct().filter(conteggio_voti_c.FK_ID_CANDIDATO == Candidato.ID_CANDIDATO).filter(Candidato.FK_ID_UTENTE == Users.CODICE_UTENTE).filter(conteggio_voti_c.FK_ID_ELEZIONE == id_elezione)
        liste=sessione.query(Lista, conteggio_voti_l).distinct().filter(conteggio_voti_l.FK_ID_LISTA == Lista.ID_LISTA, conteggio_voti_l.FK_ID_ELEZIONE == id_elezione)
        print(candidati)
        return render_template("elezione.html", candidati=candidati, liste=liste)
    elif g.elezione.DATA_FIN < present:
        candidati=sessione.query(Candidato, Users.NOME, Users.COGNOME, conteggio_voti_c).distinct().filter(conteggio_voti_c.FK_ID_CANDIDATO == Candidato.ID_CANDIDATO).filter(Candidato.FK_ID_UTENTE == Users.CODICE_UTENTE).filter(conteggio_voti_c.FK_ID_ELEZIONE == id_elezione)
        liste=sessione.query(Lista, conteggio_voti_l).distinct().filter(conteggio_voti_l.FK_ID_LISTA == Lista.ID_LISTA, conteggio_voti_l.FK_ID_ELEZIONE == id_elezione)
        return render_template("elezioneFinita.html",  candidati=candidati, liste=liste)
    else:
        return render_template("elezioneNonIniziata.html")



@app.route('/input', methods=['GET', 'POST'])
def insertUser():

    print("ciao")

    if request.method == 'POST':
        message = ''
        email = request.values.get("inputEmail")
        nome = request.values.get("nome")
        cognome = request.values.get("cognome")
        password = request.values.get("inputPassword")
        reInputPass = request.values.get("reInputPassword")
        date = request.values.get("date")
        print(nome + cognome + email + password + reInputPass + date)
    if email and nome and cognome and password and reInputPass and date:
        if not checkEmail(email):
            if password == reInputPass:
                codice_utente = str(uuid.uuid4())
                randomBytes = os.urandom(32)
                salt = b64encode(randomBytes).decode('utf-8')
                print(len(salt))
                print(salt)
                hashedPassword = str(hashlib.sha512((password + salt).encode('utf-8')).hexdigest())
                newUser = Users(CODICE_UTENTE=codice_utente, EMAIL=email, NOME=nome, COGNOME=cognome, PASSWORD=hashedPassword, DN=date, SALT=salt)
                Session = sessionmaker(bind=engine)
                session = Session()
                session.add(newUser)
                session.commit()
                elezioni_list = ritornaElelezioni()
                return render_template("login.html", elezioni_list=elezioni_list)
            else:
                message += "Le password non coincidono\n"
                return render_template('register.html', message=message)
        else:
            message += "L'utente è già registrato\n"
            return render_template('register.html', messages=message)
    else:
        message += "Nessun campo compilato\n"
        return render_template('register.html', message=message)
    return "Provo"


@app.route("/loginUser", methods=['GET', 'POST'])
def loginUser():

    if request.method == 'POST':
        message = ''
        email = request.values.get('inputEmail')
        password = request.values.get('inputPassword')
        print(password)
        if checkEmail(email):
            Session = sessionmaker(bind=engine)
            p = Session()
            user = p.query(Users).filter_by(EMAIL=email).first()
            g.user = user
            print(g.user.ADMIN)
            user_salt = str(user.SALT.encode('utf-8'))
            print(str(hashlib.sha512((password + user.SALT).encode('utf-8')).hexdigest()))
            if str((hashlib.sha512((password + user.SALT).encode('utf-8')).hexdigest())) == user.PASSWORD:
                checkLogin=True
                session['user'] = user.CODICE_UTENTE
                elezioni_list = ritornaElelezioni()
                return render_template("index.html", elezioni_list=elezioni_list), checkLogin
            else:
                message +="Email o Password errati\n"
                return render_template("login.html", message=message)
        else:
            message +="Email o Password errati\n"
            return render_template("login.html", message=message)


@app.route("/insertLista", methods=['GET', 'POST'])
def insertLista():

    if request.method == 'POST':
        message = ''
        nomeLista = request.form.get('formInserisciNomeLista')
        logoLista = request.form.get('formInserisciLogoLista')
        if nomeLista and logoLista:
            if checkLista(nomeLista):
                id_lista = str(uuid.uuid4())
                newList = Lista(ID_LISTA = id_lista, NOME_LISTA = nomeLista, LOGO_LISTA = logoLista)
                Session = sessionmaker(bind=engine)
                s = Session()
                s.add(newList)
                s.commit()
                g.user = Users.get_user_by_id(session['user'])
                elezioni_list = ritornaElelezioni()
                return render_template("index.html", elezioni_list=elezioni_list)
            else:
                message+="Lista già presente\n"
                return inserisciLista(message=message)
        else:
            message+="Compila tutti i campi\n"
            return inserisciLista(message=message)


@app.route("/insertCandidato", methods=['GET', 'POST'])
def insertCandidato():

    if request.method == 'POST':
        message=''
        user=request.values.get('select-user')
        lista=request.values.get('select-lista')
        candidatura=request.values.get('candidatura')
        if user and lista and candidatura:
            id_candidato=str(uuid.uuid4())
            newCandidato=Candidato(ID_CANDIDATO=id_candidato, FK_ID_UTENTE=user, FK_ID_LISTA = lista, CANDIDATURA=candidatura)
            Session=sessionmaker(bind=engine)
            s = Session()
            s.add(newCandidato)
            s.commit()
            g.user = Users.get_user_by_id(session['user'])
            elezioni_list=ritornaElelezioni()
            return render_template("index.html", elezioni_list=elezioni_list)
        else:
            message+="Compila tutti i campi"
            return inserisciCandidato(message=message)


@app.route("/insertElezione", methods=['GET', 'POST'])
def insertElezione():

    if request.method == 'POST':
        message = ''
        descrizioneElezione = request.values.get('descrizioneElezione')
        dataElezione = request.values.get('InserisciDataInizio')
        dataFine = request.values.get('InserisciDataFine')
        if descrizioneElezione and dataElezione and dataFine:
            if checkElezione(descrizioneElezione):
                id_elezione = str(uuid.uuid4())
                newElection = Elezioni(ID_ELEZIONE = id_elezione, DESCRIZIONE_ELEZIONE = descrizioneElezione, DATA_IN = dataElezione, DATA_FIN = dataFine)
                Session = sessionmaker(bind=engine)
                s = Session()
                s.add(newElection)
                s.commit()
                g.user = Users.get_user_by_id(session['user'])
                elezioni_list=ritornaElelezioni()
                return render_template("index.html", elezioni_list=elezioni_list)
            else:
                message+="Elezione già presente\n"
                return inserisciElezione(message=message)
        else:
            message+="Compila tutti i campi\n"
            return inserisciElezione(message=message)

@app.route("/insertCandidatoElezione", methods=['GET', 'POST'])
def insertCandidatoElezione():

    if request.method == 'POST':
        message = ''
        id_candidato = request.values.get('select-candidato')
        id_lista = request.values.get('select-lista')
        id_elezione = request.values.get('select-elezione')
        if id_candidato and id_lista and id_elezione:
            if checkCandidatoElezione(id_candidato, id_elezione):
                newCandidatoElezione = conteggio_voti_c(FK_ID_CANDIDATO=id_candidato, FK_ID_ELEZIONE=id_elezione, ID_LISTA=id_lista, NUMERO_VOTI_C=0)
                Session = sessionmaker(bind=engine)
                sessione = Session()
                sessione.add(newCandidatoElezione)
                sessione.commit()
                g.user = Users.get_user_by_id(session['user'])
                elezioni_list = ritornaElelezioni()
                return render_template('index.html', elezioni_list=elezioni_list)
            else:
                message="Candidato già presente in quest'elezione"
                return presentaCandidatoElezione(message=message)
        else:
            message = "Compila tutti i campi richiesti"
            return presentaCandidatoElezione(message=message)


@app.route("/insertListaElezione", methods=['GET', 'POST'])
def insertListaElezione():
    if request.method == 'POST':
        id_lista = request.values.get('select-lista')
        id_elezione = request.values.get('select-elezione')
        if not id_lista=="Seleziona una lista" and not id_elezione=="Selezione un Elezione":
            if checkListaElezione(id_lista, id_elezione):
                newListaElezioni = conteggio_voti_l(FK_ID_LISTA=id_lista, FK_ID_ELEZIONE=id_elezione, NUMERO_VOTI_L=0)
                Session = sessionmaker(bind=engine)
                sessione = Session()
                sessione.add(newListaElezioni)
                sessione.commit()
                g.user = Users.get_user_by_id(session['user'])
                elezioni_list=ritornaElelezioni()
                return render_template('index.html', elezioni_list=elezioni_list)
            else:
                message="Lista già candidata a quest'elezione"
                return presentaListaElezione(message=message)
        else:
            message="Devi compilare tutti i campi"
            return presentaListaElezione(message=message)


@csrf.exempt
@app.route("/voto/", methods=['GET', 'POST'])
def voto():
    if request.method == 'POST':
        elezioni_list = ritornaElelezioni()
        print("ok")
        g.user = Users.get_user_by_id(session['user'])
        g.elezioni = Elezioni.get_elezione_by_id(session['elezione'])
        if checkVoto(g.elezioni.ID_ELEZIONE, g.user.CODICE_UTENTE):
            print("voto-ok")
            id_candidato = request.form.get('id_candidato')
            id_lista = request.form.get('id_lista')
            print(id_lista)
            print(id_candidato)
            if id_candidato:
                Session = sessionmaker(bind=engine)
                sessione = Session()
                voti_c = sessione.query(conteggio_voti_c).filter_by(FK_ID_CANDIDATO = id_candidato).filter_by(FK_ID_ELEZIONE = g.elezioni.ID_ELEZIONE).first()
                voti_l = sessione.query(conteggio_voti_l).filter_by(FK_ID_LISTA = id_lista).filter_by(FK_ID_ELEZIONE = g.elezioni.ID_ELEZIONE).first()
                voti_l.NUMERO_VOTI_L += 1
                voti_c.NUMERO_VOTI_C += 1
                id_voto = str(uuid.uuid4())
                newVoto = Voto(ID_VOTO=id_voto, FK_ID_UTENTE = g.user.CODICE_UTENTE, FK_ID_ELEZIONE=g.elezioni.ID_ELEZIONE)
                sessione.add(newVoto)
                sessione.commit()

                return "Voto eseguito con successo!"
            else:
                Session = sessionmaker(bind=engine)
                sessione = Session()
                voti_l = sessione.query(conteggio_voti_l).filter_by(FK_ID_LISTA = id_lista).filter_by(FK_ID_ELEZIONE = g.elezioni.ID_ELEZIONE).first()
                voti_l.NUMERO_VOTI_L += 1
                id_voto = str(uuid.uuid4())
                newVoto = Voto(ID_VOTO=id_voto, FK_ID_UTENTE=g.user.CODICE_UTENTE, FK_ID_ELEZIONE=g.elezioni.ID_ELEZIONE)
                sessione.add(newVoto)
                sessione.commit()

                return "Voto eseguito con successo!"
        else:
            return "Hai già espresso il tuo voto alla seguente elezione"



def checkLista(nomeLista):
    lista = Lista.get_lista_by_name(nomeLista)

    if not lista:
        return True
    else:
        return False

def checkVoto(id_el, id_utente):
    Session = sessionmaker(bind=engine)
    sessione = Session()
    voto = sessione.query(Voto).filter_by(FK_ID_UTENTE = id_utente).filter_by(FK_ID_ELEZIONE = id_el).first()

    if not voto:
        return True
    else:
        return False

def checkElezione(descElezione):
    elezione = Elezioni.get_elezione_by_desc(descElezione)

    if not elezione:
        return True
    else:
        return False


def checkEmail(email):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(Users).filter_by(EMAIL=email).first()

    if not user:
        return False
    else:
        return True

def checkCandidatoElezione(id, id_elezione):

    candidato = conteggio_voti_c.get_candidato_by_id(id, id_elezione)

    if candidato:
        return False
    else:
        return True

def checkListaElezione(id, id_elezione):

    lista = conteggio_voti_l.get_lista_by_id(id, id_elezione)

    if lista:
        return False
    else:
        return True


def ritornaElelezioni():
    Session = sessionmaker(bind=engine)
    sessione = Session()

    return sessione.query(Elezioni).all()


def ritornaListe():
    Session = sessionmaker(bind=engine)
    sessione = Session()

    return sessione.query(Lista).all()



if __name__ == '__main__':
    app.run(debug=True)




