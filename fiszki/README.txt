FISZKI — paczka startowa
========================

Fiszki/                 projekt Android Studio (Kotlin + Jetpack Compose), 5 ekranów:
                        Start, Nauka, Nowa fiszka, Statystyki, Wygląd (motywy działają w całej aplikacji)
projekt-design/         projekt graficzny z kanwy (.dc.html + canvas.json) — wzór wyglądu
INSTRUKCJA_KALI.txt     instalacja Android Studio na Kali i uruchomienie projektu
INSTRUKCJA_APK.txt      jak zbudować podpisany APK i zainstalować go na telefonie
PROMPT_DLA_CLAUDE.txt   gotowe polecenie dla Claude'a, żeby rozwijał aplikację dalej

Stan: zadania 1–8 z PROMPT_DLA_CLAUDE.txt zrobione:
  - fonty Barlow Condensed + JetBrains Mono (res/font, licencje w Fiszki/licenses/)
  - baza Room (Deck, Card, ReviewLog) + DAO z Flow + ViewModele; przykładowe talie
    wstawiane tylko przy pierwszym uruchomieniu
  - ustawienia wyglądu zapisywane w DataStore
  - prawdziwe statystyki z historii powtórek (seria, 7 dni, skuteczność, opanowane)
  - ekran talii: lista kart, edycja, usuwanie, zmiana nazwy/usunięcie talii, nowa talia
  - ikona adaptacyjna (też ikona tematyczna Android 13+)
  - podpisywanie release przez keystore.properties
Nawigacja: stuknięcie talii na ekranie TALIE otwiera listę jej kart (tam ▶ UCZ_SIĘ);
▶ START_SESJI na górze uczy ze wszystkich talii.
