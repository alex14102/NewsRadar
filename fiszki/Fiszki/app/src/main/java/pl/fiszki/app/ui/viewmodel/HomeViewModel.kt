package pl.fiszki.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import pl.fiszki.app.data.Deck
import pl.fiszki.app.data.Repository
import pl.fiszki.app.data.Stats
import pl.fiszki.app.data.epochDay

data class DeckRow(val deck: Deck, val total: Int, val due: Int)

data class HomeUi(
    val loaded: Boolean = false,
    val decks: List<DeckRow> = emptyList(),
    val dueAll: Int = 0,
    val doneToday: Int = 0,
    val streak: Int = 0,
)

class HomeViewModel(private val repo: Repository) : ViewModel() {
    val ui: StateFlow<HomeUi> = combine(repo.decks, repo.cards, repo.dayStats, repo.ticks()) { decks, cards, stats, now ->
        val today = epochDay(now)
        val dueCards = cards.filter { it.dueAtMillis <= now }
        HomeUi(
            loaded = true,
            decks = decks.map { d ->
                DeckRow(d, total = cards.count { it.deckId == d.id }, due = dueCards.count { it.deckId == d.id })
            },
            dueAll = dueCards.size,
            doneToday = Stats.reviewsOn(stats, today),
            streak = Stats.streak(stats.map { it.day }, today),
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), HomeUi())

    fun addDeck(name: String, short: String) {
        viewModelScope.launch { repo.addDeck(name, short) }
    }
}
