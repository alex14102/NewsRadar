package pl.fiszki.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import pl.fiszki.app.data.Repository
import pl.fiszki.app.navigation.AppNav
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.FiszkiTheme
import pl.fiszki.app.ui.theme.ThemeSettings

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { FiszkiApp() }
    }
}

@Composable
fun FiszkiApp() {
    // TODO: przenieść do ViewModelu (teraz dane giną np. po obrocie ekranu).
    val repo = remember { Repository() }
    var settings by remember { mutableStateOf(ThemeSettings()) }

    FiszkiTheme(settings) {
        val t = Fiszki.t
        Box(
            Modifier
                .fillMaxSize()
                .background(Brush.radialGradient(listOf(t.c.glow, t.c.bg)))
                .systemBarsPadding()
        ) {
            AppNav(repo, settings) { settings = it }
        }
    }
}
