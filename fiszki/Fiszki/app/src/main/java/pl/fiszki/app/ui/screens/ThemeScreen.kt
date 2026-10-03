package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import pl.fiszki.app.ui.components.BottomBar
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.CyberToggle
import pl.fiszki.app.ui.components.Hatch
import pl.fiszki.app.ui.components.Headline
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.theme.Accents
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.PaletteId
import pl.fiszki.app.ui.theme.Palettes
import pl.fiszki.app.ui.theme.TextSize
import pl.fiszki.app.ui.theme.ThemeSettings

@Composable
private fun Section(title: String, content: @Composable ColumnScope.() -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        MonoLabel(title, color = Fiszki.t.accent)
        content()
    }
}

/** Zmiany działają od razu w całej aplikacji i są zapisywane (DataStore). */
@Composable
fun ThemeScreen(settings: ThemeSettings, onChange: (ThemeSettings) -> Unit, onTab: (String) -> Unit) {
    val t = Fiszki.t
    Box(Modifier.fillMaxSize()) {
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(start = 20.dp, end = 20.dp, bottom = 110.dp),
            verticalArrangement = Arrangement.spacedBy(22.dp),
        ) {
            Column(Modifier.padding(top = 24.dp, start = 4.dp)) {
                MonoLabel("/SYS/THEME", decorative = true)
                Headline("Wygląd", size = 38)
            }

            Section("> PODGLĄD") {
                Panel(Modifier.fillMaxWidth(), cut = 20.dp, padding = PaddingValues(18.dp)) {
                    Row(
                        Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        MonoLabel("_FRONT // EN", size = 10, decorative = true)
                        Hatch(Modifier.size(44.dp, 12.dp))
                    }
                    Spacer(Modifier.height(8.dp))
                    Headline("reluctant", size = settings.textSize.wordSp)
                    MonoLabel("/rɪˈlʌk.tənt/", color = t.c.primary, size = 13)
                    Spacer(Modifier.height(10.dp))
                    Box(
                        Modifier
                            .fillMaxWidth()
                            .clip(t.shape(12.dp))
                            .background(t.c.primary)
                            .padding(horizontal = 14.dp, vertical = 10.dp)
                    ) {
                        Headline("niechętny, oporny", size = 22, color = t.c.onPrimary)
                    }
                    Spacer(Modifier.height(10.dp))
                    CyberButton("POKAŻ_ODPOWIEDŹ", {}, Modifier.fillMaxWidth(), cut = 10.dp)
                }
            }

            Section("> MOTYW") {
                PaletteId.entries.chunked(2).forEach { rowItems ->
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        rowItems.forEach { id ->
                            val p = Palettes.getValue(id)
                            val sel = settings.palette == id
                            val shape = t.shape(10.dp)
                            Column(
                                Modifier
                                    .weight(1f)
                                    .heightIn(min = 64.dp)
                                    .clip(shape)
                                    .background(t.c.surface)
                                    .border(2.dp, if (sel) t.accent else t.c.line, shape)
                                    .selectable(selected = sel, role = Role.RadioButton) {
                                        onChange(settings.copy(palette = id, accent = null))
                                    }
                                    .padding(12.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                            ) {
                                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                    listOf(p.bg, p.primary, p.accent).forEach { c ->
                                        Box(
                                            Modifier
                                                .size(18.dp)
                                                .background(c)
                                                .border(1.dp, t.c.line)
                                        )
                                    }
                                }
                                MonoLabel(p.name, color = if (sel) t.accent else t.c.ink, size = 12, bold = true)
                            }
                        }
                        if (rowItems.size == 1) Spacer(Modifier.weight(1f))
                    }
                }
            }

            Section("> KOLOR AKCENTU") {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Accents.forEach { a ->
                        val sel = t.accent == a.color
                        Box(
                            Modifier
                                .weight(1f)
                                .height(48.dp)
                                .border(2.dp, if (sel) t.c.ink else Color.Transparent, t.shape(8.dp))
                                .padding(4.dp)
                                .clip(t.shape(6.dp))
                                .background(a.color)
                                .selectable(selected = sel, role = Role.RadioButton) {
                                    onChange(settings.copy(accent = a))
                                }
                                .semantics { contentDescription = a.label }
                        )
                    }
                }
            }

            Section("> KSZTAŁTY I DETALE") {
                Column {
                    CyberToggle("Ścięte narożniki", "CLIP: 45° / ROUND", settings.chamfer) {
                        onChange(settings.copy(chamfer = it))
                    }
                    CyberToggle("Kreskowanie", "STRIPES // -45°", settings.hatch) {
                        onChange(settings.copy(hatch = it))
                    }
                    CyberToggle("Etykiety terminala", "/PROC/SYS, _FRONT", settings.deco) {
                        onChange(settings.copy(deco = it))
                    }
                }
            }

            Section("> ROZMIAR TEKSTU FISZKI") {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    TextSize.entries.forEach { s ->
                        val sel = settings.textSize == s
                        Box(
                            Modifier
                                .weight(1f)
                                .heightIn(min = 48.dp)
                                .clip(t.shape(8.dp))
                                .background(if (sel) t.c.primary else t.c.raised)
                                .selectable(selected = sel, role = Role.RadioButton) {
                                    onChange(settings.copy(textSize = s))
                                },
                            contentAlignment = Alignment.Center,
                        ) {
                            MonoLabel(s.label, color = if (sel) t.c.onPrimary else t.c.ink, size = 12, bold = true)
                        }
                    }
                }
            }

            CyberButton(
                "RESET_DO_CYBER",
                { onChange(ThemeSettings()) },
                Modifier.fillMaxWidth(),
                bg = t.c.raised,
                fg = t.c.ink,
            )
        }
        BottomBar("theme", onTab, Modifier.align(Alignment.BottomCenter))
    }
}
