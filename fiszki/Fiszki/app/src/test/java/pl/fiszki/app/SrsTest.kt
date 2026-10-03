package pl.fiszki.app

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.Rating
import pl.fiszki.app.data.Srs

class SrsTest {
    private val fresh = Card(id = 1, deckId = 1, front = "a", back = "b")

    @Test
    fun againResetsInterval() {
        val c = Srs.review(fresh, Rating.AGAIN, now = 0)
        assertEquals(0, c.intervalDays)
        assertEquals(60_000L, c.dueAtMillis)
    }

    @Test
    fun goodTwiceGivesSixDays() {
        val once = Srs.review(fresh, Rating.GOOD, now = 0)
        val twice = Srs.review(once, Rating.GOOD, now = 0)
        assertEquals(1, once.intervalDays)
        assertEquals(6, twice.intervalDays)
    }

    @Test
    fun easyIsLongerThanGood() {
        assertTrue(Srs.review(fresh, Rating.EASY).intervalDays > Srs.review(fresh, Rating.GOOD).intervalDays)
    }
}
