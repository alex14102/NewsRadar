package pl.fiszki.app.data.db

import androidx.room.Database
import androidx.room.RoomDatabase
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.Deck
import pl.fiszki.app.data.ReviewLog

@Database(entities = [Deck::class, Card::class, ReviewLog::class], version = 1, exportSchema = false)
abstract class FiszkiDatabase : RoomDatabase() {
    abstract fun deckDao(): DeckDao
    abstract fun cardDao(): CardDao
    abstract fun reviewLogDao(): ReviewLogDao
}
