package pl.fiszki.app

import android.app.Application
import android.content.Context
import androidx.datastore.preferences.preferencesDataStore
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import pl.fiszki.app.data.Repository
import pl.fiszki.app.data.SettingsStore
import pl.fiszki.app.data.db.FiszkiDatabase

private val Context.themeDataStore by preferencesDataStore(name = "theme_settings")

class FiszkiApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}

/** Ręczne „DI”: jedna baza, jedno repozytorium i jeden magazyn ustawień na całą aplikację. */
class AppContainer(context: Context) {
    /** Zadania, które mają się dokończyć niezależnie od ekranu (np. zapis ustawień). */
    val appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    private val db: FiszkiDatabase = Room.databaseBuilder(context, FiszkiDatabase::class.java, "fiszki.db")
        .addCallback(object : RoomDatabase.Callback() {
            // Wywoływane tylko raz — gdy plik bazy powstaje (pierwsze uruchomienie).
            override fun onCreate(db: SupportSQLiteDatabase) {
                appScope.launch { repository.seedSampleData() }
            }
        })
        .build()

    val repository: Repository by lazy {
        Repository(db.deckDao(), db.cardDao(), db.reviewLogDao())
    }

    val settings = SettingsStore(context.themeDataStore)
}
