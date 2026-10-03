package pl.fiszki.app.data

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import kotlin.math.max
import kotlin.math.roundToInt

@Entity(tableName = "decks")
data class Deck(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val short: String,
    val path: String,
)

@Entity(
    tableName = "cards",
    foreignKeys = [
        ForeignKey(
            entity = Deck::class,
            parentColumns = ["id"],
            childColumns = ["deckId"],
            onDelete = ForeignKey.CASCADE,
        ),
    ],
    indices = [Index("deckId"), Index("dueAtMillis")],
)
data class Card(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val deckId: Long,
    val front: String,
    val back: String,
    val ipa: String = "",
    val example: String = "",
    val ease: Double = 2.5,
    val intervalDays: Int = 0,
    val reps: Int = 0,
    val dueAtMillis: Long = 0L,
)

/**
 * Jedna ocena karty. Bez klucza obcego — historia (i statystyki) zostaje,
 * nawet gdy karta albo talia zostanie usunięta.
 * day = numer dnia (LocalDate.toEpochDay) w strefie telefonu w chwili powtórki.
 */
@Entity(tableName = "review_log", indices = [Index("day")])
data class ReviewLog(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val cardId: Long,
    val deckId: Long,
    val rating: Rating,
    val reviewedAt: Long,
    val day: Long,
)

/** Wynik zapytania: ile powtórek danego dnia i ile z nich bez „ZNOWU”. */
data class DayStat(val day: Long, val reviews: Int, val correct: Int)

enum class Rating(val label: String) {
    AGAIN("ZNOWU"), HARD("TRUDNE"), GOOD("DOBRZE"), EASY("ŁATWE")
}

/** Uproszczony algorytm SM-2 (jak w Anki/SuperMemo). */
object Srs {
    private const val DAY = 24L * 60 * 60 * 1000

    fun review(card: Card, r: Rating, now: Long = System.currentTimeMillis()): Card {
        val q = when (r) {
            Rating.AGAIN -> 1
            Rating.HARD -> 3
            Rating.GOOD -> 4
            Rating.EASY -> 5
        }
        val ease = (card.ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))).coerceAtLeast(1.3)
        if (q < 3) {
            return card.copy(ease = ease, reps = 0, intervalDays = 0, dueAtMillis = now + 60_000)
        }
        val reps = card.reps + 1
        var interval = when (reps) {
            1 -> 1
            2 -> 6
            else -> (card.intervalDays * ease).roundToInt()
        }
        if (r == Rating.EASY) interval = max(interval + 1, (interval * 1.3).roundToInt())
        if (r == Rating.HARD) interval = max(1, (interval * 0.6).roundToInt())
        return card.copy(ease = ease, reps = reps, intervalDays = interval, dueAtMillis = now + interval * DAY)
    }

    /** Tekst pod przyciskiem oceny: „<1M”, „1D”, „6D”… */
    fun previewLabel(card: Card, r: Rating): String {
        val n = review(card, r, 0L).intervalDays
        return if (n == 0) "<1M" else "${n}D"
    }
}
