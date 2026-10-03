package pl.fiszki.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import pl.fiszki.app.data.Repository
import pl.fiszki.app.navigation.AppNav
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.FiszkiTheme
import pl.fiszki.app.ui.theme.ThemeSettings

@Composable
fun FiszkiApp(repo: Repository, settings: ThemeSettings, onSettings: (ThemeSettings) -> Unit) {
    FiszkiTheme(settings) {
        val t = Fiszki.t
        Box(
            Modifier
                .fillMaxSize()
                .background(Brush.radialGradient(listOf(t.c.glow, t.c.bg)))
                .systemBarsPadding()
        ) {
            AppNav(repo, settings, onSettings)
        }
    }
}
