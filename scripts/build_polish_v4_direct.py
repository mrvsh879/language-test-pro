import json
from pathlib import Path

DATA = Path('data')
LEVELS = ['A1','A2','B1','B2','C1','C2']


def load(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def q(qid, level, skill, prompt, options, answer, explanation, passage=None):
    item = {
        'id': qid,
        'level': level,
        'skill': skill,
        'prompt': prompt,
        'options': options,
        'answer': answer,
        'explanation': explanation,
    }
    if passage is not None:
        item['passage'] = passage
    return item


def improve_basic_explanations(items):
    for item in items:
        if item['level'] not in {'A1','A2'}:
            continue
        correct = item['options'][item['answer']]
        skill = item['skill']
        if skill == 'grammar':
            item['explanation'] = f'Poprawna forma to „{correct}”. Pasuje do osoby, liczby, czasu lub przypadku wymaganego przez całe zdanie; pozostałe formy naruszają tę zgodność.'
        elif skill == 'vocabulary':
            item['explanation'] = f'„{correct}” najlepiej odpowiada znaczeniu zdania. Pozostałe wyrazy należą do innego kontekstu albo zmieniają sens wypowiedzi.'
        else:
            item['explanation'] = f'Informacja prowadząca do odpowiedzi „{correct}” znajduje się bezpośrednio w tekście. Inne warianty mylą godzinę, miejsce, termin lub czynność.'


MAIN_REPLACEMENTS = {
'B1': [
q('pl-b1-g-01','B1','grammar','Gdybym wcześniej znał termin, ___ urlop inaczej.',['planuję','zaplanowałbym','zaplanowałem','będę planować'],1,'Tryb warunkowy wymaga formy „zaplanowałbym”, ponieważ mowa o hipotetycznej zmianie przeszłej decyzji.'),
q('pl-b1-g-02','B1','grammar','To jest klient, z ___ rozmawialiśmy wczoraj.',['który','którego','którym','któremu'],2,'Przyimek „z” łączy się z narzędnikiem, dlatego poprawna forma to „z którym”.'),
q('pl-b1-g-03','B1','grammar','Kiedy dotarliśmy na miejsce, prezentacja już ___.',['zaczyna się','zaczęła się','zacznie się','zaczynałaby się'],1,'Czynność zakończyła się przed innym wydarzeniem w przeszłości, więc potrzebny jest czas przeszły: „zaczęła się”.'),
q('pl-b1-g-04','B1','grammar','Kierownik poprosił, żebyśmy ___ raport do piątku.',['kończymy','skończyli','skończymy','kończyć'],1,'Po „poprosił, żebyśmy” używamy formy czasu przeszłego w funkcji życzeniowo-rozkazującej: „skończyli”.'),
q('pl-b1-g-05','B1','grammar','Nie tylko przygotował dane, ___ także wyjaśnił ich znaczenie.',['ale','bo','więc','chociaż'],0,'Konstrukcja łączna ma postać „nie tylko…, ale także…”.'),
q('pl-b1-g-06','B1','grammar','Im dłużej trwało spotkanie, tym ___ było utrzymać uwagę.',['trudne','trudniej','najtrudniej','trudny'],1,'W konstrukcji „im…, tym…” potrzebny jest przysłówek w stopniu wyższym: „trudniej”.'),
q('pl-b1-g-07','B1','grammar','Dokument, ___ dziś wysłałeś, wymaga jeszcze podpisu.',['który','którego','któremu','którym'],0,'Zaimek jest dopełnieniem bliższym nieżywotnym w bierniku, który ma formę „który”.'),
q('pl-b1-v-01','B1','vocabulary','„Dotrzymać terminu” oznacza ___.',['zmienić datę bez uprzedzenia','wykonać zadanie na czas','odłożyć pracę','ustalić nowy budżet'],1,'Wyrażenie oznacza zakończenie pracy w ustalonym czasie, a nie zmianę lub przesunięcie terminu.'),
q('pl-b1-v-02','B1','vocabulary','Jeżeli rozwiązanie jest „tymczasowe”, to ___.',['ma obowiązywać przez ograniczony czas','jest ostateczne','nie wymaga kontroli','dotyczy wyłącznie finansów'],0,'„Tymczasowe” znaczy przejściowe, wprowadzone na pewien okres.'),
q('pl-b1-v-03','B1','vocabulary','„Uwzględnić uwagę klienta” to ___.',['zignorować ją','wziąć ją pod uwagę','przekazać ją konkurencji','odpowiedzieć bez analizy'],1,'Czasownik „uwzględnić” oznacza włączenie danej informacji do decyzji lub planu.'),
q('pl-b1-v-04','B1','vocabulary','Projekt jest „opóźniony”, czyli ___.',['realizowany szybciej','nie przebiega zgodnie z harmonogramem','został rozszerzony','nie ma kosztów'],1,'Opóźnienie oznacza, że realizacja pozostaje w tyle wobec planowanego harmonogramu.'),
q('pl-b1-v-05','B1','vocabulary','„Przejąć obowiązki” znaczy ___.',['zrezygnować z pracy','zacząć wykonywać zadania innej osoby','zmienić umowę','zgłosić urlop'],1,'Zwrot oznacza rozpoczęcie wykonywania zadań należących wcześniej do kogoś innego.'),
q('pl-b1-v-06','B1','vocabulary','Informacja „poufna” powinna być ___.',['publicznie udostępniona','chroniona przed osobami nieuprawnionymi','wydrukowana w wielu kopiach','wysłana bez szyfrowania'],1,'„Poufna” oznacza przeznaczoną wyłącznie dla uprawnionych odbiorców.'),
q('pl-b1-v-07','B1','vocabulary','„Wstępna wersja” dokumentu to wersja ___.',['gotowa do publikacji bez zmian','przygotowana przed ostateczną redakcją','nieważna prawnie w każdym przypadku','zawsze krótsza'],1,'Wersja wstępna poprzedza finalną i może jeszcze wymagać zmian.'),
q('pl-b1-r-01','B1','reading','Dlaczego firma nie wdroży systemu od razu?',['Brakuje pracowników','Najpierw chce sprawdzić go w jednym dziale','System jest nielegalny','Klienci odmówili testów'],1,'Tekst mówi o pilotażu, którego celem jest wykrycie problemów przed wdrożeniem w całej firmie.','Nowy system obsługi klienta zostanie najpierw uruchomiony w dziale sprzedaży. Po sześciu tygodniach firma oceni liczbę błędów i opinie pracowników. Dopiero wtedy zapadnie decyzja o wdrożeniu go w pozostałych działach.'),
q('pl-b1-r-02','B1','reading','Co powinien zrobić pracownik, który nie może uczestniczyć w szkoleniu?',['Nic, szkolenie nie jest potrzebne','Zapisać się na drugi termin','Przyjść bez rejestracji','Wysłać zastępcę bez zgody'],1,'W wiadomości podano alternatywny termin dla osób, które nie mogą uczestniczyć w pierwszym spotkaniu.','Szkolenie z bezpieczeństwa odbędzie się 12 maja. Osoby, które tego dnia pracują poza biurem, powinny zapisać się na dodatkowy termin 19 maja. Obecność na jednym ze spotkań jest obowiązkowa.'),
q('pl-b1-r-03','B1','reading','Jaki jest główny problem autora wiadomości?',['Nie zna ceny usługi','Otrzymał produkt późno i w złym stanie','Chce zmienić adres','Nie potrafi złożyć zamówienia'],1,'Autor wskazuje dwa powiązane problemy: opóźnioną dostawę i uszkodzenie przesyłki.','Zamówienie miało dotrzeć w poniedziałek, ale kurier dostarczył je dopiero w czwartek. Po otwarciu paczki zauważyłem pękniętą obudowę urządzenia. Proszę o informację, czy możliwa jest wymiana bez dodatkowych kosztów.'),
q('pl-b1-r-04','B1','reading','Co wynika z ogłoszenia?',['Biblioteka będzie całkowicie zamknięta','Część usług będzie dostępna w innym miejscu','Zwrot książek zostaje zawieszony','Remont zakończy się jutro'],1,'Ogłoszenie przenosi część usług do budynku obok, więc działalność jest ograniczona, ale nie całkowicie wstrzymana.','Z powodu remontu czytelnia na pierwszym piętrze będzie nieczynna przez dwa tygodnie. Książki można nadal wypożyczać i zwracać w punkcie tymczasowym w budynku obok.'),
q('pl-b1-r-05','B1','reading','Dlaczego termin projektu może się zmienić?',['Zespół zakończył pracę wcześniej','Dostawca nie potwierdził daty dostawy','Budżet został zwiększony','Klient zrezygnował'],1,'Niepewność dotyczy dostawy sprzętu, od której zależy rozpoczęcie kolejnego etapu.','Pierwszy etap projektu zakończyliśmy zgodnie z planem. Nadal jednak czekamy na potwierdzenie terminu dostawy sprzętu. Jeżeli dostawca nie wyśle go do końca tygodnia, rozpoczęcie testów trzeba będzie przesunąć.'),
q('pl-b1-r-06','B1','reading','Jaką decyzję podjęto po ankiecie?',['Zlikwidowano pracę zdalną','Wprowadzono dwa dni pracy zdalnej tygodniowo','Zamknięto biuro','Skrócono tydzień pracy'],1,'Decyzja jest kompromisem między oczekiwaniami pracowników a potrzebą spotkań zespołowych.','Większość pracowników chciała pracować z domu trzy dni w tygodniu, natomiast kierownicy wskazywali na trudności ze współpracą. Firma zdecydowała więc, że od czerwca praca zdalna będzie możliwa przez dwa dni w tygodniu.'),
],
'B2': [
q('pl-b2-g-01','B2','grammar','Gdyby dane zostały opublikowane wcześniej, zespół ___ uniknąć części błędów.',['mógł','mógłby','może','miał'],1,'Zdanie opisuje niezrealizowany warunek z przeszłości; poprawna jest forma przypuszczająca „mógłby”.'),
q('pl-b2-g-02','B2','grammar','Nie ma pewności, ___ proponowane rozwiązanie rzeczywiście obniży koszty.',['że','czy','które','gdyż'],1,'Po wyrażeniu niepewności stosujemy pytanie zależne wprowadzone przez „czy”.'),
q('pl-b2-g-03','B2','grammar','Raport został przygotowany tak, aby wszystkie założenia ___ możliwe do zweryfikowania.',['są','były','będą','być'],1,'Po „tak, aby” w odniesieniu do celu stosujemy formę „były”.'),
q('pl-b2-g-04','B2','grammar','Choć propozycja wydawała się rozsądna, nie zdecydowano się jej ___.',['wdrożyć','wdrażano','wdrożono','wdrażając'],0,'Po konstrukcji „zdecydować się” używamy bezokolicznika: „wdrożyć”.'),
q('pl-b2-g-05','B2','grammar','Im bardziej szczegółowe są przepisy, tym trudniej ___ je do nietypowych sytuacji.',['stosują','zastosować','zastosowali','stosując'],1,'Po bezosobowym „trudniej” potrzebny jest bezokolicznik „zastosować”.'),
q('pl-b2-g-06','B2','grammar','Zespół przedstawił kilka wariantów, z których żaden nie ___ wszystkich warunków.',['spełniał','spełniłby był','spełniając','spełniony'],0,'Zdanie wymaga osobowej formy czasu przeszłego: „żaden nie spełniał”.'),
q('pl-b2-g-07','B2','grammar','O ile nie pojawią się nowe dane, decyzja ___ bez zmian.',['pozostawała','pozostanie','pozostałaby','zostając'],1,'„O ile” wprowadza realny warunek przyszły, dlatego w zdaniu głównym używamy czasu przyszłego.'),
q('pl-b2-v-01','B2','vocabulary','„Uzasadnić decyzję” oznacza ___.',['powtórzyć ją głośniej','przedstawić argumenty, na których się opiera','odłożyć ją bez terminu','ukryć jej skutki'],1,'Uzasadnienie polega na wskazaniu przesłanek i argumentów prowadzących do decyzji.'),
q('pl-b2-v-02','B2','vocabulary','Rozwiązanie „proporcjonalne” do problemu jest ___.',['adekwatne do jego skali','najdroższe z możliwych','całkowicie przypadkowe','pozbawione ograniczeń'],0,'„Proporcjonalne” oznacza odpowiednie do skali, ryzyka i znaczenia problemu.'),
q('pl-b2-v-03','B2','vocabulary','Jeżeli wynik jest „miarodajny”, to ___.',['pozwala na wiarygodną ocenę','jest zawsze korzystny','nie wymaga interpretacji','dotyczy jednej osoby'],0,'Miarodajny wynik dostarcza wiarygodnej podstawy do oceny badanego zjawiska.'),
q('pl-b2-v-04','B2','vocabulary','„Zastrzeżenie” wobec projektu to ___.',['bezwarunkowa zgoda','wątpliwość lub ograniczenie wymagające wyjaśnienia','gotowa instrukcja','dodatkowy budżet'],1,'Zastrzeżenie wskazuje problem, warunek lub wątpliwość, która wymaga odniesienia.'),
q('pl-b2-v-05','B2','vocabulary','„Niejednoznaczny komunikat” ___.',['ma tylko jedną możliwą interpretację','może być rozumiany na kilka sposobów','zawiera wyłącznie liczby','jest zawsze nieprawdziwy'],1,'Niejednoznaczność oznacza możliwość więcej niż jednej interpretacji.'),
q('pl-b2-v-06','B2','vocabulary','„Ograniczyć ryzyko” to ___.',['usunąć wszelką niepewność','zmniejszyć prawdopodobieństwo lub skutki problemu','zwiększyć liczbę decyzji','przenieść odpowiedzialność bez analizy'],1,'Ograniczenie ryzyka nie musi go całkowicie eliminować; zmniejsza jego prawdopodobieństwo lub konsekwencje.'),
q('pl-b2-v-07','B2','vocabulary','„Wdrożenie etapowe” oznacza, że zmiana ___.',['następuje jednocześnie wszędzie','jest wprowadzana kolejno w kilku fazach','nie jest testowana','dotyczy wyłącznie dokumentów'],1,'Wdrożenie etapowe dzieli proces na kolejne fazy, często z oceną wyników po każdej z nich.'),
q('pl-b2-r-01','B2','reading','Jakie stanowisko zajmuje autor?',['Jednoznacznie popiera automatyzację','Odrzuca automatyzację','Dostrzega korzyści, ale domaga się kontroli wyjątków','Uważa, że człowiek nie powinien uczestniczyć w decyzjach'],2,'Autor uznaje zalety automatyzacji, lecz wskazuje konieczność mechanizmu odwoławczego i kontroli nietypowych przypadków.','Automatyzacja prostych decyzji może skrócić czas obsługi i zmniejszyć liczbę przypadkowych błędów. Nie oznacza to jednak, że każdą sprawę należy rozstrzygać według tego samego schematu. System powinien wskazywać przypadki nietypowe i umożliwiać człowiekowi zmianę decyzji wraz z uzasadnieniem.'),
q('pl-b2-r-02','B2','reading','Dlaczego wzrost sprzedaży może być mylący?',['Dane obejmują zbyt wiele lat','Wynika głównie z jednorazowego zamówienia','Firma obniżyła zatrudnienie','Nie uwzględniono kosztów energii'],1,'Jednorazowe zamówienie poprawia wynik okresu, ale nie musi świadczyć o trwałym wzroście popytu.','Sprzedaż w ostatnim kwartale wzrosła o 18 procent. Ponad połowę tej poprawy wygenerowało jednak jednorazowe zamówienie od nowego klienta. Bez niego wzrost byłby niewielki, dlatego zarząd nie chce jeszcze zwiększać stałych kosztów.'),
q('pl-b2-r-03','B2','reading','Jaki jest główny argument przeciwko jednej procedurze?',['Jest zbyt krótka','Nie uwzględnia istotnych różnic między przypadkami','Nie zawiera danych finansowych','Wymaga zbyt mało dokumentów'],1,'Autor wskazuje, że jednolita procedura poprawia spójność, lecz może prowadzić do niedopasowanych decyzji w sytuacjach nietypowych.','Wspólna procedura ułatwia kontrolę i ogranicza rozbieżności między działami. Problem pojawia się wtedy, gdy sprawy podobne na pierwszy rzut oka różnią się pod względem ryzyka, historii klienta lub skutków decyzji. Zbyt sztywne stosowanie reguł może wówczas prowadzić do niesprawiedliwych rezultatów.'),
q('pl-b2-r-04','B2','reading','Co autor uważa za warunek przejrzystości?',['Publikowanie jak największej liczby plików','Możliwość zrozumienia kryteriów i toku decyzji','Usunięcie wszystkich wyjątków','Ukrycie danych osobowych bez wyjaśnienia'],1,'Sama liczba dokumentów nie wystarcza; odbiorca musi móc odtworzyć kryteria i tok rozumowania.','Instytucja publikuje coraz więcej dokumentów, lecz część odbiorców nadal nie rozumie, dlaczego podejmowane są konkretne decyzje. Przejrzystość nie polega wyłącznie na udostępnieniu danych. Wymaga również jasnego opisania kryteriów, wyjątków oraz sposobu ważenia sprzecznych argumentów.'),
q('pl-b2-r-05','B2','reading','Dlaczego pilotaż nie daje jeszcze pełnej odpowiedzi?',['Nie zebrano żadnych danych','Objął grupę, która może różnić się od pozostałych użytkowników','Trwał zbyt długo','Nie zastosowano żadnego systemu'],1,'Wynik może być prawdziwy dla badanej grupy, ale nie musi automatycznie przenosić się na inne środowiska.','Pilotaż nowej aplikacji zakończył się spadkiem liczby błędów. Test przeprowadzono jednak wyłącznie w dziale, którego pracownicy wcześniej korzystali z podobnych narzędzi. Przed wdrożeniem w całej organizacji warto sprawdzić, czy taki sam efekt pojawi się w zespołach o mniejszym doświadczeniu technicznym.'),
q('pl-b2-r-06','B2','reading','Jaki kompromis proponuje tekst?',['Pełną rezygnację z pracy zdalnej','Dowolną liczbę dni pracy zdalnej','Elastyczność połączoną z ustalonymi dniami współpracy zespołowej','Stałą pracę wyłącznie z biura'],2,'Propozycja łączy indywidualną elastyczność z obowiązkową obecnością w dniach wymagających współpracy.','Pracownicy wysoko oceniają możliwość skupienia się w domu, ale wskazują też na słabszy przepływ informacji. Zamiast ustalać identyczny grafik dla wszystkich, firma może pozostawić zespołom dwa elastyczne dni pracy zdalnej i jednocześnie wyznaczyć wspólne dni przeznaczone na spotkania i wymianę wiedzy.'),
],
'C1': [
q('pl-c1-g-01','C1','grammar','Nie tyle zakwestionowano sam cel reformy, ___ sposób, w jaki próbowano go osiągnąć.',['jak','ile','lecz','więc'],1,'Konstrukcja korelacyjna ma postać „nie tyle…, ile…”.'),
q('pl-c1-g-02','C1','grammar','Założenia, na ___ oparto prognozę, nie zostały jasno opisane.',['które','których','którym','którymi'],1,'Po przyimku „na” w znaczeniu podstawy i czasowniku „oparto” używamy miejscownika liczby mnogiej: „na których”.'),
q('pl-c1-g-03','C1','grammar','Jakkolwiek przekonująco ___ argument, nie rozstrzyga on wszystkich wątpliwości.',['brzmi','brzmiałby','brzmieć','zabrzmiał'],0,'„Jakkolwiek” wprowadza ustępstwo odnoszące się do aktualnej cechy argumentu, dlatego właściwy jest czas teraźniejszy.'),
q('pl-c1-g-04','C1','grammar','Gdyby nie pominięto danych z ostatniego kwartału, wniosek mógłby ___ inaczej.',['sformułować','zostać sformułowany','sformułowany','formułując'],1,'Potrzebna jest strona bierna po czasowniku modalnym: „mógłby zostać sformułowany”.'),
q('pl-c1-g-05','C1','grammar','Nie sposób ocenić skuteczności programu, nie ___ jego długofalowych konsekwencji.',['uwzględniając','uwzględniono','uwzględnić','uwzględnia'],0,'Imiesłów „nie uwzględniając” wyraża warunek konieczny dla rzetelnej oceny.'),
q('pl-c1-g-06','C1','grammar','To, że oba zjawiska występują równocześnie, nie oznacza jeszcze, ___ jedno powoduje drugie.',['czy','jakoby','które','o ile'],1,'„Jakoby” wprowadza treść traktowaną z dystansem jako nieudowodnione twierdzenie.'),
q('pl-c1-g-07','C1','grammar','Decyzję podjęto, zanim wszystkie alternatywy zdążono dokładnie ___.',['przeanalizować','przeanalizowano','analizując','przeanalizowane'],0,'Po „zdążono” używamy bezokolicznika: „przeanalizować”.'),
q('pl-c1-v-01','C1','vocabulary','„Przesłanka” argumentu to ___.',['wniosek końcowy','twierdzenie, na którym opiera się rozumowanie','styl wypowiedzi','przykład bez związku'],1,'Przesłanka stanowi podstawę, z której wyprowadza się dalszy wniosek.'),
q('pl-c1-v-02','C1','vocabulary','„Uogólnić wynik” oznacza ___.',['zastosować wniosek do szerszej grupy przypadków','usunąć dane odstające','zmienić metodę pomiaru','powtórzyć badanie'],0,'Uogólnienie rozszerza zakres wniosku poza bezpośrednio badaną próbę.'),
q('pl-c1-v-03','C1','vocabulary','„Pozorna zgodność” to zgodność, która ___.',['jest pełna i potwierdzona','wydaje się istnieć, ale znika po dokładniejszej analizie','wynika z definicji','nie wymaga danych'],1,'„Pozorna” oznacza jedynie powierzchowną, niekoniecznie rzeczywistą.'),
q('pl-c1-v-04','C1','vocabulary','Jeżeli argument „pomija kontekst”, to ___.',['uwzględnia wszystkie okoliczności','ignoruje informacje istotne dla interpretacji','jest napisany krótko','zawiera za dużo przykładów'],1,'Pominięcie kontekstu oznacza nieuwzględnienie warunków zmieniających sens lub wagę danych.'),
q('pl-c1-v-05','C1','vocabulary','„Rozbieżność” między wynikami to ___.',['pełna zgodność','istotna różnica','brak pomiaru','błąd językowy'],1,'Rozbieżność oznacza różnicę lub niespójność między danymi, ocenami albo rezultatami.'),
q('pl-c1-v-06','C1','vocabulary','„Wniosek warunkowy” obowiązuje ___.',['niezależnie od okoliczności','tylko przy spełnieniu określonych założeń','wyłącznie w przeszłości','bez żadnych danych'],1,'Wniosek warunkowy zależy od prawdziwości wskazanych założeń lub warunków.'),
q('pl-c1-v-07','C1','vocabulary','„Zniuansować ocenę” to ___.',['uczynić ją bardziej kategoryczną','uwzględnić różnice, ograniczenia i wyjątki','usunąć argumenty','zastąpić ją liczbą'],1,'Zniuansowanie polega na odejściu od prostego sądu na rzecz bardziej zróżnicowanej oceny.'),
q('pl-c1-r-01','C1','reading','Jaki błąd rozumowania krytykuje autor?',['Oparcie decyzji na zbyt wielu źródłach','Uznanie korelacji za dowód związku przyczynowego','Porównanie dwóch okresów','Podanie danych procentowych'],1,'Autor rozróżnia współwystępowanie zjawisk od dowodu, że jedno z nich powoduje drugie.','Po wdrożeniu programu spadła liczba reklamacji, dlatego część zarządu uznała program za bezpośrednią przyczynę poprawy. W tym samym okresie zmieniono jednak skład zespołu, uproszczono ofertę i ograniczono liczbę zamówień. Samo następstwo czasowe nie pozwala ustalić, który czynnik był decydujący.'),
q('pl-c1-r-02','C1','reading','Dlaczego publikacja danych może nie zwiększyć przejrzystości?',['Dane są zawsze nieprawdziwe','Sposób selekcji i prezentacji może ukrywać tok decyzji','Odbiorcy nie powinni znać kryteriów','Każda publikacja narusza prawo'],1,'Autor podkreśla, że przejrzystość zależy nie tylko od dostępu do danych, lecz także od możliwości zrozumienia ich wyboru i zastosowania.','Organizacja udostępniła setki stron tabel, ale nie wyjaśniła, dlaczego jedne wskaźniki uznano za ważniejsze od innych. Odbiorca może więc zobaczyć materiał źródłowy, a mimo to nie potrafi odtworzyć procesu decyzyjnego. Nadmiar informacji bywa równie nieprzejrzysty jak jej brak.'),
q('pl-c1-r-03','C1','reading','Jaką funkcję pełnią zastrzeżenia w tekście?',['Całkowicie obalają tezę','Ograniczają zakres tezy, ale jej nie unieważniają','Zmieniają temat','Potwierdzają każdy przypadek'],1,'Zastrzeżenia pokazują granice stosowalności tezy i zapobiegają jej nadmiernemu uogólnieniu.','Wyniki badania wskazują, że elastyczny czas pracy poprawił satysfakcję uczestników. Próba obejmowała jednak głównie osoby wykonujące zadania samodzielne, a obserwacja trwała tylko trzy miesiące. Dane wspierają więc ostrożny wniosek, lecz nie uzasadniają twierdzenia, że rozwiązanie sprawdzi się w każdej branży.'),
q('pl-c1-r-04','C1','reading','Na czym polega napięcie opisane przez autora?',['Między szybkością decyzji a możliwością uwzględnienia wyjątków','Między ceną a reklamą','Między liczbą pracowników a powierzchnią biura','Między językiem a grafiką'],0,'Standaryzacja przyspiesza decyzje, ale może osłabić zdolność reagowania na przypadki nietypowe.','Jednolite kryteria pomagają podejmować decyzje szybciej i ograniczają wpływ przypadkowych preferencji. Im bardziej szczegółowy staje się jednak schemat, tym trudniej uwzględnić okoliczności, których wcześniej nie przewidziano. System musi więc godzić przewidywalność z możliwością uzasadnionego odstępstwa.'),
q('pl-c1-r-05','C1','reading','Dlaczego autor odrzuca prosty wybór między dwiema opcjami?',['Obie opcje są identyczne','Problem można rozwiązać rozwiązaniem pośrednim i warunkowym','Nie ma żadnych danych','Decyzja została już podjęta'],1,'Tekst pokazuje, że spór nie musi prowadzić do wyboru skrajności; możliwy jest model łączący zalety obu podejść.','Debata przedstawiana jest często jako wybór między pełną automatyzacją a ręcznym rozpatrywaniem każdej sprawy. To fałszywa alternatywa. System może automatycznie obsługiwać przypadki typowe, a jednocześnie przekazywać człowiekowi sprawy o wysokim ryzyku lub niskiej pewności.'),
q('pl-c1-r-06','C1','reading','Co podważa reprezentatywność próby?',['Jej liczebność jest podana w raporcie','Uczestnicy dobrowolnie zgłosili się do programu i mogli być bardziej zmotywowani','Badanie trwało rok','Zastosowano ankietę'],1,'Dobrowolny udział może powodować błąd selekcji: uczestnicy różnią się od osób, które się nie zgłosiły.','Program oceniono na podstawie wyników osób, które same zgłosiły chęć udziału. Tacy uczestnicy mogli być bardziej zmotywowani i otwarci na zmianę niż przeciętny pracownik. Dobre rezultaty nie muszą więc powtórzyć się po obowiązkowym wdrożeniu w całej organizacji.'),
],
'C2': [
q('pl-c2-g-01','C2','grammar','Nie sposób rozstrzygnąć, czy wynik potwierdza hipotezę, dopóki nie ___ alternatywnych wyjaśnień.',['wykluczono','wykluczy się','wykluczając','wykluczone'],0,'W bezosobowej konstrukcji dotyczącej warunku zakończonej analizy naturalna jest forma „nie wykluczono”.'),
q('pl-c2-g-02','C2','grammar','Choćby argument wydawał się intuicyjny, nie wynika z tego, ___ był metodologicznie poprawny.',['jak','jakoby','że','czyż'],2,'Po „nie wynika z tego” wprowadzamy zdanie dopełnieniowe spójnikiem „że”.'),
q('pl-c2-g-03','C2','grammar','O ile teza ma zachować wartość wyjaśniającą, nie może być sformułowana tak szeroko, by ___ każdy możliwy wynik.',['obejmowała','obejmować','objęła','obejmuje'],1,'Po konstrukcji „tak…, by” i czasowniku modalnym sens wymaga bezokolicznika „obejmować”.'),
q('pl-c2-g-04','C2','grammar','Zarzut nie dotyczy tego, co w raporcie napisano, lecz tego, co świadomie ___.',['pominięto','pomijając','pominięte','pomijałoby'],0,'Konstrukcja kontrastuje dwie czynności dokonane; potrzebna jest bezosobowa forma przeszła „pominięto”.'),
q('pl-c2-g-05','C2','grammar','Niezależnie od tego, jak przekonujące ___ się dane, ich interpretacja zależy od przyjętego modelu.',['wydadzą','wydają','wydawałyby','wydać'],1,'Zdanie formułuje ogólną zależność, dlatego właściwy jest czas teraźniejszy „wydają się”.'),
q('pl-c2-g-06','C2','grammar','Nie tyle brak dowodów osłabia tezę, ile fakt, że dostępne dane można równie dobrze ___ inaczej.',['zinterpretować','zinterpretowano','interpretując','zinterpretowane'],0,'Po „można” stosujemy bezokolicznik „zinterpretować”.'),
q('pl-c2-g-07','C2','grammar','Gdyby kryteria były jawne od początku, spór zapewne nie ___ tak długo.',['trwa','trwałby','trwał','będzie trwał'],1,'Hipotetyczny skutek niezrealizowanego warunku wymaga formy przypuszczającej „trwałby”.'),
q('pl-c2-v-01','C2','vocabulary','„Falsyfikowalna hipoteza” to hipoteza, którą ___.',['można potencjalnie obalić za pomocą danych','należy uznać za prawdziwą','sformułowano niejasno','popiera większość'],0,'Falsyfikowalność oznacza możliwość wskazania obserwacji, która podważyłaby hipotezę.'),
q('pl-c2-v-02','C2','vocabulary','„Retoryczne przesunięcie ciężaru dowodu” polega na ___.',['przedstawieniu nowych danych','żądaniu, by przeciwnik obalił tezę, zamiast samemu ją uzasadnić','doprecyzowaniu pojęć','uznaniu ograniczeń badania'],1,'Ciężar dowodu spoczywa na osobie formułującej twierdzenie, a nie na odbiorcy zobowiązanym je obalać.'),
q('pl-c2-v-03','C2','vocabulary','„Założenie ukryte” to przesłanka, która ___.',['została wyraźnie zdefiniowana','wpływa na wniosek, choć nie została jawnie wypowiedziana','nie ma związku z argumentem','jest wynikiem końcowym'],1,'Ukryte założenie działa w rozumowaniu, mimo że autor nie formułuje go wprost.'),
q('pl-c2-v-04','C2','vocabulary','„Nadmierna ekstrapolacja” oznacza ___.',['ostrożne ograniczenie wniosku','rozszerzenie wniosku poza zakres uzasadniony danymi','powtórzenie badania','zmianę terminologii'],1,'Ekstrapolacja staje się nadmierna, gdy wniosek obejmuje populacje lub warunki nieobjęte dowodami.'),
q('pl-c2-v-05','C2','vocabulary','„Pozorna neutralność” decyzji może oznaczać, że ___.',['nie ma żadnych skutków','ukryte kryteria faworyzują określone grupy mimo formalnie jednakowych reguł','decyzja jest losowa','wszyscy zgadzają się z wynikiem'],1,'Formalnie jednakowa reguła może nie być neutralna, jeśli jej skutki systematycznie różnią się między grupami.'),
q('pl-c2-v-06','C2','vocabulary','„Argument samouszczelniający się” ___.',['dopuszcza możliwość obalenia','interpretuje każdy kontrprzykład jako dodatkowe potwierdzenie','opiera się na jednym źródle','jest zawsze krótki'],1,'Taki argument unika falsyfikacji, ponieważ każdą krytykę włącza jako rzekome potwierdzenie własnej tezy.'),
q('pl-c2-v-07','C2','vocabulary','„Rozróżnienie analityczne” służy do ___.',['łączenia wszystkich pojęć','oddzielenia zjawisk podobnych, lecz istotnie różnych','usuwania wyjątków','zastępowania danych opinią'],1,'Rozróżnienie analityczne pozwala uniknąć mieszania pojęć, które wymagają odmiennych kryteriów oceny.'),
q('pl-c2-r-01','C2','reading','Dlaczego autor uważa tezę za trudną do obalenia?',['Jest poparta wieloma eksperymentami','Każdy możliwy wynik można zinterpretować jako jej potwierdzenie','Zawiera dokładne prognozy','Opiera się na jawnych kryteriach'],1,'Teza została sformułowana tak szeroko, że nie wskazuje wyniku, który mógłby jej zaprzeczyć.','Autorzy twierdzą, że program działa zarówno wtedy, gdy wskaźniki rosną, bo uczestnicy są bardziej aktywni, jak i wtedy, gdy spadają, bo zmiana rzekomo ujawnia ukryte problemy. Jeżeli każdy rezultat uznaje się za potwierdzenie, teza traci zdolność odróżniania sukcesu od porażki.'),
q('pl-c2-r-02','C2','reading','Na czym polega krytyka neutralności procedury?',['Procedura jest zbyt krótka','Jednakowe formalnie kryterium może mieć nierówne skutki z powodu różnic początkowych','Nie zawiera wyjątków językowych','Wyniki są publikowane zbyt szybko'],1,'Autor odróżnia formalne równe traktowanie od rzeczywistego wpływu reguły na grupy znajdujące się w odmiennych warunkach.','Reguła przyznaje wszystkim taki sam czas na dostarczenie dokumentów, dlatego przedstawia się ją jako neutralną. Nie uwzględnia jednak, że część osób otrzymuje informacje później lub ma ograniczony dostęp do wymaganych usług. Jednakowe kryterium może więc utrwalać nierówność wynikającą z odmiennych warunków początkowych.'),
q('pl-c2-r-03','C2','reading','Jaki problem wynika z nadmiaru wskaźników?',['Nie można zebrać żadnych danych','Można po fakcie wybrać te, które wspierają oczekiwaną narrację','Wszystkie wskaźniki dają ten sam wynik','Raport staje się krótszy'],1,'Duża liczba możliwych miar zwiększa swobodę selekcji po analizie, co może tworzyć pozornie przekonujący, lecz niestabilny obraz.','Projekt oceniano za pomocą kilkudziesięciu wskaźników. W raporcie końcowym omówiono głównie te, które wykazały poprawę, choć przed rozpoczęciem badania nie wskazano, które z nich będą kluczowe. Taka swoboda wyboru pozwala zbudować korzystną narrację nawet wtedy, gdy ogólny obraz jest niejednoznaczny.'),
q('pl-c2-r-04','C2','reading','Dlaczego odwołanie do eksperta nie rozstrzyga sporu?',['Ekspert nie ma żadnego doświadczenia','Autorytet nie zastępuje ujawnienia przesłanek i danych','Eksperci nigdy się nie zgadzają','Raport jest zbyt długi'],1,'Kompetencje eksperta mogą zwiększać wiarygodność, ale nie zwalniają z przedstawienia rozumowania podlegającego ocenie.','Decyzję uzasadniono stwierdzeniem, że poparł ją zespół ekspertów. Nie przedstawiono jednak kryteriów, danych ani sposobu rozstrzygania rozbieżności. Odwołanie do autorytetu może być informacją pomocniczą, lecz nie zastępuje argumentu, który odbiorca może samodzielnie prześledzić.'),
q('pl-c2-r-05','C2','reading','Co jest ukrytym założeniem krytykowanego wniosku?',['Że brak skarg oznacza brak problemu','Że wszystkie skargi są prawdziwe','Że procedura jest publiczna','Że liczba pracowników wzrosła'],0,'Wniosek utożsamia brak zgłoszeń z brakiem problemu, pomijając bariery, które mogą powstrzymywać ludzi przed zgłoszeniem.','Po zmianie procedury nie odnotowano formalnych skarg, więc zarząd uznał, że rozwiązanie jest akceptowane. Wniosek ten zakłada jednak, że każda niezadowolona osoba zna procedurę odwoławczą, ufa jej i jest gotowa ponieść koszt zgłoszenia. Brak skarg może oznaczać akceptację, ale może też wynikać z barier.'),
q('pl-c2-r-06','C2','reading','Jak autor rozróżnia trafność i rzetelność?',['Uznaje je za synonimy','Rzetelny pomiar może być powtarzalny, ale mierzyć nie to, co powinien','Trafność dotyczy wyłącznie kosztów','Rzetelność oznacza zgodność z opinią większości'],1,'Tekst odróżnia powtarzalność wyniku od tego, czy narzędzie rzeczywiście mierzy zamierzoną cechę.','Test daje niemal identyczne wyniki przy każdym powtórzeniu, co świadczy o wysokiej rzetelności. Jeżeli jednak mierzy głównie znajomość specjalistycznego słownictwa zamiast zdolności rozwiązywania problemów, pozostaje mało trafny. Stabilny wynik nie gwarantuje więc, że oceniana jest właściwa cecha.'),
],
}

LISTENING_REPLACEMENTS = {
'B1': [
('pl-b1-l-01','Spotkanie zaczniemy pół godziny później, ponieważ pierwszy prelegent utknął w pociągu. Sala i kolejność pozostałych wystąpień nie zmieniają się.','Co zmieniono w planie?',['Miejsce spotkania','Godzinę rozpoczęcia','Kolejność wszystkich prezentacji','Datę wydarzenia'],1,'Zmienia się wyłącznie godzina rozpoczęcia; miejsce i dalsza kolejność pozostają bez zmian.'),
('pl-b1-l-02','Reklamacja została uznana. Klient może wybrać bezpłatną wymianę produktu albo pełny zwrot pieniędzy, ale koszt dodatkowych akcesoriów nie podlega zwrotowi.','Jakie możliwości ma klient?',['Tylko naprawę','Wymianę lub zwrot ceny produktu','Zwrot wszystkich kosztów wraz z akcesoriami','Wyłącznie rabat'],1,'Nagranie proponuje dwie opcje dotyczące produktu, lecz wyłącza koszt akcesoriów.'),
('pl-b1-l-03','Proszę przesłać poprawioną wersję najpóźniej w czwartek rano. Chcę ją sprawdzić przed spotkaniem z klientem, które odbędzie się po południu.','Dlaczego dokument jest potrzebny rano?',['Aby wysłać go do księgowości','Aby sprawdzić go przed spotkaniem','Aby zmienić termin spotkania','Aby skrócić prezentację'],1,'Termin poranny umożliwia kontrolę dokumentu przed popołudniowym spotkaniem.'),
('pl-b1-l-04','Szkolenie nie jest obowiązkowe dla wszystkich. Muszą wziąć w nim udział osoby, które zatwierdzają płatności, a pozostali pracownicy mogą zapisać się dobrowolnie.','Kto ma obowiązek uczestniczyć?',['Wszyscy pracownicy','Osoby zatwierdzające płatności','Wyłącznie nowi pracownicy','Tylko kierownicy działów'],1,'Obowiązek dotyczy funkcji zatwierdzania płatności, nie stanowiska ani stażu.'),
],
'B2': [
('pl-b2-l-01','Wynik kwartalny wzrósł o piętnaście procent, ale prawie cały wzrost pochodzi z jednego kontraktu. To dobra wiadomość dla płynności, lecz zbyt mało, by mówić o trwałej zmianie popytu.','Jak mówca interpretuje wynik?',['Jako dowód trwałego wzrostu','Jako korzystny, ale niewystarczający do dalekich wniosków','Jako całkowicie nieistotny','Jako sygnał natychmiastowej redukcji kosztów'],1,'Mówca uznaje krótkoterminową korzyść, ale odrzuca uogólnienie na trwały trend.'),
('pl-b2-l-02','Jednolita procedura zmniejszyła liczbę błędów, jednak pracownicy zaczęli stosować ją również w sytuacjach, dla których nie była projektowana. Problemem nie jest sama reguła, lecz brak mechanizmu uzasadnionego wyjątku.','Co według mówcy wymaga poprawy?',['Całkowite usunięcie procedury','Możliwość odstępstwa w nietypowych przypadkach','Zwiększenie liczby obowiązkowych kroków','Rezygnacja z kontroli'],1,'Krytyka dotyczy braku elastycznego wyjątku, a nie samego istnienia procedury.'),
('pl-b2-l-03','Praca zdalna poprawiła koncentrację przy zadaniach indywidualnych, ale nowi pracownicy rzadziej prosili o pomoc i wolniej poznawali nieformalne zasady zespołu.','Jaki wniosek najlepiej oddaje wypowiedź?',['Praca zdalna działa jednakowo dla wszystkich','Korzyści zależą od rodzaju zadania i doświadczenia pracownika','Nowi pracownicy pracują szybciej w domu','Współpraca nie zmieniła się'],1,'Nagranie pokazuje zróżnicowane skutki zależne od zadania i doświadczenia.'),
('pl-b2-l-04','Nie kwestionuję celu reformy, ale przedstawione dane nie pokazują, czy wybrane narzędzie jest skuteczniejsze od tańszych alternatyw. Bez takiego porównania trudno ocenić proporcjonalność rozwiązania.','Czego brakuje w uzasadnieniu?',['Opisu celu','Porównania z alternatywami','Listy pracowników','Daty publikacji'],1,'Mówca akceptuje cel, lecz domaga się porównania skuteczności i kosztów innych możliwości.'),
],
'C1': [
('pl-c1-l-01','Publikowanie kolejnych tabel może tworzyć wrażenie otwartości, lecz nie wyjaśnia, dlaczego jedne kryteria otrzymały większą wagę niż inne. Przejrzystość wymaga możliwości odtworzenia toku decyzji, a nie tylko dostępu do materiału.','Jaka jest główna teza?',['Większa liczba danych zawsze zwiększa zaufanie','Przejrzystość zależy od zrozumiałości procesu decyzyjnego','Tabele należy całkowicie usunąć','Kryteria nie powinny być publikowane'],1,'Autor odróżnia sam dostęp do danych od możliwości zrozumienia sposobu ich użycia.'),
('pl-c1-l-02','Zastrzeżenia dotyczą krótkiego czasu obserwacji i niereprezentatywnej próby. Nie unieważniają wyniku, ale ograniczają zakres, w jakim można go przenosić na inne zespoły.','Jaką funkcję pełnią zastrzeżenia?',['Obalają wynik','Ograniczają możliwość uogólnienia','Potwierdzają wszystkie zastosowania','Dotyczą wyłącznie stylu raportu'],1,'Zastrzeżenia zawężają zakres wniosku, nie negując obserwowanego efektu w badanej próbie.'),
('pl-c1-l-03','Spadek liczby skarg nastąpił po zmianie procedury, ale w tym samym czasie ograniczono liczbę klientów i zmieniono kanał kontaktu. Kolejność wydarzeń nie wystarcza, by przypisać efekt jednemu czynnikowi.','Przed jakim błędem ostrzega mówca?',['Przed użyciem zbyt wielu danych','Przed utożsamieniem następstwa czasowego z przyczynowością','Przed porównaniem okresów','Przed publikacją wyników'],1,'Mówca wskazuje na czynniki współwystępujące i odrzuca prosty wniosek przyczynowy.'),
('pl-c1-l-04','Automatyczne decyzje sprawdzają się w sprawach typowych, lecz system powinien przekazywać człowiekowi przypadki o niskiej pewności lub wysokim ryzyku. Nie jest to rezygnacja z automatyzacji, tylko wyznaczenie jej granic.','Jakie rozwiązanie proponuje mówca?',['Pełną automatyzację','Całkowicie ręczną obsługę','Model hybrydowy zależny od ryzyka i pewności','Losowy podział spraw'],2,'Propozycja łączy automatyzację przypadków typowych z kontrolą człowieka w sprawach ryzykownych.'),
],
'C2': [
('pl-c2-l-01','Hipotezę sformułowano tak szeroko, że wzrost wskaźnika ma świadczyć o sukcesie programu, a jego spadek o ujawnieniu ukrytych problemów. Skoro żaden możliwy wynik nie może jej podważyć, hipoteza traci wartość wyjaśniającą.','Co jest głównym zarzutem?',['Hipoteza jest zbyt szczegółowa','Hipoteza nie jest falsyfikowalna','Zebrano za mało wskaźników','Program trwał zbyt krótko'],1,'Każdy wynik jest interpretowany jako potwierdzenie, więc nie istnieje obserwacja mogąca obalić hipotezę.'),
('pl-c2-l-02','Formalnie wszystkim wyznaczono ten sam termin, lecz nie wszyscy otrzymali informację w tym samym momencie ani mieli jednakowy dostęp do wymaganych usług. Równa reguła może więc działać nierówno, jeśli pomija różnice warunków początkowych.','Jak mówca podważa neutralność reguły?',['Wskazuje na różne skutki wynikające z nierównych warunków','Twierdzi, że terminy są zawsze niesprawiedliwe','Odrzuca wszelkie wspólne zasady','Krytykuje język komunikatu'],0,'Mówca odróżnia formalną równość reguły od jej rzeczywistego wpływu na osoby w różnych warunkach.'),
('pl-c2-l-03','Raport analizował kilkadziesiąt wskaźników, lecz przed badaniem nie wskazano, które z nich będą decydujące. Po fakcie wybrano głównie wyniki korzystne, co zwiększa ryzyko dopasowania narracji do danych.','Na czym polega problem metodologiczny?',['Na zbyt małej liczbie danych','Na selekcji korzystnych wskaźników po analizie','Na braku jakichkolwiek pomiarów','Na użyciu jednego języka'],1,'Brak wcześniejszego wskazania kluczowych miar pozwala wybierać po fakcie wyniki wspierające oczekiwaną tezę.'),
('pl-c2-l-04','Odwołanie do opinii ekspertów może zwiększać zaufanie, ale nie zastępuje ujawnienia przesłanek, danych i sposobu rozstrzygania sporów. Bez tego odbiorca zna autorytet źródła, lecz nie może ocenić argumentu.','Dlaczego autorytet ekspertów nie wystarcza?',['Eksperci nie mają wiedzy','Nie pozwala samodzielnie prześledzić uzasadnienia','Każda opinia eksperta jest błędna','Dane są zawsze poufne'],1,'Autorytet może wspierać argument, lecz nie zastępuje jawnego toku rozumowania.'),
],
}

SPEAKING_REPLACEMENTS = {
'B1': [
('pl-b1-s-01','Od przyszłego miesiąca pracownicy będą mogli rozpoczynać pracę między siódmą a dziewiątą. Każdy zespół musi jednak ustalić wspólne godziny, w których wszyscy są dostępni na spotkania i konsultacje.',55),
('pl-b1-s-02','Proszę przesłać poprawioną wersję raportu do czwartku rano. Chciałbym sprawdzić liczby, komentarze i źródła przed spotkaniem z klientem zaplanowanym na godzinę piętnastą.',55),
('pl-b1-s-03','Firma uznała reklamację i zaproponowała klientowi bezpłatną wymianę produktu albo pełny zwrot ceny. Koszt dodatkowych akcesoriów nie zostanie jednak zwrócony.',55),
('pl-b1-s-04','Nowy system ułatwia codzienną pracę, ale wymaga dokładnego przestrzegania zasad bezpieczeństwa. Pracownicy nie powinni udostępniać haseł ani pozostawiać otwartej sesji bez nadzoru.',55),
],
'B2': [
('pl-b2-s-01','Wyniki sprzedaży wzrosły o osiemnaście procent, jednak większość poprawy wynika z jednego dużego zamówienia. Zarząd uznał więc, że jest za wcześnie na zwiększanie stałych kosztów, dopóki wzrost nie potwierdzi się w kolejnych kwartałach.',75),
('pl-b2-s-02','Wspólna procedura ogranicza liczbę błędów i ułatwia kontrolę, lecz w nietypowych przypadkach może prowadzić do niedopasowanych decyzji. Dlatego system powinien umożliwiać uzasadnione odstępstwo oraz późniejszą ocenę jego skutków.',75),
('pl-b2-s-03','Praca zdalna poprawiła koncentrację podczas zadań indywidualnych, ale osłabiła nieformalną wymianę wiedzy. Szczególnie nowi pracownicy rzadziej prosili o pomoc i wolniej poznawali praktyczne zasady obowiązujące w zespole.',75),
('pl-b2-s-04','Nie kwestionujemy celu reformy, lecz mamy wątpliwości, czy wybrane narzędzie jest proporcjonalne do problemu. Przed podjęciem decyzji należy porównać jego skuteczność, koszty oraz możliwe rozwiązania alternatywne.',75),
],
'C1': [
('pl-c1-s-01','Publikowanie większej liczby danych nie gwarantuje przejrzystości, jeżeli odbiorca nadal nie wie, dlaczego jedne kryteria uznano za ważniejsze od innych. Rzeczywista otwartość wymaga przedstawienia toku decyzji, sposobu ważenia argumentów oraz zasad stosowania wyjątków.',95),
('pl-c1-s-02','Zastrzeżenia dotyczące krótkiego czasu obserwacji i niereprezentatywnej próby nie obalają wyniku, lecz ograniczają jego zakres. Dane mogą uzasadniać ostrożny wniosek o badanej grupie, ale nie pozwalają automatycznie przenosić go na wszystkie branże i środowiska.',95),
('pl-c1-s-03','Jednolite reguły sprzyjają spójności i ograniczają wpływ przypadkowych preferencji, ale mogą pomijać różnice istotne dla oceny konkretnej sprawy. Dobry system powinien więc łączyć przewidywalne kryteria z możliwością uzasadnionego odstępstwa podlegającego późniejszej kontroli.',95),
('pl-c1-s-04','Badanie pokazuje rzeczywisty efekt wśród uczestników pilotażu, jednak jego wyników nie można bezpośrednio uogólniać. Uczestnicy zgłosili się dobrowolnie, mieli większe doświadczenie techniczne, a obserwacja trwała zaledwie trzy miesiące.',95),
],
'C2': [
('pl-c2-s-01','Reforma usuwa najbardziej widoczne skutki problemu, lecz nie zmienia bodźców, które ten problem stale odtwarzają. Krótkoterminowa poprawa może więc prowadzić do przedwczesnego poczucia sukcesu, podczas gdy mechanizm odpowiedzialny za wcześniejsze nieprawidłowości pozostaje nienaruszony.',115),
('pl-c2-s-02','Pozorna przejrzystość może wynikać nie tylko z braku informacji, ale również z ich nadmiaru. Jeżeli instytucja publikuje setki tabel bez wskazania kryteriów selekcji i sposobu ich ważenia, odbiorca otrzymuje materiał źródłowy, lecz nadal nie może odtworzyć rzeczywistego procesu decyzyjnego.',115),
('pl-c2-s-03','Wniosek może być zgodny z dostępnymi danymi, a mimo to pozostawać słabo uzasadniony, jeżeli nie wykluczono równie prawdopodobnych wyjaśnień. Zgodność z obserwacją nie wystarcza, gdy kilka konkurencyjnych hipotez przewiduje dokładnie ten sam rezultat.',115),
('pl-c2-s-04','Nie tyle brak danych budzi wątpliwości, ile sposób ich selekcji oraz interpretacji w świetle wcześniej przyjętych założeń. Jeżeli kluczowe wskaźniki wybiera się dopiero po poznaniu wyników, łatwo zbudować przekonującą narrację, która nie utrzyma się w kolejnym badaniu.',115),
],
}

main = load('pl.json')
listening = load('pl-listening.json')
speaking = load('pl-speaking.json')

improve_basic_explanations(main['questions'])
main['questions'] = [x for x in main['questions'] if x['level'] in {'A1','A2'}]
for level in ['B1','B2','C1','C2']:
    main['questions'].extend(MAIN_REPLACEMENTS[level])
main['version'] = '4.0.0-professional-direct'
main['questionCount'] = len(main['questions'])

listening['questions'] = [x for x in listening['questions'] if x['level'] in {'A1','A2'}]
for level in ['B1','B2','C1','C2']:
    for qid, transcript, prompt, options, answer, explanation in LISTENING_REPLACEMENTS[level]:
        listening['questions'].append({
            'id': qid, 'level': level, 'skill': 'listening',
            'transcript': transcript, 'prompt': prompt, 'options': options,
            'answer': answer, 'maxPlays': 2, 'explanation': explanation,
        })
listening['version'] = '4.0.0-professional-direct'
listening['questionCount'] = len(listening['questions'])

speaking['questions'] = [x for x in speaking['questions'] if x['level'] in {'A1','A2'}]
for level in ['B1','B2','C1','C2']:
    for qid, text, duration in SPEAKING_REPLACEMENTS[level]:
        speaking['questions'].append({
            'id': qid, 'level': level, 'skill': 'speaking',
            'prompt': 'Przeczytaj tekst na głos w naturalnym tempie.',
            'referenceText': text,
            'maxDurationSec': duration,
        })
speaking['version'] = '4.0.0-professional-direct'
speaking['questionCount'] = len(speaking['questions'])

assert main['questionCount'] == 120
assert listening['questionCount'] == 40
assert speaking['questionCount'] == 28
for bank in (main, listening, speaking):
    assert {x['level'] for x in bank['questions']} == set(LEVELS)
    assert len({x['id'] for x in bank['questions']}) == len(bank['questions'])

save('pl.json', main)
save('pl-listening.json', listening)
save('pl-speaking.json', speaking)
print('Polish v4 direct banks created:', main['questionCount'], listening['questionCount'], speaking['questionCount'])
