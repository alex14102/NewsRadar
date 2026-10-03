package pl.fiszki.app.data

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import pl.fiszki.app.ui.theme.Accents
import pl.fiszki.app.ui.theme.PaletteId
import pl.fiszki.app.ui.theme.TextSize
import pl.fiszki.app.ui.theme.ThemeSettings
import java.io.IOException

/** Ustawienia z ekranu „Wygląd” zapisywane w DataStore Preferences. */
class SettingsStore(private val store: DataStore<Preferences>) {
    private object Keys {
        val palette = stringPreferencesKey("palette")
        val accent = intPreferencesKey("accent") // indeks w Accents, -1 = akcent motywu
        val chamfer = booleanPreferencesKey("chamfer")
        val hatch = booleanPreferencesKey("hatch")
        val deco = booleanPreferencesKey("deco")
        val textSize = stringPreferencesKey("text_size")
    }

    val settings: Flow<ThemeSettings> = store.data
        .catch { if (it is IOException) emit(emptyPreferences()) else throw it }
        .map { p ->
            val d = ThemeSettings()
            ThemeSettings(
                palette = PaletteId.entries.firstOrNull { it.name == p[Keys.palette] } ?: d.palette,
                accent = p[Keys.accent]?.let { Accents.getOrNull(it) },
                chamfer = p[Keys.chamfer] ?: d.chamfer,
                hatch = p[Keys.hatch] ?: d.hatch,
                deco = p[Keys.deco] ?: d.deco,
                textSize = TextSize.entries.firstOrNull { it.name == p[Keys.textSize] } ?: d.textSize,
            )
        }

    suspend fun save(s: ThemeSettings) {
        store.edit { p ->
            p[Keys.palette] = s.palette.name
            p[Keys.accent] = s.accent?.let { Accents.indexOf(it) } ?: -1
            p[Keys.chamfer] = s.chamfer
            p[Keys.hatch] = s.hatch
            p[Keys.deco] = s.deco
            p[Keys.textSize] = s.textSize.name
        }
    }
}
