package pl.fiszki.app.ui.theme

import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import pl.fiszki.app.R

/** Fonty z res/font (licencja SIL OFL — patrz licenses/). */
object Fonts {
    /** Barlow Condensed — nagłówki, wersaliki. */
    val Display: FontFamily = FontFamily(
        Font(R.font.barlow_condensed_semibold, FontWeight.Medium),
        Font(R.font.barlow_condensed_semibold, FontWeight.SemiBold),
        Font(R.font.barlow_condensed_bold, FontWeight.Bold),
    )

    /** JetBrains Mono — etykiety terminala. */
    val Mono: FontFamily = FontFamily(
        Font(R.font.jetbrains_mono_regular, FontWeight.Normal),
        Font(R.font.jetbrains_mono_bold, FontWeight.Bold),
    )
}
