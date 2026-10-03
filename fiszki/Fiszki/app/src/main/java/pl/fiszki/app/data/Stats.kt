package pl.fiszki.app.data

import java.time.DayOfWeek
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

/** Numer dnia (jak LocalDate.toEpochDay) dla chwili [millis] w strefie [zone]. */
fun epochDay(millis: Long, zone: ZoneId = ZoneId.systemDefault()): Long =
    Instant.ofEpochMilli(millis).atZone(zone).toLocalDate().toEpochDay()

/** Polska odmiana: 1 karta, 2 karty, 5 kart, 22 karty… */
fun plural(n: Int, one: String, few: String, many: String): String {
    val mod10 = n % 10
    val mod100 = n % 100
    return when {
        n == 1 -> one
        mod10 in 2..4 && mod100 !in 12..14 -> few
        else -> many
    }
}

fun kart(n: Int) = "$n ${plural(n, "karta", "karty", "kart")}"
fun dni(n: Int) = "$n ${if (n == 1) "dzień" else "dni"}"

data class DayCount(val label: String, val count: Int, val isToday: Boolean)

/** Statystyki liczone z historii powtórek (ReviewLog → DayStat). */
object Stats {
    /** Karta jest „opanowana”, gdy jej odstęp to co najmniej tyle dni. */
    const val MASTERED_DAYS = 21

    /**
     * Seria: ile kolejnych dni z co najmniej jedną powtórką, licząc wstecz od dziś.
     * Jeśli dziś jeszcze nic nie było, seria z wczoraj nadal trwa (do północy).
     */
    fun streak(days: Collection<Long>, today: Long): Int {
        val set = days.toHashSet()
        var d = when {
            today in set -> today
            today - 1 in set -> today - 1
            else -> return 0
        }
        var n = 0
        while (d in set) {
            n++
            d--
        }
        return n
    }

    /** Ostatnie 7 dni (od najstarszego); ostatni element to dziś. */
    fun week(stats: List<DayStat>, today: Long): List<DayCount> {
        val byDay = stats.associateBy { it.day }
        return (6 downTo 0).map { back ->
            val day = today - back
            DayCount(
                label = if (back == 0) "DZIŚ" else dayLabel(LocalDate.ofEpochDay(day).dayOfWeek),
                count = byDay[day]?.reviews ?: 0,
                isToday = back == 0,
            )
        }
    }

    /** Skuteczność w % (oceny inne niż ZNOWU) dla dni od [fromDay] do [toDay]; null = brak powtórek. */
    fun retention(stats: List<DayStat>, fromDay: Long, toDay: Long): Int? {
        val range = stats.filter { it.day in fromDay..toDay }
        val total = range.sumOf { it.reviews }
        if (total == 0) return null
        return range.sumOf { it.correct } * 100 / total
    }

    fun reviewsOn(stats: List<DayStat>, day: Long): Int = stats.firstOrNull { it.day == day }?.reviews ?: 0

    private fun dayLabel(d: DayOfWeek) = when (d) {
        DayOfWeek.MONDAY -> "PN"
        DayOfWeek.TUESDAY -> "WT"
        DayOfWeek.WEDNESDAY -> "ŚR"
        DayOfWeek.THURSDAY -> "CZ"
        DayOfWeek.FRIDAY -> "PT"
        DayOfWeek.SATURDAY -> "SB"
        DayOfWeek.SUNDAY -> "ND"
    }
}
