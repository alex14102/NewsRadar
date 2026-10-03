package pl.fiszki.app.ui.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.Deck
import pl.fiszki.app.data.Repository

/**
 * Nowa fiszka (cardId < 0) albo edycja istniejącej.
 * presetDeckId ≥ 0 → ta talia jest wybrana na starcie.
 */
class CardEditorViewModel(
    private val repo: Repository,
    private val cardId: Long,
    presetDeckId: Long,
) : ViewModel() {
    val isEdit = cardId >= 0

    val decks: StateFlow<List<Deck>?> =
        repo.decks.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    private var original: Card? = null

    /** Gotowe do edycji (przy edycji: karta wczytana). */
    var ready by mutableStateOf(!isEdit)
        private set
    var deckId by mutableLongStateOf(presetDeckId)
    var front by mutableStateOf("")
    var back by mutableStateOf("")
    var ipa by mutableStateOf("")
    var example by mutableStateOf("")
    var reversed by mutableStateOf(true)

    val valid: Boolean get() = front.isNotBlank() && back.isNotBlank() && deckId >= 0

    init {
        if (isEdit) {
            viewModelScope.launch {
                repo.card(cardId)?.let { c ->
                    original = c
                    deckId = c.deckId
                    front = c.front
                    back = c.back
                    ipa = c.ipa
                    example = c.example
                }
                ready = true
            }
        }
    }

    /** Gdy nic nie wybrano (albo wybrana talia zniknęła) — pierwsza z listy. */
    fun ensureDeck(decks: List<Deck>) {
        if (decks.isNotEmpty() && decks.none { it.id == deckId }) deckId = decks.first().id
    }

    fun save(onDone: () -> Unit) {
        if (!valid) return
        viewModelScope.launch {
            val o = original
            if (o != null) {
                repo.updateCard(
                    o.copy(deckId = deckId, front = front.trim(), back = back.trim(), ipa = ipa.trim(), example = example.trim())
                )
            } else {
                repo.addCard(deckId, front.trim(), back.trim(), ipa.trim(), example.trim(), reversed)
            }
            onDone()
        }
    }
}
