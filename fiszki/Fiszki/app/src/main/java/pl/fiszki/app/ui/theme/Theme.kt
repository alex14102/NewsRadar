package pl.fiszki.app.ui.theme

import androidx.compose.foundation.shape.CutCornerShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

enum class TextSize(val label: String, val wordSp: Int) {
    S("MAŁY", 34), M("ŚREDNI", 42), L("DUŻY", 52)
}

/** Ustawienia z ekranu „Wygląd”. TODO: zapisywać w DataStore. */
data class ThemeSettings(
    val palette: PaletteId = PaletteId.CYBER,
    val accent: AccentOption? = null,
    val chamfer: Boolean = true,
    val hatch: Boolean = true,
    val deco: Boolean = true,
    val textSize: TextSize = TextSize.M,
)

class Tokens(
    val c: FiszkiColors,
    val accent: Color,
    val onAccent: Color,
    val settings: ThemeSettings,
) {
    /** Ścięte narożniki 45° (lewy-górny i prawy-dolny) albo zaokrąglenie, zależnie od ustawień. */
    fun shape(cut: Dp): Shape =
        if (settings.chamfer) CutCornerShape(topStart = cut, bottomEnd = cut)
        else RoundedCornerShape(if (cut > 14.dp) 14.dp else cut)
}

val LocalTokens = staticCompositionLocalOf<Tokens> { error("Brak FiszkiTheme") }

object Fiszki {
    val t: Tokens
        @Composable @ReadOnlyComposable get() = LocalTokens.current
}

/**
 * Fonty. TODO: wrzucić do res/font pliki Barlow Condensed (Bold/SemiBold)
 * i JetBrains Mono, a potem podmienić na FontFamily(Font(R.font.…)).
 */
object Fonts {
    val Display: FontFamily = FontFamily.SansSerif
    val Mono: FontFamily = FontFamily.Monospace
}

@Composable
fun FiszkiTheme(settings: ThemeSettings, content: @Composable () -> Unit) {
    val c = Palettes.getValue(settings.palette)
    val tokens = Tokens(
        c = c,
        accent = settings.accent?.color ?: c.accent,
        onAccent = settings.accent?.on ?: c.onAccent,
        settings = settings,
    )
    val scheme = if (settings.palette == PaletteId.PAPER) {
        lightColorScheme(
            primary = c.primary, onPrimary = c.onPrimary,
            background = c.bg, onBackground = c.ink,
            surface = c.surface, onSurface = c.ink,
        )
    } else {
        darkColorScheme(
            primary = c.primary, onPrimary = c.onPrimary,
            background = c.bg, onBackground = c.ink,
            surface = c.surface, onSurface = c.ink,
        )
    }
    MaterialTheme(colorScheme = scheme) {
        CompositionLocalProvider(
            LocalTokens provides tokens,
            LocalContentColor provides c.ink,
            content = content,
        )
    }
}
