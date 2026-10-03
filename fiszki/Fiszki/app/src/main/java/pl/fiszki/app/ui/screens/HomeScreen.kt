package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import pl.fiszki.app.data.dni
import pl.fiszki.app.data.kart
import pl.fiszki.app.ui.components.BottomBar
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.DeckFormDialog
import pl.fiszki.app.ui.components.Hatch
import pl.fiszki.app.ui.components.Headline
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.components.SegmentBar
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.Fonts
import pl.fiszki.app.ui.viewmodel.HomeViewModel

@Composable
fun HomeScreen(
    vm: HomeViewModel,
    onStudy: (Long) -> Unit,
    onOpenDeck: (Long) -> Unit,
    onAdd: () -> Unit,
    onTab: (String) -> Unit,
) {
    val t = Fiszki.t
    val ui by vm.ui.collectAsStateWithLifecycle()
    val dueAll = ui.dueAll
    val done = ui.doneToday
    val progress = if (done + dueAll == 0) 1f else done.toFloat() / (done + dueAll)
    var newDeck by remember { mutableStateOf(false) }

    Box(Modifier.fillMaxSize()) {
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 170.dp)
        ) {
            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(start = 24.dp, end = 20.dp, top = 24.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top,
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    MonoLabel("SYS://FISZKI_v0.1", decorative = true)
                    Headline("Twoje fiszki", size = 38)
                }
                Column(
                    Modifier
                        .clip(t.shape(12.dp))
                        .background(t.accent)
                        .padding(horizontal = 14.dp, vertical = 8.dp),
                    horizontalAlignment = Alignment.End,
                ) {
                    MonoLabel("STREAK", color = t.onAccent, size = 9, bold = true)
                    Headline(dni(ui.streak), size = 24, color = t.onAccent)
                }
            }

            // Kolejka na dziś
            Column(
                Modifier
                    .padding(20.dp)
                    .fillMaxWidth()
                    .clip(t.shape(22.dp))
                    .background(t.c.primary)
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    MonoLabel("_QUEUE.TODAY", color = t.c.onPrimary, bold = true)
                    MonoLabel("[$done/${done + dueAll}]", color = t.c.onPrimary, bold = true)
                }
                Headline(kart(dueAll), size = 56, color = t.c.onPrimary)
                SegmentBar(progress, t.c.onPrimary)
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CyberButton(
                        "▶ START_SESJI",
                        onClick = { onStudy(-1L) },
                        bg = t.c.onPrimary,
                        fg = t.accent,
                        enabled = dueAll > 0,
                        cut = 10.dp,
                    )
                    Hatch(Modifier.size(64.dp, 22.dp), color = t.c.onPrimary)
                }
            }

            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(start = 24.dp, end = 20.dp, top = 4.dp, bottom = 10.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom,
            ) {
                Column {
                    MonoLabel("/DECKS [%02d]".format(ui.decks.size), decorative = true)
                    Headline("Talie", size = 24)
                }
                CyberButton(
                    "+ NOWA_TALIA",
                    onClick = { newDeck = true },
                    bg = t.c.raised,
                    fg = t.c.ink,
                    cut = 8.dp,
                )
            }

            Column(
                Modifier.padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (ui.loaded && ui.decks.isEmpty()) {
                    Panel(Modifier.fillMaxWidth()) {
                        MonoLabel("_EMPTY", color = t.c.primary, bold = true)
                        Text("Nie masz jeszcze żadnej talii. Utwórz pierwszą przyciskiem + NOWA_TALIA.", fontSize = 15.sp)
                    }
                }
                ui.decks.forEach { (d, total, due) ->
                    Panel(
                        Modifier.fillMaxWidth(),
                        padding = PaddingValues(horizontal = 14.dp, vertical = 12.dp),
                        onClick = { onOpenDeck(d.id) },
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            MonoLabel("[${d.short}]", Modifier.width(56.dp), color = t.c.primary, size = 12, bold = true)
                            Column(Modifier.weight(1f)) {
                                Text(
                                    d.name.uppercase(),
                                    fontFamily = Fonts.Display,
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 19.sp,
                                )
                                MonoLabel("${kart(total).uppercase()} // ${d.path}")
                            }
                            Box(
                                Modifier
                                    .background(t.accent)
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                MonoLabel("$due", color = t.onAccent, size = 13, bold = true)
                            }
                        }
                    }
                }
            }
        }

        // FAB: nowa fiszka
        Box(
            Modifier
                .align(Alignment.BottomEnd)
                .padding(end = 20.dp, bottom = 96.dp)
                .size(58.dp)
                .clip(t.shape(14.dp))
                .background(t.accent)
                .clickable(role = Role.Button, onClick = onAdd)
                .semantics { contentDescription = "Dodaj fiszkę" },
            contentAlignment = Alignment.Center,
        ) {
            Text("+", color = t.onAccent, fontSize = 30.sp, fontWeight = FontWeight.Bold)
        }

        BottomBar("home", onTab, Modifier.align(Alignment.BottomCenter))
    }

    if (newDeck) {
        DeckFormDialog(
            title = "Nowa talia",
            initialName = "",
            initialShort = "",
            confirm = "UTWÓRZ",
            onConfirm = { name, short ->
                vm.addDeck(name, short)
                newDeck = false
            },
            onDismiss = { newDeck = false },
        )
    }
}
