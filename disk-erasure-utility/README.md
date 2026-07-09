# Disk Erasure Utility

Interaktywne narzedzie CLI (Python + Rich) do bezpiecznego, trwalego
wymazywania danych z dyskow. Skanuje urzadzenia blokowe, odczytuje dane
S.M.A.R.T., wykrywa zaszyfrowane wolumeny, wykonuje wymazywanie wieloma
metodami z monitorowaniem postepu w czasie rzeczywistym i zapisuje raporty
JSON z kazdej operacji.

## Bezpieczenstwo

Narzedzie **odmawia** wymazania:

- dysku systemowego (urzadzenie stojace za `/`, `/boot`, `/boot/efi`),
- nosnika, z ktorego uruchomiono system live/pendrive,
- aktywnych partycji swap,
- pseudo-urzadzen: `/dev/loop*`, `/dev/ram*`, `/dev/zram*`,
- dodatkowych urzadzen wpisanych w `config.yaml` (`safety.protected_extra`).

Te sprawdzenia sa wykonywane w kodzie (`EraseManager.assert_safe_to_erase`)
niezaleznie od interfejsu uzytkownika, wiec nie da sie ich pominac z menu
ani z linii polecen. Dodatkowo przed kazdym wymazaniem wymagane jest
potwierdzenie (wpisanie `WYMAZ`), chyba ze `erase.confirm_required: false`
w konfiguracji lub flaga `--yes` w trybie CLI.

## Wymagania

- Linux (wykorzystuje `lsblk`, `findmnt`, `blkid`, `/proc/mounts`, `/proc/swaps`).
- Python 3.9+.
- Root (bezposredni zapis na `/dev/sdX` wymaga uprawnien administratora).
- Opcjonalnie: `smartmontools` (SMART), `cryptsetup` (szczegoly LUKS),
  `hdparm` (ATA Secure Erase), `nvme-cli` (NVMe format), `util-linux`
  (`blkdiscard`, `lsblk`, `findmnt`).

## Pobranie

```bash
git clone https://github.com/alex14102/NewsRadar.git
cd NewsRadar
git checkout claude/disk-erasure-utility-3ncnnr
cd disk-erasure-utility
```

## Instalacja

```bash
./install.sh
```

Skrypt wykrywa menedzer pakietow (`apt`, `dnf`, `pacman`), instaluje
zaleznosci systemowe (`smartmontools`, `hdparm`, `nvme-cli`, `util-linux`)
oraz biblioteki Python z `requirements.txt` **bezposrednio na maszynie**
(bez virtualenv), tak aby narzedzie dzialalo od razu po `sudo python3 main.py`.

Instalacja reczna (bez skryptu):

```bash
pip3 install -r requirements.txt
# lub na dystrybucjach z PEP 668 (Debian/Ubuntu 23.04+):
pip3 install --break-system-packages -r requirements.txt
```

## Uzycie

### Tryb interaktywny (menu)

```bash
sudo python3 main.py
```

Menu pozwala: skanowac dyski, przegladac SMART, wykrywac szyfrowanie,
wymazywac wybrane dyski oraz przegladac raporty i ustawienia. Przed
wyborem metody wymazywania wyswietlana jest tabela wszystkich metod z
przypisana norma/standardem, liczba przebiegow i opisem. Podczas
wymazywania widoczny jest zywy pasek postepu Rich dla kazdego dysku
(numer przebiegu, procent, predkosc, ETA, temperatura SMART i status),
aktualizowany w czasie rzeczywistym i bezpieczny do przerwania Ctrl+C.

### Tryb nieinteraktywny (CLI)

```bash
# lista urzadzen blokowych
sudo python3 main.py scan

# lista metod wymazywania wraz z norma/standardem i liczba przebiegow
python3 main.py methods

# dane SMART konkretnego dysku
sudo python3 main.py smart /dev/sdb

# wykrycie szyfrowania na partycji
sudo python3 main.py crypto /dev/sdb1

# wymazanie dysku metoda 3-przebiegowa DoD, z potwierdzeniem i paskiem postepu
sudo python3 main.py erase /dev/sdb --method dod3

# jak wyzej, bez pytania o potwierdzenie (np. w skryptach automatyzacji)
sudo python3 main.py erase /dev/sdb --method zero --yes

# lista zapisanych raportow
python3 main.py reports
```

## Metody wymazywania (normy niszczenia danych)

Metody nadpisywania odzwierciedlaja powszechnie uznane normy sanityzacji
nosnikow (referencje w ramach ISO/IEC 27040 - bezpieczenstwo pamieci
masowych - odsylaja do konkretnych algorytmow nadpisywania takich jak
ponizsze). Pelna lista dostepna jest w aplikacji (`main.py methods` lub
opcja [4] w menu, przed wyborem metody).

| ID             | Norma / standard              | Przebiegi | Opis                                                     |
|----------------|--------------------------------|-----------|-----------------------------------------------------------|
| `zero`         | Podstawowe czyszczenie         | 1         | Zapis samymi zerami                                        |
| `random`       | Podstawowe czyszczenie         | 1         | Jeden przebieg danych z CSPRNG                              |
| `nist_clear`   | NIST SP 800-88 Rev.1 - Clear   | 1         | Logiczne czyszczenie zgodne z NIST SP 800-88                |
| `dod3`         | DoD 5220.22-M                  | 3         | `0x00`, `0xFF`, dane losowe                                 |
| `dod7`         | DoD 5220.22-M ECC              | 7         | Rozszerzony wariant z dodatkowymi przebiegami               |
| `vsitr`        | VSITR (Niemcy, BSI)            | 7         | Naprzemiennie `0x00`/`0xFF`, ostatni przebieg `0xAA`        |
| `hmg_is5`      | HMG Infosec Standard 5 (UK)    | 3         | `0x00`, `0xFF`, losowe + weryfikacja koncowa                |
| `gost_r50739`  | GOST R 50739-95 (Rosja)        | 1         | Jeden przebieg danych losowych (klasa ochrony 6)            |
| `schneier`     | Bruce Schneier's Algorithm     | 7         | `0xFF`, `0x00`, nastepnie 5 przebiegow losowych             |
| `gutmann`      | Gutmann Method                 | 35        | Pelne 35 przebiegow z oryginalnej publikacji Gutmanna (1996)|
| `blkdiscard`   | ATA/NVMe TRIM (discard)        | sprzetowo | Szybkie oznaczenie blokow jako nieuzywane (SSD/NVMe)        |
| `secure-erase` | ATA Security Feature Set       | sprzetowo | ATA Secure Erase przez `hdparm`                             |
| `nvme-format`  | NVMe Format NVM Command        | sprzetowo | Kryptograficzne kasowanie kluczy przez `nvme-cli`           |

Po ostatnim przebiegu (jesli `erase.verify: true`) narzedzie odczytuje
probki sektorow, aby potwierdzic czytelnosc nosnika i - dla przebiegow
deterministycznych (rowniez wieloznakowych wzorcow, jak w metodzie
Gutmanna) - zgodnosc z oczekiwanym, ciaglym wzorcem bajtow na calej
dlugosci nosnika (nadpisywanie zachowuje ciaglosc fazy wzorca pomiedzy
kolejnymi fragmentami zapisu, wiec weryfikacja jest poprawna niezaleznie
od rozmiaru fragmentu ustawionego w `erase.chunk_size_mb`).

## Ustawienia (`config.yaml`)

Plik jest tworzony automatycznie z wartosciami domyslnymi przy pierwszym
uruchomieniu, jesli nie istnieje. Zobacz przykladowy `config.yaml` w tym
katalogu - opisuje kazda sekcje: `logging`, `reports`, `erase`, `smart`,
`crypto`, `safety`, `monitor`.

## Logi i raporty

- Logi: JSON Lines w `logs/app.jsonl` (kazda operacja, polecenie
  zewnetrzne i blad jako osobny obiekt JSON z znacznikiem czasu).
- Raporty: JSON w katalogu `reports/`, jeden plik na operacje
  wymazywania, zawiera dane dysku, metode, statusy przebiegow, wyniki
  weryfikacji i dane SMART z chwili wykonania.

## Przerywanie (Ctrl+C)

Nacisniecie Ctrl+C podczas operacji wymazywania ustawia flage bezpiecznego
zatrzymania - trwajacy zapis konczy biezacy fragment, wykonuje `fsync`,
zamyka deskryptor pliku i oznacza operacje jako `interrupted` w raporcie,
zamiast przerywac proces w nieokreslonym momencie.
