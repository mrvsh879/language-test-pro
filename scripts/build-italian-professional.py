from pathlib import Path
import json
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
APP=ROOT/'app.js'
LEVELS=['A1','A2','B1','B2','C1','C2']


def mc(qid,level,skill,prompt,options,answer,explanation,passage=None):
    q={'id':qid,'level':level,'skill':skill,'prompt':prompt,'options':options,'answer':answer,'explanation':explanation}
    if passage:q['passage']=passage
    return q


def build_main():
    Q=[]
    banks={
    'A1':[
    ('g','Io ___ italiano ogni giorno.',['studio','studia','studiamo','studiate'],0,'Con “io” si usa “studio”.'),
    ('g','Maria ___ a Milano.',['abita','abito','abiti','abitano'],0,'Con Maria si usa la terza persona singolare.'),
    ('g','Noi ___ due fratelli.',['abbiamo','avete','hanno','ha'],0,'Con “noi” il verbo avere è “abbiamo”.'),
    ('g','Luca e Paolo ___ studenti.',['sono','è','siamo','siete'],0,'Il soggetto è plurale: “sono”.'),
    ('g','Questo è ___ libro.',['un','una','uno','le'],0,'“Libro” è maschile singolare.'),
    ('g','Vorrei ___ acqua, per favore.',['dell’','del','della','dei'],0,'Davanti a “acqua” si usa “dell’”.'),
    ('g','Vado ___ lavoro alle otto.',['al','alla','nel','sul'],0,'L’espressione corretta è “andare al lavoro”.'),
    ('g','Il bar è ___ banca e la farmacia.',['tra la','sotto la','dentro la','senza la'],0,'“Tra” indica una posizione in mezzo a due luoghi.'),
    ('v','Quale parola indica il giorno dopo lunedì?',['martedì','mercoledì','venerdì','domenica'],0,'Il giorno dopo lunedì è martedì.'),
    ('v','Dove si compra il pane?',['in panetteria','in farmacia','in stazione','in banca'],0,'Il pane si compra in panetteria.'),
    ('v','Il contrario di “grande” è ___.',['piccolo','lungo','alto','nuovo'],0,'Il contrario di grande è piccolo.'),
    ('v','Per telefonare uso il ___.',['telefono','cucchiaio','quaderno','cuscino'],0,'Per telefonare si usa il telefono.'),
    ('v','Una persona che lavora in ospedale può essere un ___.',['medico','cuoco','autista','cassiere'],0,'Il medico lavora in ospedale.'),
    ('v','A colazione bevo spesso il ___.',['caffè','riso','sale','pane'],0,'Il caffè è una bevanda tipica della colazione.'),
    ('r','A che ora apre il sabato?',['Alle 9','Alle 10','Alle 14','È chiusa'],1,'Il sabato apre alle 10.','Biblioteca: lunedì–venerdì 9:00–18:00, sabato 10:00–14:00, domenica chiusa.'),
    ('r','Dove si trova Anna?',['A Roma','A Torino','A Napoli','A Firenze'],1,'Anna scrive che è a Torino.','Ciao Marco, sono a Torino per lavoro. Torno a Roma venerdì sera. Anna'),
    ('r','Quanto costa il menù?',['8 euro','10 euro','12 euro','15 euro'],2,'Il cartello indica 12 euro.','Menù del giorno: pasta, insalata e acqua — 12 euro.'),
    ('r','Quando parte il treno?',['Alle 7:15','Alle 7:50','Alle 8:15','Alle 8:50'],2,'Il treno parte alle 8:15.','Treno per Bologna: partenza ore 8:15, binario 4.'),
    ('r','Che cosa deve portare il cliente?',['Il passaporto','La ricevuta','Una fotografia','Il contratto'],1,'Per il cambio serve la ricevuta.','Per cambiare un articolo, portare il prodotto e la ricevuta entro 30 giorni.'),
    ('r','Quale giorno è chiuso il negozio?',['Lunedì','Martedì','Sabato','Domenica'],3,'Il negozio è chiuso la domenica.','Orario: lunedì–sabato 9:30–19:00. Domenica chiuso.')],
    'A2':[
    ('g','Vivo qui ___ 2022.',['dal','per','tra','a'],0,'Con un punto iniziale nel tempo si usa “dal”.'),
    ('g','Ieri ___ al cinema con Giulia.',['sono andato','vado','andrò','andavo sempre'],0,'“Ieri” richiede il passato prossimo per un evento concluso.'),
    ('g','Quando ero piccolo, ___ spesso dai nonni.',['andavo','sono andato','andrò','andrei'],0,'L’imperfetto descrive un’abitudine nel passato.'),
    ('g','Domani ti ___ dopo il lavoro.',['chiamerò','chiamavo','ho chiamato','chiamassi'],0,'“Domani” richiede il futuro.'),
    ('g','Non ho comprato il vestito perché era ___ caro.',['troppo','molto di','tanti','abbastanza di'],0,'“Troppo caro” significa più caro del necessario.'),
    ('g','Puoi aiutarmi ___ questo modulo?',['a compilare','compilando di','per compilo','di compilato'],0,'Dopo “aiutare” si usa “a” più infinito.'),
    ('g','Queste chiavi sono ___.',['mie','mio','mia','miei'],0,'“Chiavi” è femminile plurale: “mie”.'),
    ('g','Se hai tempo, ___ insieme.',['pranziamo','pranzeremmo','pranzassimo','pranzato'],0,'Nel periodo ipotetico reale si usa il presente.'),
    ('v','Per favore, ___ il modulo entro venerdì.',['compili','chiuda','presti','arrivi'],0,'Un modulo si compila.'),
    ('v','La riunione è stata spostata: è stata ___.',['rinviata','assunta','riparata','spedita'],0,'“Rinviata” significa spostata a un momento successivo.'),
    ('v','Se un prodotto non funziona, è ___.',['difettoso','affollato','gratuito','silenzioso'],0,'Un prodotto che non funziona è difettoso.'),
    ('v','Prima di firmare, bisogna leggere il ___.',['contratto','marciapiede','cassetto','biglietto'],0,'Si firma un contratto.'),
    ('v','Chi risponde alle domande dei clienti lavora nell’___.',['assistenza','agricoltura','edilizia','trasporto'],0,'L’assistenza clienti risponde alle domande.'),
    ('v','Il pacco è arrivato in ritardo a causa di un ___.',['ritardo nella consegna','aumento di stipendio','cambio di password','corso serale'],0,'La causa riguarda la consegna.'),
    ('r','Quando sarà il nuovo appuntamento?',['Martedì alle 11','Martedì alle 15','Mercoledì alle 11','Mercoledì alle 15'],2,'Il nuovo appuntamento è mercoledì alle 11.','L’appuntamento è stato spostato da martedì alle 15 a mercoledì alle 11.'),
    ('r','Che cosa deve fare il cliente?',['Aspettare a casa oggi','Ritirare il pacco domani','Annullare l’ordine','Pagare di nuovo'],1,'Il pacco va ritirato domani.','Non abbiamo potuto consegnare il pacco. Può ritirarlo domani dopo le 9 presso l’ufficio postale centrale.'),
    ('r','Qual è la nuova regola?',['Si lavora meno ore','Si può iniziare tra le 7 e le 9','L’ufficio chiude alle 7','Tutti lavorano da casa'],1,'È possibile scegliere l’inizio tra le 7 e le 9.','Da lunedì l’orario è flessibile: si può iniziare tra le 7 e le 9, rispettando le ore previste.'),
    ('r','Perché il corso è stato annullato?',['Mancano iscritti','Il docente è malato','La sala è occupata','Il prezzo è aumentato'],1,'Il messaggio indica la malattia del docente.','Il corso di oggi non si terrà perché il docente è malato. La nuova data sarà comunicata domani.'),
    ('r','Entro quando bisogna rispondere?',['Oggi','Mercoledì','Venerdì','La prossima settimana'],2,'La conferma è richiesta entro venerdì.','Confermi la partecipazione alla riunione entro venerdì rispondendo a questa email.'),
    ('r','Che cosa è incluso nel prezzo?',['Solo la camera','Camera e colazione','Pranzo e cena','Parcheggio e cena'],1,'Il prezzo comprende pernottamento e colazione.','Offerta weekend: due notti in camera doppia con colazione inclusa, 180 euro.')],
    'B1':[
    ('g','Se avessi più tempo, ___ un corso.',['seguirei','seguo','seguirò','ho seguito'],0,'Il periodo ipotetico della possibilità usa condizionale e congiuntivo imperfetto.'),
    ('g','Penso che il progetto ___ utile.',['sia','è','sarà sicuramente','era stato'],0,'Dopo “penso che” si usa normalmente il congiuntivo.'),
    ('g','Appena ___ il rapporto, te lo invierò.',['avrò finito','finivo','finirei','abbia finito ieri'],0,'Per un’azione futura anteriore si usa il futuro anteriore.'),
    ('g','Nonostante ___ stanco, ha continuato a lavorare.',['fosse','era','sarà','essere'],0,'Dopo “nonostante” si usa il congiuntivo.'),
    ('g','Mi ha chiesto se ___ disponibile il giorno dopo.',['sarei stato','sarò','sono','fossi ieri'],0,'Nel discorso indiretto al passato si usa il condizionale composto.'),
    ('g','È la prima volta che ___ questo programma.',['uso','usavo','userò','avrei usato'],0,'Con “è la prima volta che” è naturale il presente.'),
    ('g','Il documento deve ___ entro domani.',['essere firmato','firmare','firmato essere','si firma'],0,'La forma passiva corretta è “deve essere firmato”.'),
    ('g','Pur ___ poco tempo, siamo riusciti a finire.',['avendo','avuto','abbiamo','avremmo'],0,'“Pur avendo” introduce una concessione.'),
    ('v','La riunione è stata ___ a causa della malattia del responsabile.',['rinviata','costruita','raggiunta','assunta'],0,'Una riunione spostata è rinviata.'),
    ('v','Dobbiamo ___ una soluzione prima di venerdì.',['trovare','raggiungere una stanza','spedire un problema','assumere un prezzo'],0,'La collocazione corretta è “trovare una soluzione”.'),
    ('v','Il cliente ha presentato un ___.',['reclamo','incrocio','turno di notte','prestito linguistico'],0,'Un reclamo esprime insoddisfazione.'),
    ('v','Il nuovo sistema ha reso il processo più ___.',['efficiente','rumoroso','casuale','fragile'],0,'“Efficiente” descrive un processo che usa bene tempo e risorse.'),
    ('v','La decisione è stata presa dopo un’attenta ___.',['valutazione','spedizione','prenotazione','traduzione'],0,'Prima di decidere si fa una valutazione.'),
    ('v','Il responsabile ha ___ il problema durante la riunione.',['sollevato','abitato','versato','indossato'],0,'“Sollevare un problema” significa portarlo all’attenzione.'),
    ('r','Che cosa potranno scegliere i dipendenti?',['Lo stipendio','L’orario di inizio','Il responsabile','Il numero di ore'],1,'Potranno scegliere quando iniziare.','Dal mese prossimo i dipendenti potranno iniziare tra le 7 e le 10, ma dovranno svolgere tutte le ore previste dal contratto.'),
    ('r','Qual è lo scopo principale del messaggio?',['Criticare i dipendenti','Preparare una prova del sistema','Annullare il progetto','Ridurre il personale'],1,'Il messaggio organizza una prova prima del lancio.','Prima di introdurre il nuovo software, faremo una prova con un piccolo gruppo. I partecipanti dovranno segnalare problemi e suggerimenti.'),
    ('r','Perché il rimborso richiederà più tempo?',['Manca il prodotto','Serve una verifica aggiuntiva','La banca è chiusa','Il cliente non ha pagato'],1,'Il caso deve essere verificato manualmente.','Il rimborso è stato approvato, ma poiché il pagamento è avvenuto con due metodi diversi, sarà necessaria una verifica manuale.'),
    ('r','Qual è il vantaggio indicato?',['Meno comunicazione','Maggiore flessibilità','Più ore obbligatorie','Eliminazione delle riunioni'],1,'Il testo presenta la flessibilità come vantaggio.','Il lavoro ibrido offre maggiore flessibilità, ma richiede regole chiare per condividere informazioni tra chi è in ufficio e chi lavora da casa.'),
    ('r','Che cosa propone l’autore?',['Eliminare la formazione','Affiancare teoria e pratica','Ridurre gli obiettivi','Usare solo video'],1,'Propone di combinare spiegazioni e applicazione.','Una formazione efficace non dovrebbe limitarsi a presentare regole. I partecipanti devono poterle applicare a casi realistici e ricevere feedback.'),
    ('r','Qual è la causa principale del ritardo?',['Un errore del cliente','La mancanza di un componente','Uno sciopero','Un cambio di indirizzo'],1,'Manca un componente necessario.','La consegna è stata posticipata perché un componente essenziale non è ancora arrivato dal fornitore.')],
    'B2':[
    ('g','Quando siamo arrivati, la presentazione ___.',['era già iniziata','inizia','inizierà','sarebbe iniziata domani'],0,'Il trapassato prossimo indica un’azione anteriore a un’altra nel passato.'),
    ('g','Qualora ___ ulteriori problemi, contattateci subito.',['sorgessero','sorgono','sorgeranno','sono sorti ieri'],0,'Dopo “qualora” si usa il congiuntivo.'),
    ('g','Il progetto sarebbe stato approvato se i costi ___ inferiori.',['fossero stati','sono stati','saranno','siano'],0,'Nel periodo ipotetico irreale del passato si usa il congiuntivo trapassato.'),
    ('g','Non è chiaro fino a che punto la misura ___ efficace.',['sia','è certamente','sarà stata','essendo'],0,'L’incertezza richiede il congiuntivo.'),
    ('g','Il direttore ha insistito affinché tutti ___ informati.',['fossero','erano','saranno','sono stati'],0,'“Affinché” regge il congiuntivo.'),
    ('g','A prescindere da come ___ la trattativa, servirà un piano alternativo.',['vada','va','andrà sicuramente','andava'],0,'La costruzione concessiva richiede il congiuntivo.'),
    ('g','Il rapporto, ___ ieri dal consiglio, sarà pubblicato domani.',['approvato','approvando','approvare','sia approvato'],0,'Il participio passato riduce una relativa passiva.'),
    ('g','Più il sistema diventa complesso, ___ difficile controllarlo.',['più è','è più di','tanto è','più sarebbe stato'],0,'La correlazione corretta è “più…, più…”.'),
    ('v','La sua spiegazione era chiara e ___.',['coerente','casuale','temporanea','sensibile'],0,'“Coerente” indica logica e assenza di contraddizioni.'),
    ('v','I risultati vanno interpretati con ___.',['cautela','fretta assoluta','indifferenza','rumore'],0,'“Con cautela” è la collocazione corretta.'),
    ('v','La nuova procedura mira a ___ gli errori.',['ridurre','abitare','versare','prenotare'],0,'Una procedura può ridurre gli errori.'),
    ('v','Il problema non è isolato, ma ___.',['ricorrente','commestibile','silenzioso','gratuito'],0,'“Ricorrente” significa che si ripete.'),
    ('v','La proposta ha ricevuto un’accoglienza ___.',['contrastante','rettangolare','notturna','liquida'],0,'“Accoglienza contrastante” indica reazioni diverse.'),
    ('v','Serve una soluzione che sia economicamente ___.',['sostenibile','affollata','provvisoria di','sensibile a caso'],0,'Una soluzione economicamente sostenibile può durare nel tempo.'),
    ('r','Che cosa raccomanda il rapporto?',['Eliminare il lavoro remoto','Un modello ibrido','Ridurre la comunicazione','Il ritorno completo'],1,'Raccomanda incontri in presenza senza abolire il remoto.','Il rapporto afferma che il lavoro da remoto ha aumentato la produttività ma ridotto lo scambio informale di conoscenze. Raccomanda incontri regolari in presenza, non un ritorno completo in ufficio.'),
    ('r','Qual è la posizione dell’autore?',['I dati sono inutili','I dati aiutano ma non sostituiscono il giudizio','Ogni decisione deve essere automatica','L’esperienza personale basta sempre'],1,'Il testo sostiene un uso equilibrato dei dati.','I dati possono rendere le decisioni più trasparenti, ma non eliminano la necessità di interpretare il contesto e valutare conseguenze difficili da misurare.'),
    ('r','Perché l’aumento non prova ancora una tendenza?',['I dati sono falsi','Dipende in parte da un ordine eccezionale','Il mercato è chiuso','Mancano dipendenti'],1,'Una parte importante è dovuta a un evento unico.','Le vendite sono cresciute, ma quasi metà dell’aumento deriva da un ordine eccezionale. È quindi prematuro parlare di una ripresa stabile.'),
    ('r','Quale rischio viene evidenziato?',['Troppe regole possono ridurre la capacità di adattarsi','La flessibilità elimina ogni controllo','Gli standard sono sempre inutili','Le eccezioni aumentano i profitti'],0,'Il rischio è una rigidità eccessiva.','Procedure standard migliorano la coerenza, ma se applicate senza considerare casi particolari possono produrre decisioni inappropriate.'),
    ('r','Che cosa distingue le due strategie?',['Solo il prezzo','Il modo di gestire l’incertezza','Il numero di uffici','La lingua dei documenti'],1,'Il testo contrappone due modi di affrontare l’incertezza.','La prima strategia riduce i rischi rinviando la decisione; la seconda accetta una parte di incertezza per ottenere informazioni prima.'),
    ('r','Qual è la conclusione più corretta?',['La tecnologia causa sempre disuguaglianze','Gli effetti dipendono anche da come viene introdotta','L’innovazione non cambia il lavoro','La formazione è irrilevante'],1,'Il testo lega gli effetti alle modalità di implementazione.','La stessa tecnologia può aumentare l’autonomia in un’organizzazione e il controllo in un’altra. Molto dipende dalle regole e dagli obiettivi con cui viene introdotta.')],
    'C1':[
    ('g','Raramente ___ una proposta così convincente.',['ho sentito','sentirei','sentirò','avevo sentito domani'],0,'L’avverbio non cambia il normale uso del passato prossimo.'),
    ('g','Benché la misura ___ risultati iniziali, restano dubbi sulla sua durata.',['abbia prodotto','ha prodotto certamente','produrrà','produceva sempre'],0,'“Benché” regge il congiuntivo.'),
    ('g','Non si può escludere che i dati ___ incompleti.',['siano','sono sicuramente','saranno stati sempre','essere'],0,'L’espressione di possibilità richiede il congiuntivo.'),
    ('g','Era necessario che la decisione ___ prima della pubblicazione.',['fosse motivata','era motivata','sarà motivata','motivava'],0,'Nel passato, “era necessario che” richiede il congiuntivo imperfetto.'),
    ('g','Per quanto ___ fondate, le obiezioni non cambiano la conclusione.',['possano essere','sono','saranno','essendo state domani'],0,'“Per quanto” concessivo regge il congiuntivo.'),
    ('g','Il problema è meno semplice di quanto ___ inizialmente.',['sembrasse','sembrava certo','sembra di','sembrerà stato'],0,'Dopo il comparativo con “di quanto” è naturale il congiuntivo.'),
    ('g','La riforma, lungi dal ___ il problema, lo ha reso più visibile.',['risolvere','risolto','risolvesse','risoluzione'],0,'“Lungi dal” è seguito dall’infinito.'),
    ('g','Che la scelta sia discutibile non ___ che sia priva di logica.',['significa','significhi di','significato','significherà stato'],0,'La frase soggettiva richiede qui l’indicativo nella principale.'),
    ('v','I risultati ___ la necessità di ulteriori ricerche.',['sottolineano','trascurano','sospendono','disperdono'],0,'“Sottolineare la necessità” significa evidenziarla.'),
    ('v','L’argomentazione è solida, ma la conclusione appare troppo ___.',['categorica','commestibile','affollata','rettangolare'],0,'“Categorica” indica una conclusione espressa senza sfumature.'),
    ('v','La distinzione proposta è utile, anche se non sempre ___.',['netta','liquida','sonora','gratuita'],0,'Una distinzione può essere netta o sfumata.'),
    ('v','Il rapporto mette in luce una conseguenza spesso ___.',['trascurata','indossata','prenotata','abitata'],0,'Una conseguenza ignorata è trascurata.'),
    ('v','La misura ha avuto effetti ___.',['ambivalenti','triangolari','domestici soltanto','commestibili'],0,'“Ambivalenti” indica effetti sia positivi sia negativi.'),
    ('v','L’autore invita a non ___ correlazione e causalità.',['confondere','spedire','assumere un tavolo','prenotare'],0,'Correlazione e causalità non vanno confuse.'),
    ('r','Qual è la preoccupazione principale?',['L’automazione è sempre dannosa','Un valore importante può essere ignorato','L’efficienza non si può misurare','La politica aziendale è inutile'],1,'Teme che valori meno visibili vengano ignorati.','L’autrice non rifiuta l’automazione; contesta invece l’idea che la sola efficienza debba guidare la politica aziendale. I risultati misurabili possono nascondere forme di valore meno visibili.'),
    ('r','Che cosa sostiene implicitamente il testo?',['Più documenti garantiscono trasparenza','La trasparenza richiede informazioni comprensibili e pertinenti','I criteri devono restare segreti','La quantità è sempre più importante della qualità'],1,'La trasparenza dipende dalla comprensibilità, non solo dalla quantità.','Pubblicare molti documenti non rende automaticamente un processo trasparente. Se criteri e passaggi decisivi restano difficili da individuare, l’abbondanza di dati può perfino confondere.'),
    ('r','Come vengono trattate le obiezioni?',['Sono ignorate','Limitano la portata della tesi senza annullarla','Dimostrano che la tesi è falsa','Sostituiscono completamente la conclusione'],1,'Le obiezioni precisano, ma non eliminano, la tesi.','Le obiezioni sono fondate e richiedono una formulazione più prudente. Tuttavia non negano il nucleo dell’argomento, ma ne delimitano l’ambito.'),
    ('r','Quale tensione descrive l’autore?',['Velocità contro precisione','Uniformità contro attenzione ai casi particolari','Profitto contro salario','Scrittura contro ascolto'],1,'Il testo contrappone standard comuni e casi specifici.','Gli standard rendono le decisioni confrontabili, ma possono trattare come uguali situazioni molto diverse. Un sistema efficace deve quindi combinare regole e possibilità motivate di eccezione.'),
    ('r','Perché il risultato va interpretato con prudenza?',['Il campione è limitato e non rappresentativo','Non esistono dati','La ricerca è troppo lunga','Tutti i partecipanti hanno risposto uguale'],0,'Il limite principale riguarda il campione.','Lo studio mostra un miglioramento rilevante, ma coinvolge un gruppo piccolo e selezionato. Non è certo che lo stesso effetto si presenti in contesti diversi.'),
    ('r','Qual è il punto centrale?',['Ogni compromesso è negativo','Il compromesso è utile solo se non nasconde il conflitto reale','Il consenso completo è sempre possibile','Le parole non influenzano le decisioni'],1,'Il testo distingue compromessi operativi da formule che nascondono il dissenso.','Il compromesso permette di agire quando l’accordo completo non è possibile. Diventa però problematico se serve soltanto a mascherare obiettivi incompatibili.')],
    'C2':[
    ('g','Senza il suo intervento, i negoziati ___.',['sarebbero falliti','falliranno','falliscono','erano falliti prima'],0,'Il condizionale composto esprime una conseguenza irreale nel passato.'),
    ('g','Non che la riforma ___ inutile, ma affronta solo una parte del problema.',['sia','è certamente','sarà','era stata sempre'],0,'“Non che” regge il congiuntivo.'),
    ('g','Per quanto se ne ___, la decisione sembra già presa.',['discuta','discute','discuterà','ha discusso certamente'],0,'La costruzione concessiva richiede il congiuntivo.'),
    ('g','Ammesso e non concesso che i dati ___ corretti, la conclusione resta eccessiva.',['siano','sono','saranno','erano certamente'],0,'La formula ipotetica richiede il congiuntivo.'),
    ('g','Se anche la misura ___ effetti positivi, non ne seguirebbe la necessità.',['avesse','ha','avrà','aveva certamente'],0,'La concessione ipotetica usa il congiuntivo imperfetto.'),
    ('g','La tesi è formulata in modo tale da non poter essere facilmente ___.',['confutata','confutando','confutare','si confuta'],0,'Dopo “essere” serve il participio passato.'),
    ('g','È proprio ciò che il rapporto tace a ___ la sua conclusione fragile.',['rendere','reso','rendesse','avere reso ieri'],0,'La costruzione scissa usa “a” più infinito.'),
    ('g','Non fosse stato per quell’errore, la discrepanza sarebbe rimasta ___.',['inosservata','osservando','osservare','si osserva'],0,'Serve un participio/aggettivo riferito a “discrepanza”.'),
    ('v','Le sue scuse erano così ___ da sembrare un tentativo di evitare ogni responsabilità.',['equivoche','meticolose','franche','tangibili'],0,'“Equivoche” indica ambiguità intenzionale.'),
    ('v','Il testo adotta un tono solo apparentemente ___.',['elogiativo','commestibile','geografico','numerico'],0,'Un tono elogiativo sembra lodare.'),
    ('v','L’autore smonta la tesi con una critica ___.',['sottile','rettangolare','stagionale','liquida'],0,'Una critica sottile è indiretta ma precisa.'),
    ('v','La distinzione rischia di essere più ___ che reale.',['nominale','alimentare','notturna','metallica'],0,'“Nominale” indica una differenza solo di nome.'),
    ('v','La formulazione lascia volutamente la questione ___.',['irrisolta','abitata','spedita','indossata'],0,'Una questione non risolta resta irrisolta.'),
    ('v','Il ragionamento è valido solo a patto di non ___ ciò che vuole dimostrare.',['presupporre','prenotare','versare','tradurre'],0,'Un ragionamento circolare presuppone la conclusione.'),
    ('r','Come va interpretato il tono?',['Del tutto sincero','Neutrale','Ironico e critico','Confuso'],2,'I complimenti rivelano indirettamente contraddizioni.','L’apparente elogio del saggio è volutamente ambiguo: ogni complimento è formulato in modo da rivelare discretamente le contraddizioni della politica descritta.'),
    ('r','Qual è la critica principale?',['La trasparenza è sempre dannosa','Una quantità eccessiva di dati può simulare apertura senza chiarire le decisioni','I documenti devono essere eliminati','Solo gli esperti possono leggere i dati'],1,'La critica riguarda una trasparenza solo apparente.','La richiesta di completa trasparenza sembra indiscutibile. Tuttavia, una massa di informazioni secondarie può nascondere i criteri davvero decisivi e trasformare l’apertura in una semplice rappresentazione.'),
    ('r','Che cosa mette in discussione il testo?',['La necessità di regole','L’equivalenza automatica tra trattamento uguale e giustizia','L’esistenza di condizioni diverse','Ogni forma di uguaglianza'],1,'Regole uguali possono avere effetti diversi.','Una regola formalmente identica può incidere su condizioni di partenza molto diverse, rafforzando disuguaglianze già esistenti. Trattamento uguale e giustizia non coincidono necessariamente.'),
    ('r','Quale inferenza è più fondata?',['La riforma non produce alcun effetto','Corregge difetti visibili ma potrebbe non modificare gli incentivi di fondo','Risolve definitivamente il problema','Gli incentivi non contano'],1,'Il testo distingue effetti immediati e problema strutturale.','Non si può dire che la riforma sia priva di effetti: elimina alcuni difetti evidenti. Resta però incerto se modifichi il sistema di incentivi che genera il problema.'),
    ('r','Perché la distinzione è instabile?',['Le categorie si sovrappongono nei casi concreti','Le definizioni sono troppo brevi solo per errore tipografico','Non esistono esempi','Il testo cambia lingua'],0,'I casi reali non rispettano sempre confini netti.','La distinzione è utile sul piano analitico, ma nei casi concreti le due categorie si sovrappongono. Trattarla come assoluta rischia quindi di produrre conclusioni artificiali.'),
    ('r','Quale strategia retorica usa l’autore?',['Afferma direttamente il contrario','Concede parte della tesi prima di limitarne la portata','Evita ogni argomento','Elenca soltanto dati'],1,'L’autore riconosce un punto e poi ne restringe le conseguenze.','Che l’efficienza sia aumentata non è in discussione. Ciò che non segue automaticamente è che ogni costo sociale della misura debba per questo essere accettato.')]
    }
    for level in LEVELS:
        for i,item in enumerate(banks[level],1):
            skill,prompt,options,answer,explanation,*passage=item
            Q.append(mc(f"it-{level.lower()}-{skill}-{i:02d}",level,{'g':'grammar','v':'vocabulary','r':'reading'}[skill],prompt,options,answer,explanation,passage[0] if passage else None))
    return Q


def build_listening():
    raw={
    'A1':[
    ('Il treno per Roma parte alle otto e venti dal binario tre.','A che ora parte il treno?',['Alle 8:00','Alle 8:20','Alle 8:30','Alle 3:00'],1),
    ('Mi chiamo Elena e vivo a Firenze.','Dove vive Elena?',['A Roma','A Milano','A Firenze','A Torino'],2),
    ('Vorrei un caffè e un bicchiere d’acqua, per favore.','Che cosa ordina?',['Tè e succo','Caffè e acqua','Solo acqua','Caffè e latte'],1),
    ('Il negozio oggi chiude alle diciannove.','Quando chiude il negozio?',['Alle 17','Alle 18','Alle 19','Alle 20'],2),
    ('Domani lavoro dalle nove alle cinque.','A che ora inizia a lavorare?',['Alle 5','Alle 8','Alle 9','Alle 10'],2),
    ('Sabato andiamo al mare con gli amici.','Quando vanno al mare?',['Venerdì','Sabato','Domenica','Lunedì'],1),
    ('Due biglietti per Venezia, per favore.','Quanti biglietti vuole?',['Uno','Due','Tre','Quattro'],1),
    ('Oggi fa freddo e piove. Porta l’ombrello.','Che tempo fa?',['Fa caldo','Nevica','Fa freddo e piove','C’è il sole'],2),
    ('La riunione è alle dieci nella sala dodici.','Dove si svolge la riunione?',['Sala 10','Sala 12','Ufficio 20','Ingresso'],1),
    ('Per il compleanno ho ricevuto un libro e una camicia blu.','Che cosa ha ricevuto?',['Un libro e una camicia','Un telefono e un libro','Scarpe e una camicia','Solo un libro'],0),
    ('L’autobus numero venti va alla stazione centrale.','Dove va l’autobus?',['All’aeroporto','In centro','Alla stazione centrale','All’ospedale'],2),
    ('Ho una prenotazione a nome Rossi per due notti.','Per quante notti?',['Una','Due','Tre','Quattro'],1)],
    'A2':[
    ('La riunione di oggi è spostata dalle quattordici alle quindici e trenta.','Quando inizia la riunione?',['14:00','14:30','15:30','16:00'],2),
    ('Non abbiamo consegnato il pacco. Può ritirarlo domani dopo le nove in posta.','Che cosa deve fare il cliente?',['Aspettare oggi','Ritirare il pacco domani','Annullare l’ordine','Chiamare alle nove'],1),
    ('Per lavori stradali, questa settimana l’autobus non ferma in piazza.','Che cosa cambia?',['Il biglietto costa meno','L’autobus non ferma in piazza','La strada riapre','La fermata è in stazione'],1),
    ('Prima dell’esame non deve mangiare, ma può bere acqua.','Che cosa può fare?',['Fare colazione','Bere acqua','Bere latte','Mangiare frutta'],1),
    ('Il tavolo è disponibile, ma le sedie arriveranno mercoledì prossimo.','Che cosa manca?',['Il tavolo','Le sedie','Tutto','Niente'],1),
    ('La colazione è dalle sette alle dieci; nel weekend fino alle dieci e trenta.','Fino a che ora nel weekend?',['9:30','10:00','10:30','11:00'],2),
    ('Il corso inizia lunedì. Le prime due lezioni saranno online.','Come saranno le prime lezioni?',['A scuola','Online','In biblioteca','Annullate'],1),
    ('Martedì non posso; vanno bene mercoledì mattina o giovedì pomeriggio.','Quale giorno non va bene?',['Martedì','Mercoledì','Giovedì','Entrambi'],0),
    ('La riparazione costa duecento euro. Se serve una batteria nuova, sono ottanta euro in più.','Di quanto può aumentare il prezzo?',['20 euro','80 euro','120 euro','280 euro'],1),
    ('Venerdì l’ufficio chiude alle tredici. Porti i documenti entro giovedì.','Quando portare i documenti?',['Venerdì sera','Entro giovedì','Sabato','Lunedì'],1),
    ('Volevamo prendere il treno, ma la linea è chiusa. Andremo in auto.','Perché vanno in auto?',['Il treno costa troppo','La linea è chiusa','L’auto è più veloce','Non hanno biglietti'],1),
    ('Le mando il contratto oggi. Restituisca la copia firmata entro venerdì.','Che cosa deve fare?',['Buttarlo','Restituire la copia firmata','Telefonare oggi','Scrivere un nuovo contratto'],1)],
    'B1':[
    ('La riunione non inizierà alle nove, ma alle nove e trenta. La sala resta la stessa.','Che cosa cambia?',['La sala','L’orario','Il giorno','I partecipanti'],1),
    ('Abbiamo esaminato il reclamo. Sostituiremo il prodotto gratuitamente e non pagherà la spedizione.','Quale soluzione viene offerta?',['Rimborso parziale','Sostituzione gratuita','Sconto futuro','Riparazione a pagamento'],1),
    ('Mandami la versione aggiornata entro giovedì, così potrò controllarla prima della presentazione.','Perché serve entro giovedì?',['Per controllarla prima','Per spostare la presentazione','Per scrivere un contratto','Per annullare la riunione'],0),
    ('Il corso non è obbligatorio, ma è consigliato a chi usa il nuovo sistema ogni giorno.','A chi è consigliato?',['A tutti i clienti','A chi usa il sistema spesso','Solo ai dirigenti','A chi non lavora'],1)],
    'B2':[
    ('I dati sembrano migliori, ma gran parte dell’aumento dipende da un ordine unico. È presto per parlare di una tendenza stabile.','Come valuta la situazione?',['Molto positivamente','Con cautela','Negativamente perché le vendite calano','Come definitiva'],1),
    ('La procedura comune riduce gli errori, ma nei casi insoliti può produrre decisioni poco adatte.','Qual è il limite?',['Costa troppo','È rigida nei casi particolari','Non riduce errori','È troppo breve'],1),
    ('Il lavoro remoto ha migliorato la concentrazione, ma ha ridotto gli scambi informali tra colleghi.','Qual è il risultato?',['Solo positivo','Vantaggi e svantaggi','Solo negativo','Nessun cambiamento'],1),
    ('Non contestiamo l’obiettivo, ma dubitiamo che lo strumento scelto sia proporzionato.','Che cosa viene criticato?',['L’obiettivo','Lo strumento','Il personale','Il calendario'],1)],
    'C1':[
    ('Pubblicare più dati non garantisce trasparenza: se i criteri decisivi restano nascosti, l’abbondanza può confondere.','Qual è la tesi?',['Più dati bastano','Conta la comprensibilità dei criteri','I dati sono inutili','La trasparenza è impossibile'],1),
    ('Le obiezioni non annullano l’argomento, ma ne limitano la portata e richiedono una formulazione più prudente.','Che effetto hanno le obiezioni?',['Annullano tutto','Precisano la tesi','Sono irrilevanti','Cambiano tema'],1),
    ('Un campione selezionato può mostrare un effetto reale senza dimostrare che esso valga in ogni contesto.','Quale limite viene indicato?',['Nessun dato','Generalizzazione limitata','Errore di calcolo','Mancanza di teoria'],1),
    ('Regole uniformi aumentano la coerenza, ma possono ignorare differenze importanti tra i casi.','Quale tensione emerge?',['Costo e tempo','Uniformità e adattamento','Lingua e tecnologia','Teoria e pratica'],1)],
    'C2':[
    ('La riforma elimina difetti evidenti, ma non è chiaro se modifichi gli incentivi che li producono.','Qual è il dubbio centrale?',['Non ha effetti','Potrebbe non risolvere la causa strutturale','Costa troppo','È illegale'],1),
    ('Una massa di informazioni secondarie può trasformare la trasparenza in una semplice rappresentazione.','Che cosa significa?',['La trasparenza è sempre falsa','L’apertura può essere solo apparente','Servono meno documenti sempre','I dati devono restare segreti'],1),
    ('Trattare tutti nello stesso modo può rafforzare disuguaglianze se le condizioni di partenza sono diverse.','Quale idea viene criticata?',['Ogni regola','L’equivalenza automatica tra uguaglianza e giustizia','La diversità','La legge'],1),
    ('Il compromesso è utile finché permette di agire; diventa problematico quando nasconde obiettivi incompatibili.','Quando è problematico?',['Sempre','Quando nasconde il conflitto','Quando è scritto','Quando è rapido'],1)]}
    out=[]
    for level in LEVELS:
        for i,(tr,p,o,a) in enumerate(raw[level],1):
            out.append({'id':f'it-{level.lower()}-l-{i:02d}','level':level,'skill':'listening','transcript':tr,'prompt':p,'options':o,'answer':a,'maxPlays':2,'explanation':f'La risposta corretta è: {o[a]}.'})
    return out


def build_speaking():
    raw={
    'A1':['Buongiorno, mi chiamo Laura e abito a Roma.','Il negozio apre alle nove e chiude alle diciotto.','Vorrei un caffè e un bicchiere d’acqua, per favore.','Domani prendo il treno delle otto per Milano.','La mia famiglia vive in una piccola città vicino al mare.','Oggi fa freddo, quindi porto una giacca.'],
    'A2':['L’appuntamento è stato spostato a mercoledì mattina. Per favore, confermi se il nuovo orario va bene.','Il pacco non è stato consegnato. Può ritirarlo domani presso l’ufficio postale centrale.','Da lunedì l’ufficio avrà un orario flessibile, ma tutti dovranno completare le ore previste.','Ho prenotato una camera per due notti con colazione inclusa.','Prima della visita può bere acqua, ma non deve mangiare.','Il corso comincia online e prosegue in presenza dalla terza lezione.'],
    'B1':['A causa di un problema tecnico, la formazione inizierà trenta minuti più tardi. Informate anche i colleghi che non sono ancora in ufficio.','Il cliente ha ricevuto il pacco in tempo, ma due articoli erano danneggiati. Verificheremo il caso e proporremo una soluzione entro domani.','Se non può venire all’appuntamento, lo annulli almeno ventiquattro ore prima. Altrimenti potrebbe essere applicata una tariffa.','L’orario flessibile facilita la vita quotidiana, ma il gruppo ha bisogno di regole chiare per condividere il lavoro.'],
    'B2':['L’introduzione del nuovo sistema è stata rinviata perché alcune integrazioni non funzionano ancora in modo affidabile. Prima del lancio faremo un’altra fase di prova.','I risultati indicano un miglioramento, ma una parte importante della crescita dipende da un ordine eccezionale. È quindi presto per parlare di una svolta stabile.','Valutare attentamente i rischi non significa rallentare ogni decisione. Spesso evita errori costosi in una fase successiva.','Il reclamo non riguarda soltanto il ritardo, ma soprattutto la mancanza di comunicazione chiara con il cliente.'],
    'C1':['Una maggiore quantità di dati non garantisce automaticamente più obiettività. Contano anche il modo in cui i dati sono raccolti e il contesto in cui vengono interpretati.','Le obiezioni sono comprensibili, ma non annullano la conclusione principale. Ne limitano piuttosto la portata e richiedono una formulazione più precisa.','La trasparenza non dipende dal numero di documenti pubblicati, ma dalla chiarezza dei criteri e delle procedure decisionali.','Le procedure standard aumentano la coerenza, ma devono lasciare spazio a eccezioni motivate quando le circostanze sono davvero diverse.'],
    'C2':['Una trasparenza solo apparente può nascondere le informazioni decisive sotto una massa di dettagli secondari, rendendo più difficile capire come è stata presa una decisione.','La riforma corregge alcuni difetti evidenti, ma resta da dimostrare che modifichi gli incentivi che continuano a generare il problema.','Una regola formalmente uguale può avere effetti molto diversi su persone che partono da condizioni differenti; per questo uguaglianza e giustizia non coincidono sempre.','Il compromesso permette di agire senza un accordo completo, ma perde valore quando serve soltanto a nascondere obiettivi che non possono essere conciliati.']}
    out=[]
    for level in LEVELS:
        for i,text in enumerate(raw[level],1):
            out.append({'id':f'it-{level.lower()}-s-{i:02d}','level':level,'skill':'speaking','prompt':'Leggi il testo ad alta voce.','passage':text,'maxDurationSec':55 if level in ['A1','A2','B1'] else 80})
    return out


def validate(items,skill=None):
    ids=[q['id'] for q in items]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate IDs')
    for q in items:
        if q['level'] not in LEVELS:raise ValueError(q['id'])
        if skill and q['skill']!=skill:raise ValueError(q['id'])
        if q['skill']!='speaking' and (len(q['options'])!=4 or q['answer'] not in range(4)):raise ValueError(q['id'])


def write(name,items):
    (DATA/name).write_text(json.dumps({'language':'it','version':'3.0.0-professional','questionCount':len(items),'questions':items},ensure_ascii=False,separators=(',',':')),encoding='utf-8')


def main():
    main=build_main(); listening=build_listening(); speaking=build_speaking()
    validate(main);validate(listening,'listening');validate(speaking,'speaking')
    counts=Counter(q['level'] for q in main)
    if any(counts[x]!=20 for x in LEVELS):raise ValueError(counts)
    write('it.json',main);write('it-listening.json',listening);write('it-speaking.json',speaking)
    text=APP.read_text(encoding='utf-8')
    text=text.replace("if(['cs','de'].includes(lang))","if(['cs','de','it'].includes(lang))")
    text=text.replace("if(['cs','de'].includes(state.candidate?.language))","if(['cs','de','it'].includes(state.candidate?.language))")
    text=text.replace("if(['cs','de'].includes(state.candidate.language)&&idx(finalLevel)>=3)","if(['cs','de','it'].includes(state.candidate.language)&&idx(finalLevel)>=3)")
    APP.write_text(text,encoding='utf-8')
    print('Italian professional build complete',len(main),len(listening),len(speaking),dict(counts))

if __name__=='__main__':main()
