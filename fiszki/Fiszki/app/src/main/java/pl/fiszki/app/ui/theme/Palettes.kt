package pl.fiszki.app.ui.theme

import androidx.compose.ui.graphics.Color

/** Komplet kolorów jednego motywu (wartości z projektu na kanwie „Fiszki”). */
data class FiszkiColors(
    val name: String,
    val bg: Color,
    val glow: Color,
    val surface: Color,
    val raised: Color,
    val line: Color,
    val ink: Color,
    val muted: Color,
    val primary: Color,
    val onPrimary: Color,
    val accent: Color,
    val onAccent: Color,
)

enum class PaletteId { CYBER, NEON, AMBER, ICE, PAPER }

val Palettes: Map<PaletteId, FiszkiColors> = mapOf(
    PaletteId.CYBER to FiszkiColors(
        name = "CYBER",
        bg = Color(0xFF1C2627), glow = Color(0xFF263334), surface = Color(0xFF1E2829),
        raised = Color(0xFF2E3B3C), line = Color(0xFF47585A),
        ink = Color(0xFFE6EDEA), muted = Color(0xFF8A9C9B),
        primary = Color(0xFF34C3AE), onPrimary = Color(0xFF0F1A1A),
        accent = Color(0xFFD6EA3C), onAccent = Color(0xFF141A12),
    ),
    PaletteId.NEON to FiszkiColors(
        name = "NEON",
        bg = Color(0xFF1A1726), glow = Color(0xFF272140), surface = Color(0xFF211D30),
        raised = Color(0xFF2E2942), line = Color(0xFF4A4462),
        ink = Color(0xFFEEEAF7), muted = Color(0xFF9D96B5),
        primary = Color(0xFFE0479E), onPrimary = Color(0xFF1A0F18),
        accent = Color(0xFF4FE3F0), onAccent = Color(0xFF0F1A1C),
    ),
    PaletteId.AMBER to FiszkiColors(
        name = "AMBER TERM",
        bg = Color(0xFF1E1A14), glow = Color(0xFF2C261C), surface = Color(0xFF26211A),
        raised = Color(0xFF332C22), line = Color(0xFF5A4E3C),
        ink = Color(0xFFF2EBDD), muted = Color(0xFFA89A82),
        primary = Color(0xFFE8A23A), onPrimary = Color(0xFF1A1206),
        accent = Color(0xFFF2E3B3), onAccent = Color(0xFF1A1206),
    ),
    PaletteId.ICE to FiszkiColors(
        name = "ICE",
        bg = Color(0xFF16202B), glow = Color(0xFF1F2D3B), surface = Color(0xFF1C2834),
        raised = Color(0xFF263544), line = Color(0xFF3F5163),
        ink = Color(0xFFE6F0F8), muted = Color(0xFF8EA3B6),
        primary = Color(0xFF5AA9F0), onPrimary = Color(0xFF0A1520),
        accent = Color(0xFFE6F1FA), onAccent = Color(0xFF0A1520),
    ),
    PaletteId.PAPER to FiszkiColors(
        name = "PAPIER",
        bg = Color(0xFFECEEE8), glow = Color(0xFFF6F7F3), surface = Color(0xFFFFFFFF),
        raised = Color(0xFFDDE1D8), line = Color(0xFFAEB6AB),
        ink = Color(0xFF161A16), muted = Color(0xFF545C53),
        primary = Color(0xFF1F8F7E), onPrimary = Color(0xFFFFFFFF),
        accent = Color(0xFF161A16), onAccent = Color(0xFFD6EA3C),
    ),
)

data class AccentOption(val label: String, val color: Color, val on: Color)

val Accents = listOf(
    AccentOption("Limonka", Color(0xFFD6EA3C), Color(0xFF141A12)),
    AccentOption("Turkus", Color(0xFF34C3AE), Color(0xFF0F1A1A)),
    AccentOption("Róż neon", Color(0xFFFF5C8A), Color(0xFF1A0F14)),
    AccentOption("Cyjan", Color(0xFF4FE3F0), Color(0xFF0F1A1C)),
    AccentOption("Bursztyn", Color(0xFFF2A93B), Color(0xFF1A140A)),
    AccentOption("Fiolet", Color(0xFFB49CFF), Color(0xFF140F1F)),
)
