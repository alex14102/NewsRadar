package pl.fiszki.app.data.db

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.DayStat
import pl.fiszki.app.data.Deck
import pl.fiszki.app.data.ReviewLog

@Dao
interface DeckDao {
    @Query("SELECT * FROM decks ORDER BY id")
    fun observeAll(): Flow<List<Deck>>

    @Query("SELECT * FROM decks WHERE id = :id")
    fun observe(id: Long): Flow<Deck?>

    @Query("SELECT * FROM decks WHERE id = :id")
    suspend fun get(id: Long): Deck?

    @Insert
    suspend fun insert(deck: Deck): Long

    @Update
    suspend fun update(deck: Deck)

    /** Karty talii znikają razem z nią (ForeignKey.CASCADE). */
    @Delete
    suspend fun delete(deck: Deck)
}

@Dao
interface CardDao {
    @Query("SELECT * FROM cards ORDER BY id")
    fun observeAll(): Flow<List<Card>>

    @Query("SELECT * FROM cards WHERE deckId = :deckId ORDER BY id")
    fun observeByDeck(deckId: Long): Flow<List<Card>>

    @Query("SELECT * FROM cards WHERE id = :id")
    suspend fun get(id: Long): Card?

    /** deckId < 0 → wszystkie talie. */
    @Query("SELECT * FROM cards WHERE dueAtMillis <= :now AND (:deckId < 0 OR deckId = :deckId) ORDER BY dueAtMillis, id")
    suspend fun due(deckId: Long, now: Long): List<Card>

    @Insert
    suspend fun insert(card: Card): Long

    @Insert
    suspend fun insertAll(cards: List<Card>)

    @Update
    suspend fun update(card: Card)

    @Delete
    suspend fun delete(card: Card)
}

@Dao
interface ReviewLogDao {
    @Insert
    suspend fun insert(log: ReviewLog)

    @Query(
        "SELECT day, COUNT(*) AS reviews, " +
            "SUM(CASE WHEN rating = 'AGAIN' THEN 0 ELSE 1 END) AS correct " +
            "FROM review_log GROUP BY day ORDER BY day"
    )
    fun observeDayStats(): Flow<List<DayStat>>
}
