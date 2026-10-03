package pl.fiszki.app

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import pl.fiszki.app.data.DayStat
import pl.fiszki.app.data.Stats
import pl.fiszki.app.data.deckCode
import pl.fiszki.app.data.epochDay
import pl.fiszki.app.data.kart
import java.time.LocalDate
import java.time.ZoneOffset

class StatsTest {
    private val today = LocalDate.of(2026, 10, 3).toEpochDay() // sobota

    @Test
    fun streakCountsConsecutiveDaysEndingToday() {
        assertEquals(3, Stats.streak(listOf(today, today - 1, today - 2, today - 4), today))
    }

    @Test
    fun streakFromYesterdayStillAlive() {
        assertEquals(2, Stats.streak(listOf(today - 1, today - 2), today))
    }

    @Test
    fun streakBrokenAfterGap() {
        assertEquals(0, Stats.streak(listOf(today - 2, today - 3), today))
        assertEquals(0, Stats.streak(emptyList(), today))
    }

    @Test
    fun weekHasSevenDaysEndingToday() {
        val week = Stats.week(listOf(DayStat(today, 5, 4), DayStat(today - 6, 2, 2), DayStat(today - 9, 9, 9)), today)
        assertEquals(listOf("ND", "PN", "WT", "ŚR", "CZ", "PT", "DZIŚ"), week.map { it.label })
        assertEquals(listOf(2, 0, 0, 0, 0, 0, 5), week.map { it.count })
        assertEquals(true, week.last().isToday)
    }

    @Test
    fun retentionInRange() {
        val stats = listOf(DayStat(today, 4, 3), DayStat(today - 1, 6, 6), DayStat(today - 10, 10, 0))
        assertEquals(90, Stats.retention(stats, today - 6, today))
        assertEquals(75, Stats.retention(stats, today, today))
        assertNull(Stats.retention(stats, today - 5, today - 2))
    }

    @Test
    fun epochDayUsesZone() {
        val millis = LocalDate.of(2026, 10, 3).atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli()
        assertEquals(today, epochDay(millis, ZoneOffset.UTC))
        assertEquals(today - 1, epochDay(millis, ZoneOffset.ofHours(-2)))
    }

    @Test
    fun polishPlural() {
        assertEquals(listOf("1 karta", "2 karty", "5 kart", "12 kart", "22 karty", "0 kart"), listOf(1, 2, 5, 12, 22, 0).map(::kart))
    }

    @Test
    fun deckCodeFromNameOrShort() {
        assertEquals("ANG", deckCode("", "angielski"))
        assertEquals("EN", deckCode("en", "Angielski"))
        assertEquals("TAL", deckCode("", "— —"))
    }
}
