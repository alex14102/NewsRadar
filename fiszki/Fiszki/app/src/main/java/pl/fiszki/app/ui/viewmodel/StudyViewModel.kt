package pl.fiszki.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.Deck
import pl.fiszki.app.data.Rating
import pl.fiszki.app.data.Repository

data class StudyUi(
    val loading: Boolean = true,
    val deck: Deck? = null,
    val card: Card? = null,
    val total: Int = 0,
    val done: Int = 0,
    val flipped: Boolean = false,
)

/** Sesja nauki. deckId < 0 → wszystkie talie. Kolejka jest ustalana raz, na starcie sesji. */
class StudyViewModel(private val repo: Repository, private val deckId: Long) : ViewModel() {
    private val queue = ArrayDeque<Card>()
    private var busy = false

    private val _ui = MutableStateFlow(StudyUi())
    val ui: StateFlow<StudyUi> = _ui.asStateFlow()

    init {
        viewModelScope.launch {
            val deck = if (deckId >= 0) repo.deckOnce(deckId) else null
            queue.addAll(repo.dueCards(deckId.takeIf { it >= 0 }))
            _ui.value = StudyUi(loading = false, deck = deck, card = queue.firstOrNull(), total = queue.size)
        }
    }

    fun flip() = _ui.update { it.copy(flipped = true) }

    fun rate(r: Rating) {
        val card = queue.firstOrNull() ?: return
        if (busy) return
        busy = true
        viewModelScope.launch {
            try {
                val updated = repo.rate(card, r)
                queue.removeFirstOrNull()
                // „ZNOWU” → karta wraca na koniec tej samej sesji.
                if (r == Rating.AGAIN) queue.addLast(updated)
                _ui.update {
                    it.copy(card = queue.firstOrNull(), done = it.total - queue.size, flipped = false)
                }
            } finally {
                busy = false
            }
        }
    }
}
