package pl.fiszki.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.Fonts
import kotlin.math.roundToInt

/** Etykieta w stylu terminala. decorative = chowana, gdy wyłączone „Etykiety terminala”. */
@Composable
fun MonoLabel(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Fiszki.t.c.muted,
    size: Int = 11,
    bold: Boolean = false,
    decorative: Boolean = false,
) {
    if (decorative && !Fiszki.t.settings.deco) return
    Text(
        text, modifier,
        color = color,
        fontFamily = Fonts.Mono,
        fontSize = size.sp,
        letterSpacing = 1.sp,
        fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal,
    )
}

/** Nagłówek: wąski, gruby, wersaliki. */
@Composable
fun Headline(text: String, modifier: Modifier = Modifier, size: Int = 34, color: Color = Fiszki.t.c.ink) {
    Text(
        text.uppercase(), modifier,
        color = color,
        fontFamily = Fonts.Display,
        fontWeight = FontWeight.Bold,
        fontSize = size.sp,
        lineHeight = (size + 2).sp,
        letterSpacing = 0.5.sp,
    )
}

/** Panel ze ściętymi narożnikami. Bez fill = obrys 1 dp w kolorze linii. */
@Composable
fun Panel(
    modifier: Modifier = Modifier,
    cut: Dp = 12.dp,
    fill: Color? = null,
    padding: PaddingValues = PaddingValues(16.dp),
    onClick: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit,
) {
    val t = Fiszki.t
    val shape = t.shape(cut)
    var m = modifier.clip(shape).background(fill ?: t.c.surface, shape)
    if (fill == null) m = m.border(1.dp, t.c.line, shape)
    if (onClick != null) m = m.clickable(role = Role.Button, onClick = onClick)
    Column(m.padding(padding), content = content)
}

@Composable
fun CyberButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    bg: Color = Fiszki.t.accent,
    fg: Color = Fiszki.t.onAccent,
    enabled: Boolean = true,
    cut: Dp = 12.dp,
) {
    val shape = Fiszki.t.shape(cut)
    Box(
        modifier
            .heightIn(min = 56.dp)
            .clip(shape)
            .background(if (enabled) bg else bg.copy(alpha = 0.35f))
            .clickable(enabled = enabled, role = Role.Button, onClick = onClick)
            .padding(horizontal = 18.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text,
            color = if (enabled) fg else fg.copy(alpha = 0.6f),
            fontFamily = Fonts.Mono,
            fontWeight = FontWeight.Bold,
            fontSize = 13.sp,
            letterSpacing = 1.5.sp,
        )
    }
}

/** Ukośne kreskowanie -45° jak na okładce. */
@Composable
fun Hatch(modifier: Modifier = Modifier, color: Color = Fiszki.t.accent) {
    if (!Fiszki.t.settings.hatch) return
    Canvas(modifier.clipToBounds()) {
        val step = 7.dp.toPx()
        val stroke = 3.dp.toPx()
        var x = -size.height
        while (x < size.width) {
            drawLine(color, Offset(x, size.height), Offset(x + size.height, 0f), stroke)
            x += step
        }
    }
}

/** Pasek postępu z segmentów. */
@Composable
fun SegmentBar(progress: Float, on: Color, modifier: Modifier = Modifier, segments: Int = 10) {
    val filled = (progress.coerceIn(0f, 1f) * segments).roundToInt()
    Row(modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
        repeat(segments) { i ->
            Box(
                Modifier
                    .weight(1f)
                    .height(8.dp)
                    .background(if (i < filled) on else on.copy(alpha = 0.25f))
            )
        }
    }
}

@Composable
fun TopBar(
    title: String,
    sub: String,
    onBack: () -> Unit,
    backLabel: String = "Wróć",
    trailing: String? = null,
) {
    val t = Fiszki.t
    val ink = t.c.ink
    Row(
        Modifier
            .fillMaxWidth()
            .padding(start = 6.dp, end = 20.dp, top = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(48.dp)
                .clickable(role = Role.Button, onClick = onBack)
                .semantics { contentDescription = backLabel },
            contentAlignment = Alignment.Center,
        ) {
            Canvas(Modifier.size(20.dp)) {
                val w = size.width
                val s = 2.2.dp.toPx()
                drawLine(ink, Offset(w * 0.68f, w * 0.12f), Offset(w * 0.3f, w * 0.5f), s)
                drawLine(ink, Offset(w * 0.3f, w * 0.5f), Offset(w * 0.68f, w * 0.88f), s)
            }
        }
        Column(Modifier.weight(1f)) {
            MonoLabel(sub, size = 10, decorative = true)
            Headline(title, size = 24)
        }
        if (trailing != null) MonoLabel(trailing, color = t.accent, size = 13, bold = true)
    }
}

@Composable
fun BottomBar(current: String, onTab: (String) -> Unit, modifier: Modifier = Modifier) {
    val t = Fiszki.t
    Column(modifier.fillMaxWidth().background(t.c.bg)) {
        Box(Modifier.fillMaxWidth().height(1.dp).background(t.c.line))
        Row(Modifier.fillMaxWidth().height(72.dp)) {
            listOf("home" to "TALIE", "stats" to "STATY", "theme" to "WYGLĄD").forEach { (route, label) ->
                val sel = route == current
                Column(
                    Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .clickable(role = Role.Tab) { onTab(route) },
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Box(
                        Modifier
                            .width(40.dp)
                            .height(3.dp)
                            .background(if (sel) t.accent else Color.Transparent)
                    )
                    Spacer(Modifier.height(24.dp))
                    MonoLabel(label, color = if (sel) t.accent else t.c.muted, size = 12, bold = sel)
                }
            }
        }
    }
}

@Composable
fun CyberToggle(label: String, hint: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    val t = Fiszki.t
    Row(
        Modifier
            .fillMaxWidth()
            .heightIn(min = 56.dp)
            .toggleable(value = checked, role = Role.Switch, onValueChange = onChange),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(label, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
            MonoLabel(hint, size = 10, decorative = true)
        }
        val track = if (t.settings.chamfer) t.shape(6.dp) else RoundedCornerShape(50)
        Box(
            Modifier
                .size(48.dp, 26.dp)
                .clip(track)
                .background(if (checked) t.accent else t.c.raised)
                .padding(4.dp),
            contentAlignment = if (checked) Alignment.CenterEnd else Alignment.CenterStart,
        ) {
            Box(
                Modifier
                    .size(18.dp)
                    .clip(if (t.settings.chamfer) RectangleShape else CircleShape)
                    .background(if (checked) t.onAccent else t.c.muted)
            )
        }
    }
    Box(Modifier.fillMaxWidth().height(1.dp).background(t.c.line))
}

@Composable
fun CyberField(
    label: String,
    value: String,
    onChange: (String) -> Unit,
    big: Boolean = true,
    minLines: Int = 1,
) {
    val t = Fiszki.t
    var focused by remember { mutableStateOf(false) }
    val shape = t.shape(10.dp)
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        MonoLabel(label, color = t.accent)
        BasicTextField(
            value = value,
            onValueChange = onChange,
            modifier = Modifier
                .fillMaxWidth()
                .clip(shape)
                .background(t.c.surface)
                .border(if (focused) 2.dp else 1.dp, if (focused) t.c.primary else t.c.line, shape)
                .onFocusChanged { focused = it.isFocused }
                .semantics { contentDescription = label.removePrefix("> ") }
                .padding(horizontal = 14.dp, vertical = 14.dp),
            textStyle = TextStyle(
                color = t.c.ink,
                fontFamily = if (big) Fonts.Display else FontFamily.Default,
                fontWeight = if (big) FontWeight.SemiBold else FontWeight.Normal,
                fontSize = if (big) 22.sp else 16.sp,
            ),
            cursorBrush = SolidColor(t.accent),
            singleLine = big,
            minLines = minLines,
        )
    }
}

/** Okno dialogowe w stylu aplikacji (ścięty panel z obrysem). */
@Composable
fun CyberDialog(
    title: String,
    sub: String,
    onDismiss: () -> Unit,
    content: @Composable ColumnScope.() -> Unit,
) {
    Dialog(onDismissRequest = onDismiss) {
        Panel(
            Modifier.fillMaxWidth(),
            cut = 18.dp,
            fill = Fiszki.t.c.bg,
            padding = PaddingValues(20.dp),
        ) {
            MonoLabel(sub, size = 10, decorative = true)
            Headline(title, size = 26)
            Spacer(Modifier.height(16.dp))
            Column(verticalArrangement = Arrangement.spacedBy(16.dp), content = content)
        }
    }
}

/** Pytanie „na pewno?” z przyciskami ANULUJ / [confirm]. */
@Composable
fun ConfirmDialog(
    title: String,
    message: String,
    confirm: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    val t = Fiszki.t
    CyberDialog(title, "SYS://CONFIRM", onDismiss) {
        Text(message, color = t.c.ink, fontSize = 16.sp)
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            CyberButton("ANULUJ", onDismiss, Modifier.weight(1f), bg = t.c.raised, fg = t.c.ink)
            CyberButton(confirm, onConfirm, Modifier.weight(1f))
        }
    }
}

/** Nowa talia / zmiana nazwy: nazwa + krótki kod (np. EN). */
@Composable
fun DeckFormDialog(
    title: String,
    initialName: String,
    initialShort: String,
    confirm: String,
    onConfirm: (name: String, short: String) -> Unit,
    onDismiss: () -> Unit,
) {
    val t = Fiszki.t
    var name by remember { mutableStateOf(initialName) }
    var short by remember { mutableStateOf(initialShort) }
    CyberDialog(title, "DECK.EDIT()", onDismiss) {
        CyberField("> NAZWA", name, { name = it })
        CyberField("> KOD [MAX 4, OPCJONALNIE]", short, { short = it.take(4).uppercase() })
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            CyberButton("ANULUJ", onDismiss, Modifier.weight(1f), bg = t.c.raised, fg = t.c.ink)
            CyberButton(
                confirm,
                onClick = { onConfirm(name.trim(), short.trim()) },
                modifier = Modifier.weight(1f),
                enabled = name.isNotBlank(),
            )
        }
    }
}
