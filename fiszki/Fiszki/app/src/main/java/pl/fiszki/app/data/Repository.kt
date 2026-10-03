package pl.fiszki.app.data

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.setValue

/**
 * Dane trzymane w pamięci (znikają po zamknięciu aplikacji).
 * TODO: zastąpić bazą Room + ViewModel.
 */
class Repository {
    val decks = mutableStateListOf(
        Deck(1, "Angielski B2", "EN", "/LANG/EN"),
        Deck(2, "Hiszpański — podstawy", "ES", "/LANG/ES"),
        Deck(3, "Sieci komputerowe", "NET", "/IT/TCP"),
        Deck(4, "Matematyka dyskretna", "MD", "/STUDIA"),
    )
    val cards = mutableStateListOf<Card>()

    var reviewedToday by mutableIntStateOf(0)
        private set
    var correctToday by mutableIntStateOf(0)
        private set

    /** PRZYKŁADOWA wartość — do policzenia z historii powtórek. */
    val streakDays = 12

    private var nextId = 1L

    init {
        fun add(deck: Long, front: String, back: String, ipa: String = "", ex: String = "") {
            cards.add(Card(nextId++, deck, front, back, ipa, ex))
        }
        add(1, "reluctant", "niechętny, oporny", "/rɪˈlʌk.tənt/", "She was reluctant to admit her mistake.")
        add(1, "thorough", "dokładny, gruntowny", "/ˈθʌr.ə/", "The audit was thorough.")
        add(1, "to deploy", "wdrożyć", "/dɪˈplɔɪ/", "We deploy the app on Friday.")
        add(1, "ubiquitous", "wszechobecny", "/juːˈbɪk.wɪ.təs/")
        add(1, "to emerge", "wyłonić się", "/ɪˈmɜːdʒ/")
        add(2, "hola", "cześć")
        add(2, "gracias", "dziękuję")
        add(2, "la casa", "dom")
        add(2, "aprender", "uczyć się")
        add(3, "Port SSH", "22/TCP")
        add(3, "Warstwa 3 OSI", "sieciowa (IP)")
        add(3, "Co robi DHCP?", "automatycznie przydziela adresy IP")
        add(3, "Adres pętli zwrotnej IPv6", "::1")
        add(4, "Liczba podzbiorów zbioru n-elementowego", "2^n")
        add(4, "Ile krawędzi ma drzewo o n wierzchołkach?", "n − 1")
    }

    fun due(deckId: Long?, now: Long = System.currentTimeMillis()): List<Card> =
        cards.filter { (deckId == null || it.deckId == deckId) && it.dueAtMillis <= now }

    fun rate(card: Card, r: Rating) {
        val i = cards.indexOfFirst { it.id == card.id }
        if (i >= 0) cards[i] = Srs.review(cards[i], r)
        reviewedToday++
        if (r != Rating.AGAIN) correctToday++
    }

    fun addCard(deckId: Long, front: String, back: String, example: String, reversed: Boolean) {
        cards.add(Card(nextId++, deckId, front, back, example = example))
        if (reversed) cards.add(Card(nextId++, deckId, back, front, example = example))
    }

    fun retentionLabel(): String =
        if (reviewedToday == 0) "—" else "${correctToday * 100 / reviewedToday}%"

    /** Ostatnie 7 dni. Wcześniejsze dni to PRZYKŁADOWE liczby, ostatni = dzisiaj. */
    fun weekHistory(): List<Pair<String, Int>> = listOf(
        "PN" to 32, "WT" to 45, "ŚR" to 18, "CZ" to 51, "PT" to 27, "SB" to 38, "DZIŚ" to reviewedToday,
    )
}
