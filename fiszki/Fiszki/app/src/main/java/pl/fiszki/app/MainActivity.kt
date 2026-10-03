package pl.fiszki.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import kotlinx.coroutines.launch
import pl.fiszki.app.ui.FiszkiApp
import pl.fiszki.app.ui.theme.ThemeSettings

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = (application as FiszkiApplication).container
        setContent {
            // null = ustawienia jeszcze się wczytują (ułamek sekundy) — widać tło okna z themes.xml.
            val settings: ThemeSettings? by app.settings.settings.collectAsStateWithLifecycle(initialValue = null)
            settings?.let { s ->
                FiszkiApp(app.repository, s) { new -> app.appScope.launch { app.settings.save(new) } }
            }
        }
    }
}
