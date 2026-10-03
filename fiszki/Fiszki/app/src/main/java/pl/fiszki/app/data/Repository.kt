package pl.fiszki.app.data

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import pl.fiszki.app.data.db.CardDao
import pl.fiszki.app.data.db.DeckDao
import pl.fiszki.app.data.db.ReviewLogDao

/** Jedno miejsce dostępu do danych (Room). Ekrany korzystają z niego przez ViewModele. */
class Repository(
    private val deckDao: DeckDao,
    private val cardDao: CardDao,
    private val logDao: ReviewLogDao,
    private val clock: () -> Long = System::currentTimeMillis,
) {
    val decks: Flow<List<Deck>> = deckDao.observeAll()
    val cards: Flow<List<Card>> = cardDao.observeAll()
    val dayStats: Flow<List<DayStat>> = logDao.observeDayStats()

    /** Bieżący czas co [periodMs] — żeby karty „do powtórki” i „dziś” same się odświeżały. */
    fun ticks(periodMs: Long = 30_000): Flow<Long> = flow {
        while (true) {
            emit(clock())
            delay(periodMs)
        }
    }

    fun now(): Long = clock()

    fun deck(id: Long): Flow<Deck?> = deckDao.observe(id)
    fun cardsOf(deckId: Long): Flow<List<Card>> = cardDao.observeByDeck(deckId)

    suspend fun deckOnce(id: Long): Deck? = deckDao.get(id)
    suspend fun card(id: Long): Card? = cardDao.get(id)

    /** deckId == null → wszystkie talie. */
    suspend fun dueCards(deckId: Long?): List<Card> = cardDao.due(deckId ?: -1L, clock())

    /** Zapisuje ocenę: nowy termin karty (SM-2) + wpis w historii. Zwraca kartę po zmianie. */
    suspend fun rate(card: Card, r: Rating): Card {
        val now = clock()
        val updated = Srs.review(card, r, now)
        cardDao.update(updated)
        logDao.insert(
            ReviewLog(cardId = card.id, deckId = card.deckId, rating = r, reviewedAt = now, day = epochDay(now))
        )
        return updated
    }

    suspend fun addCard(deckId: Long, front: String, back: String, ipa: String, example: String, reversed: Boolean) {
        cardDao.insert(Card(deckId = deckId, front = front, back = back, ipa = ipa, example = example))
        if (reversed) cardDao.insert(Card(deckId = deckId, front = back, back = front, example = example))
    }

    suspend fun updateCard(card: Card) = cardDao.update(card)
    suspend fun deleteCard(card: Card) = cardDao.delete(card)

    suspend fun addDeck(name: String, short: String): Long {
        val code = deckCode(short, name)
        return deckDao.insert(Deck(name = name, short = code, path = "/USER/$code"))
    }

    suspend fun renameDeck(deck: Deck, name: String, short: String) {
        val code = deckCode(short, name)
        deckDao.update(deck.copy(name = name, short = code))
    }

    suspend fun deleteDeck(deck: Deck) = deckDao.delete(deck)

    /** Przykładowe talie — wywoływane tylko raz, przy tworzeniu bazy (pierwsze uruchomienie). */
    suspend fun seedSampleData() {
        val en = deckDao.insert(Deck(name = "Angielski B2", short = "EN", path = "/LANG/EN"))
        val es = deckDao.insert(Deck(name = "Hiszpański — podstawy", short = "ES", path = "/LANG/ES"))
        val net = deckDao.insert(Deck(name = "Sieci komputerowe", short = "NET", path = "/IT/TCP"))
        val md = deckDao.insert(Deck(name = "Matematyka dyskretna", short = "MD", path = "/STUDIA"))
        cardDao.insertAll(
            listOf(
                Card(deckId = en, front = "reluctant", back = "niechętny, oporny", ipa = "/rɪˈlʌk.tənt/", example = "She was reluctant to admit her mistake."),
                Card(deckId = en, front = "thorough", back = "dokładny, gruntowny", ipa = "/ˈθʌr.ə/", example = "The audit was thorough."),
                Card(deckId = en, front = "to deploy", back = "wdrożyć", ipa = "/dɪˈplɔɪ/", example = "We deploy the app on Friday."),
                Card(deckId = en, front = "ubiquitous", back = "wszechobecny", ipa = "/juːˈbɪk.wɪ.təs/"),
                Card(deckId = en, front = "to emerge", back = "wyłonić się", ipa = "/ɪˈmɜːdʒ/"),
                Card(deckId = es, front = "hola", back = "cześć"),
                Card(deckId = es, front = "gracias", back = "dziękuję"),
                Card(deckId = es, front = "la casa", back = "dom"),
                Card(deckId = es, front = "aprender", back = "uczyć się"),
                Card(deckId = net, front = "Port SSH", back = "22/TCP"),
                Card(deckId = net, front = "Warstwa 3 OSI", back = "sieciowa (IP)"),
                Card(deckId = net, front = "Co robi DHCP?", back = "automatycznie przydziela adresy IP"),
                Card(deckId = net, front = "Adres pętli zwrotnej IPv6", back = "::1"),
                Card(deckId = md, front = "Liczba podzbiorów zbioru n-elementowego", back = "2^n"),
                Card(deckId = md, front = "Ile krawędzi ma drzewo o n wierzchołkach?", back = "n − 1"),
            )
        )
    }
}

/** Kod talii do etykiety [EN]: podany przez użytkownika albo 3 pierwsze litery nazwy. */
fun deckCode(short: String, name: String): String {
    val src = short.ifBlank { name }
    val code = src.filter { it.isLetterOrDigit() }.take(if (short.isBlank()) 3 else 4).uppercase()
    return code.ifEmpty { "TAL" }
}
