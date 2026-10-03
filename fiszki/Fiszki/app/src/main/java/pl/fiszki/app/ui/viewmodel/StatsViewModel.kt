package pl.fiszki.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import pl.fiszki.app.data.DayCount
import pl.fiszki.app.data.Repository
import pl.fiszki.app.data.Stats
import pl.fiszki.app.data.epochDay

data class StatsUi(
    val streak: Int = 0,
    /** Skuteczność z ostatnich 7 dni w %, null = brak powtórek. */
    val retentionWeek: Int? = null,
    val retentionToday: Int? = null,
    val week: List<DayCount> = emptyList(),
    val totalCards: Int = 0,
    val mastered: Int = 0,
    val reviewedToday: Int = 0,
    val reviewsAllTime: Int = 0,
)

class StatsViewModel(repo: Repository) : ViewModel() {
    val ui: StateFlow<StatsUi> = combine(repo.cards, repo.dayStats, repo.ticks(60_000)) { cards, stats, now ->
        val today = epochDay(now)
        StatsUi(
            streak = Stats.streak(stats.map { it.day }, today),
            retentionWeek = Stats.retention(stats, today - 6, today),
            retentionToday = Stats.retention(stats, today, today),
            week = Stats.week(stats, today),
            totalCards = cards.size,
            mastered = cards.count { it.intervalDays >= Stats.MASTERED_DAYS },
            reviewedToday = Stats.reviewsOn(stats, today),
            reviewsAllTime = stats.sumOf { it.reviews },
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), StatsUi())
}
