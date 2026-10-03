package pl.fiszki.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.Deck
import pl.fiszki.app.data.Repository

data class DeckUi(
    val loaded: Boolean = false,
    val deck: Deck? = null,
    val cards: List<Card> = emptyList(),
    val due: Int = 0,
    val now: Long = 0L,
)

/** Lista kart jednej talii + zmiana nazwy / usuwanie. */
class DeckViewModel(private val repo: Repository, private val deckId: Long) : ViewModel() {
    val ui: StateFlow<DeckUi> = combine(repo.deck(deckId), repo.cardsOf(deckId), repo.ticks()) { deck, cards, now ->
        DeckUi(loaded = true, deck = deck, cards = cards, due = cards.count { it.dueAtMillis <= now }, now = now)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), DeckUi())

    fun rename(name: String, short: String) {
        val deck = ui.value.deck ?: return
        viewModelScope.launch { repo.renameDeck(deck, name, short) }
    }

    fun deleteDeck() {
        val deck = ui.value.deck ?: return
        viewModelScope.launch { repo.deleteDeck(deck) }
    }

    fun deleteCard(card: Card) {
        viewModelScope.launch { repo.deleteCard(card) }
    }
}
